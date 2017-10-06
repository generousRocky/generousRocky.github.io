---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-09-09 11:00:00
author: Rocky Lim
categories: research
excerpt: "Kernel Code Analysis - Write path"
image:
  feature:
  teaser: openChannelSSD.png
  path: images/openChannelSSD.png
comments: true
locale: "vn"
share: true
ads: true
---


<p style="text-align: center;">
	<img src="{{ site.url }}/images/openChannelSSD.png" alt="Drawing" style="width: 600;"/>
</p>

관련 논문:  <a href="/publication/fast17-bjorling.pdf">"LightNVM: The Linux Open-Channel SSD Subsystem"</a>


## Overview of write flow (This is a work in progress.)

```c
/* physical block device target */
static struct nvm_tgt_type tt_pblk = {
  .name   = "pblk",
  .version  = {1, 0, 0},

  .make_rq  = pblk_make_rq,
  .capacity = pblk_capacity,

  .init   = pblk_init,
  .exit   = pblk_exit,

  .sysfs_init = pblk_sysfs_init,
  .sysfs_exit = pblk_sysfs_exit,
};
```
위와 같이 pblk_make_rq와 pblk_init 이 nvm_tgt_type에 매핑되어 있다.

```c
static void *pblk_init(struct nvm_tgt_dev *dev, struct gendisk *tdisk, int flags){

  .
  .
  ret = pblk_writer_init(pblk);
}
```

```c
static int pblk_writer_init(struct pblk *pblk)
{
  setup_timer(&pblk->wtimer, pblk_write_timer_fn, (unsigned long)pblk);
  mod_timer(&pblk->wtimer, jiffies + msecs_to_jiffies(100));

  pblk->writer_ts = kthread_create(pblk_write_ts, pblk, "pblk-writer-t");
  if (IS_ERR(pblk->writer_ts)) {
    pr_err("pblk: could not allocate writer kthread\n");
    return PTR_ERR(pblk->writer_ts);
  }

  return 0;
}
```
pblk initialization을 진행 할 떄, write를 위한 thread를 생성, 초기화 시켜준다.
pblk->write_ts 변수에 write thread에 대한 task_struct 정보가 저장된다.


```c
int pblk_write_ts(void *data)
{
  struct pblk *pblk = data;

  while (!kthread_should_stop()) {
    if (!pblk_submit_write(pblk))
      continue;
    set_current_state(TASK_INTERRUPTIBLE);
    io_schedule();
  }

  return 0;
}
```
write 쓰레드 생성시 호출되는 시작되는 함수는 위와 같다. **_kthread_should_stop_** 함수와 **_pblk_submit_write()_** 함수를 반복적으로 호출하면서 wirte i/o를 수행한다.



```c
static int pblk_rw_io(struct request_queue *q, struct pblk *pblk, struct bio *bio){

  if(read 일 경우){
    ret = pblk_submit_read(pblk, bio);
      .
      .
    return ret;
  }

  // write 일 경우
  return pblk_write_to_cache(pblk, bio, PBLK_IOTYPE_USER);
}
```

```c
int pblk_write_to_cache(struct pblk *pblk, struct bio *bio, unsigned long flags)
{
  struct pblk_w_ctx w_ctx;
  sector_t lba = pblk_get_lba(bio);
  unsigned int bpos, pos;
  int nr_entries = pblk_get_secs(bio);
  int i, ret;

  /* Update the write buffer head (mem) with the entries that we can
   * write. The write in itself cannot fail, so there is no need to
   * rollback from here on.
   */
retry:
  ret = pblk_rb_may_write_user(&pblk->rwb, bio, nr_entries, &bpos);
  switch (ret) {
  case NVM_IO_REQUEUE:
    io_schedule();
    goto retry;
  case NVM_IO_ERR:
    pblk_pipeline_stop(pblk);
    goto out;
  }

  pblk_ppa_set_empty(&w_ctx.ppa);
  w_ctx.flags = flags;
  if (bio->bi_opf & REQ_PREFLUSH)
    w_ctx.flags |= PBLK_FLUSH_ENTRY;

  for (i = 0; i < nr_entries; i++) {
    void *data = bio_data(bio);

    w_ctx.lba = lba + i;

    pos = pblk_rb_wrap_pos(&pblk->rwb, bpos + i);
    pblk_rb_write_entry_user(&pblk->rwb, data, w_ctx, pos);

    bio_advance(bio, PBLK_EXPOSED_PAGE_SIZE);
  }

#ifdef CONFIG_NVM_DEBUG
  atomic_long_add(nr_entries, &pblk->inflight_writes);
  atomic_long_add(nr_entries, &pblk->req_writes);
#endif

  pblk_rl_inserted(&pblk->rl, nr_entries);

out:
  pblk_write_should_kick(pblk);
  return ret;
}
```

**pblk_rb_may_write_user**:<br />
Atomically check that (i) there is space on the write buffer for the incoming I/O, and (ii) the current I/O type has enough budget in the write buffer (rate-limiter).

write buffer의 크기는 몇 일까?


**pblk_rb_write_entry_user**:<br />
Write @nr_entries to ring buffer from @data buffer if there is enough space. Typically, 4KB data chunks coming from a bio will be copied to the ring buffer, thus the write will fail if not all incoming data can be copied.

ring buffer 의 크기가 일반저긍로 4kb인가보다.

**pblk_write_should_kick(struct pblk *pblk)**:<br />
pblk_write_kick(pblk) 함수 호출

```c
static void pblk_write_kick(struct pblk *pblk)
{
  wake_up_process(pblk->writer_ts);
  mod_timer(&pblk->wtimer, jiffies + msecs_to_jiffies(1000));
}
```
wake_up_process(kernel/sched/core.c) 함수 : Attempt to wake up the nominated process and move it to the set of runnable processes.


```c
int pblk_write_ts(void *data)
{
  struct pblk *pblk = data;

  while (!kthread_should_stop()) {
    if (!pblk_submit_write(pblk))
      continue;
    set_current_state(TASK_INTERRUPTIBLE);
    io_schedule();
  }

  return 0;
}
```
write request가 있을 때다 위와 같이 pblk_write_ts 쓰레드가 진행된다.

```c
static int pblk_submit_write(struct pblk *pblk){
		.
		.
		// rqd 에 write request 만큼의 메모리 할당, 0 초기화
		rqd = pblk_alloc_rqd(pblk, WRITE);
		.
		.
		// bio forming
		pblk_rb_read_to_bio(&pblk->rwb, rqd, bio, pos, secs_to_sync,secs_avail);
		.
		.
		.
		// i/o submit
		pblk_submit_io_set(pblk,rqd);
		.
		.
}
```
**_pblk_rb_read_to_bio()_**:<br />
ring buffer에서 available한 엔트리 들을 읽어서 bio에 추가 해 준다. 즉 bio을 forming하는 함수.


**_pblk_submit_io_set_**
```c
static int pblk_submit_io_set(struct pblk *pblk, struct nvm_rq *rqd){
		
		.
		.
		err = pblk_setup_w_rq(pblk, rqd, c_ctx, &erase_ppa);
		.
		.
		.


}
```


```c
static int pblk_setup_w_rq(struct pblk *pblk, struct nvm_rq *rqd, struct pblk_c_ctx *c_ctx, struct ppa_addr *erase_ppa){

		.
		.
		ret = pblk_alloc_w_rq(pblk, rqd, nr_secs, pblk_end_io_write);
		.
		.
		if (likely(!e_line || !atomic_read(&e_line->left_eblks)))
				pblk_map_rq(pblk, rqd, c_ctx->sentry, lun_bitmap, valid, 0);
		else
				pblk_map_erase_rq(pblk, rqd, c_ctx->sentry, lun_bitmap, valid, erase_ppa);

		.
		.
}

```


rqd structure 생성, structure 체워나가기. bio -> rqd 





























