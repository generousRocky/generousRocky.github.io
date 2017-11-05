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


## Initialization of write thread (This is a work in progress.)

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
위와 같이 make_rq함수와 init함수가 각각 pblk_make_rq와 pblk_init에 매핑되어 있다.


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
생성된 thread는 **_pblk_write_ts_**함수를 수행한다.


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
write 쓰레드 생성시 호출되는 시작되는 함수는 위와 같다. io 스케줄러에 의해
**_kthread_should_stop_** 함수와 **_pblk_submit_write()_** 함수를 반복적으로 호출하면서 wirte를 진행한다.


## write path

---
파일시스템으로부터의 write는 make_rq와 매핑된. pblk_make_rq함수에 의해 수행된다.
```c
static blk_qc_t pblk_make_rq(struct request_queue *q, struct bio *bio)
{
  struct pblk *pblk = q->queuedata;

  if (bio_op(bio) == REQ_OP_DISCARD) {
    pblk_discard(pblk, bio);
    if (!(bio->bi_opf & REQ_PREFLUSH)) {
      bio_endio(bio);
      return BLK_QC_T_NONE;
    }
  }

  switch (pblk_rw_io(q, pblk, bio)) {
  case NVM_IO_ERR:
    bio_io_error(bio);
    break;
  case NVM_IO_DONE:
    bio_endio(bio);
    break;
  }

  return BLK_QC_T_NONE;
}
```
---
pblk함수에서 read path와 write path가 분리되어 처리된다.
reaa request는 pblk_submit_io함수, 그리고 wirte는 pblk_write_to_cache함수를 통해 i/o path가 이어서 진행된다.
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
---
write buffer에 데이터를 체워 넣고, write context를 저장한다. 일반적으로 bio로부터 4kb의 데이터 chunk가 ring buffer에 copy된다.

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

logical block address to physical page address mapping table을 업데이트 해 준다.(pblk_trans_map_update 함수)

pblk_rb_write_entry_user -> pblk_update_map_cache -> pblk_update_map -> pblk_trans_map_set

```c
void pblk_update_map(struct pblk *pblk, sector_t lba, struct ppa_addr ppa)
{
  struct ppa_addr ppa_l2p;

  /* logic error: lba out-of-bounds. Ignore update */
  if (!(lba < pblk->rl.nr_secs)) {
    WARN(1, "pblk: corrupted L2P map request\n");
    return;
  }

  spin_lock(&pblk->trans_lock);
  ppa_l2p = pblk_trans_map_get(pblk, lba);

  if (!pblk_addr_in_cache(ppa_l2p) && !pblk_ppa_empty(ppa_l2p))
   pblk_map_invalidate(pblk, ppa_l2p);

  pblk_trans_map_set(pblk, lba, ppa);
  spin_unlock(&pblk->trans_lock);
}
```

```c

static inline void pblk_trans_map_set(struct pblk *pblk, sector_t lba,
            struct ppa_addr ppa)
{
  if (pblk->ppaf_bitsize < 32) {
    u32 *map = (u32 *)pblk->trans_map;

    map[lba] = pblk_ppa64_to_ppa32(pblk, ppa);
  } else {
    u64 *map = (u64 *)pblk->trans_map;

    map[lba] = ppa.ppa;
  }
}
```


---







```c
void pblk_write_should_kick(struct pblk *pblk)
{
  unsigned int secs_avail = pblk_rb_read_count(&pblk->rwb);

  if (secs_avail >= pblk->min_write_pgs)
    pblk_write_kick(pblk);
}
```
---
```c
static void pblk_write_kick(struct pblk *pblk)
{
  wake_up_process(pblk->writer_ts);
  mod_timer(&pblk->wtimer, jiffies + msecs_to_jiffies(1000));
}
 ```
wake_up_process(kernel/sched/core.c) 함수 : Attempt to wake up the nominated process and move it to the set of runnable processes.

---
wake_up_process함수에 의해 pblk_submit_write 함수가 호출된다.
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
---

```c
static int pblk_submit_write(struct pblk *pblk){
		.
		.
		// bio forming
		pblk_rb_read_to_bio(&pblk->rwb, rqd, bio, pos, secs_to_sync,secs_avail);
		.
		.
		// i/o submit
		pblk_submit_io_set(pblk,rqd);
}
```

**_pblk_rb_read_to_bio()_**:<br />
ring buffer에서 available한 엔트리 들을 읽어서 bio에 추가 해 준다. 즉 write bio을 forming하는 함수.

To avoid a memory copy, a page reference to the write buffer is used to be added to the bio.
This function is used by the **write thread** to form the write bio that will persist data on the write buffer to the media.

---
```c
static int pblk_submit_io_set(struct pblk *pblk, struct nvm_rq *rqd){
		
		.
		.
		/* Assign lbas to ppas and populate request structure */
		err = pblk_setup_w_rq(pblk, rqd, c_ctx, &erase_ppa);
		.
		.
		/* Submit metadata write for previous data line */
		err = pblk_sched_meta_io(pblk, rqd->ppa_list, rqd->nr_ppas);.
		err = pblk_submit_io(pblk, rqd);
		
		OR
		
		/* Submit data write for current data line */
		err = pblk_submit_io(pblk, rqd);
}
```
---
write request setup, logical address를 physical address로 변환,

```c
static int pblk_setup_w_rq(struct pblk *pblk, struct nvm_rq *rqd, struct pblk_c_ctx *c_ctx, struct ppa_addr *erase_ppa){

		.
		.
		// Setup write request = rqd structure 체우기
		ret = pblk_alloc_w_rq(pblk, rqd, nr_secs, pblk_end_io_write);
		.
		.
		//
		if (likely(!e_line || !atomic_read(&e_line->left_eblks)))
				pblk_map_rq(pblk, rqd, c_ctx->sentry, lun_bitmap, valid, 0);
		else
				pblk_map_erase_rq(pblk, rqd, c_ctx->sentry, lun_bitmap, valid, erase_ppa);

		.
		.
}

```
**_pblk_alloc_w_rq_**:<br />
assign lbas to ppas and pipulate request structure. 
rqd structure 생성, structure 체워나가기. 


**_pblk_map_rq()_** 또는 **_pblk_map_erase_rq()_**:<br />:
 the write buffer is protected by the sync backpointer, and a single writer thread have access to each specific entry at a time. Thus, it is safe to modify the context for the entry we are setting up for submission without taking any lock or memory barrier.


위 두 함수를 통해 통해 physical address를 만들어 낸다. [address space 사진 넣기]

---
```c
int pblk_submit_io(struct pblk *pblk, struct nvm_rq *rqd)
{
		.
		.
		return nvm_sumbit_io(dev, rad);
}
```

---
```c
int nvm_submit_io(struct nvm_tgt_dev *tgt_dev, struct nvm_rq *rqd)
{
		.
		.
		ret = dev->ops->submit_io(dev, rqd);
		if(ret)
				nvm_rq_dev_to_tgt(tgt_dev_rqd);

		return ret;
}

```
---
submit_io는 nvme_nvm_submit_io로 매핑되어 있다.


```c
static int nvme_nvm_submit_io(struct nvm_dev *dev, struct nvm_rq *rqd)
{
		.
		.
		blk_execute_rq_nowait(q, NULL, rq, 0, nvme_nvm_end_io);

}
```
---
request queue에 I/O를 집어넣는다. 비 동기적으로 실행된다. request queue access시 spin lock.
```c
/**
* blk_execute_rq_nowait - insert a request into queue for execution
* @q:    queue to insert the request in
* @bd_disk:  matching gendisk
* @rq:   request to insert
* @at_head:    insert request at head or tail of queue
* @done: I/O completion handler
*
* Description:
*    Insert a fully prepared request at the back of the I/O scheduler queue
*    for execution.  Don't wait for completion.
*
* Note:
*    This function will invoke @done directly if the queue is dead.
*/
void blk_execute_rq_nowait(struct request_queue *q, struct gendisk *bd_disk, struct request *rq, int at_head, rq_end_io_fn *done)
{
		int where = at_head ? ELEVATOR_INSERT_FRONT : ELEVATOR_INSERT_BACK;

		WARN_ON(irqs_disabled());
		WARN_ON(!blk_rq_is_passthrough(rq));

		rq->rq_disk = bd_disk;
		rq->end_io = done;

		/*
		* don't check dying flag for MQ because the request won't
		* be reused after dying flag is set
		*/
		if (q->mq_ops) {
				blk_mq_sched_insert_request(rq, at_head, true, false, false);
				return;
		}
		spin_lock_irq(q->queue_lock);

		if (unlikely(blk_queue_dying(q))) {
				rq->rq_flags |= RQF_QUIET;
				__blk_end_request_all(rq, BLK_STS_IOERR);
				spin_unlock_irq(q->queue_lock);
				return;
		}

		__elv_add_request(q, rq, where);
		__blk_run_queue(q);
		spin_unlock_irq(q->queue_lock);
}
```
---

```c
void __blk_run_queue(struct request_queue *q)
{
		lockdep_assert_held(q->queue_lock);
		 WARN_ON_ONCE(q->mq_ops);

		if (unlikely(blk_queue_stopped(q)))
		return;

		__blk_run_queue_uncond(q);
}
```
---
구현되어 있는 request_fn을 invoke한다. 여러 쓰레드가 이 request function을 concurrent하게 수행할 수 있음. -> lock 필요.
```c
/**
* __blk_run_queue_uncond - run a queue whether or not it has been stopped
* @q:  The queue to run
*
* Description:
*    Invoke request handling on a queue if there are any pending requests.
*    May be used to restart request handling after a request has completed.
*    This variant runs the queue whether or not the queue has been
*    stopped. Must be called with the queue lock held and interrupts
*    disabled. See also @blk_run_queue.
*/
inline void __blk_run_queue_uncond(struct request_queue *q)
{
		lockdep_assert_held(q->queue_lock);
		WARN_ON_ONCE(q->mq_ops);
		if (unlikely(blk_queue_dead(q)))
				return;
		/*
		* Some request_fn implementations, e.g. scsi_request_fn(), unlock
		* the queue lock internally. As a result multiple threads may be
		* running such a request function concurrently. Keep track of the
		* number of active request_fn invocations such that blk_drain_queue()
		* can wait until all these request_fn calls have finished.
		*/
		q->request_fn_active++;
		q->request_fn(q);
		q->request_fn_active--;
}
```





















