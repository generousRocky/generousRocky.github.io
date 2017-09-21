---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-08-20 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "Kernel Code Analysis - Read path"
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



# pblk: Physical Block Device Target

<p style="text-align: center;">
	<img src="{{ site.url }}/images/openChannelSSD_code.png" alt="Drawing" style="width: 600;"/>
</p>

pblk implements a fully associative, host-based FTL that exposes a traditional block I/O interface. Its primary responsibilities are:

- Map logical addresses onto physical addresses (4KB granularity) in a logical-to-physical (L2P) table.
- Maintain the integrity and consistency of the L2P table as well as its recovery from normal tear down and power outage.
- Deal with controller- and media-specific constrains.
- Handle I/O errors.
- Implement garbage collection.
- Maintain consistency across the I/O stack during synchronization points.

For more information please refer to: <http://lightnvm.io>

## Source Code Overview

LightNVM와 관련된 중요한 기능의 대부분은 커널 소스코드의 /driver/lightnvm/에 구현되어 있으며 각 file별 주요 구현 내용은 다음과 같다.

nvme block device의 creation과 같은 core.c 파일에 구현되어 있다. 그 중 write buffering, address mapping, garbage collection과 같은 기존의 FTL에서 수행하고 있던 기능들은 pblk-* file에 구현되어 있다.

* _pblk.h_ - Implementation of a Physical Block-device target for Open-channel SSDs.
* rrpc.h, rrpc.c - Implementation of a Round-robin page-based Hybrid FTL for Open-channel SSDs.
* _pblk-cache.c_ - pblk's write cache
* _pblk-core.c_ - pblk's core functionality
* _pblk-gc.c_ - pblk's garbage collector
* _pblk-init.c_ - pblk's initialization.
* _pblk-map.c_ - pblk's lba-ppa mapping strategy
* _pblk-rb.c_ - pblk's write buffer
* _pblk-read.c_ - pblk's read path
* _pblk-recovery.c_ - pblk's recovery path
* _pblk-rl.c_ - pblk's rate limiter for user I/O
* _pblk-sysfs.c_ - pblk's sysfs
* _pblk-write.c_ - pblk's write path from write buffer to media

## Overview of read path (This is a work in progress.)

<p style="text-align: center;">
	<img src="{{ site.url }}/images/openChannelSSD_code_01.png" alt="Drawing" style="width: 600;"/>
</p>

```c
static const struct file_operations _ctl_fops = {
	.open = nonseekable_open,
	.unlocked_ioctl = nvm_ctl_ioctl,
	.owner = THIS_MODULE,
	.llseek  = noop_llseek,
};
```
fs 레벨에서 ioctl(unlock_ioctl, i/o 컨트롤 시스템 콜)을 호출하면, 다음과 같이 driver/lightnvm/core.c 의 자료구조에 operation이 매핑된다.


```c
static int nvm_create_tgt(struct nvm_dev *dev, struct nvm_ioctl_create *create){

  .
  .
  blk_queue_make_request(tqueue, tt->make_rq);
  .
  .
}
```
nvm_create_tgt 함수 내에서 make_rq 함수 포인터를 매개변수로 전달한다.


```c
static struct nvm_tgt_type tt_pblk = {

  .name   = "pblk",
  .version  = {1, 0, 0},
  .make_rq  = pblk_make_rq,
          .
          .
          .
}
```
make_rq는 다음과 같이 /driver/lightnvm/pblk-init.c 파일에 다음과 같은 자료구조로 매핑되어 있다.

```c
static blk_qc_t pblk_make_rq(struct request_queue *q, struct bio *bio)
{

          .
          .
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
pblk_make_rq함수는 pblk_rw_io함수를 호출


```c
static int pblk_rw_io(struct request_queue *q, struct pblk *pblk, struct bio *bio){

  if (bio_data_dir(bio) == READ) {
    . . .
    ret = pblk_submit_read(pblk, bio);
    . . .
    return ret;
  }

  //else -> write
    .
    .
}
```
pblk_rw_io에서 read i/o일 경우 pblk_submit_read함수 호출


```c
int pblk_submit_read(struct pblk *pblk, struct bio *bio){
  . . .
}
```

* 파라미터로 pblk 구조체 포인터와 bio 구조체 포인터가 전달된다. bio 구조체로부터 logical block address 얻는다.(_pblk_get_lba(bio)_)

* _read_bitmap_ 변수에 최대 64개 까지의 read request에 대한 ppa가 저장된다.(_pblk_read_rq_ 함수 또는 _pblk_read_ppalist_rq_ 함수를 통해서).

* nvm_rq 구조체 변수인 rqd에 구조체 멤버변수들이 할당됨.

* io를 위한 메모리 영역을 할당 해 준다.(dma)

* r_seq 값에 따라, _pblk_read_rq_(<= 1), _pblk_read_ppalist_rq_(>1) 함수가 호출된다.

* _pblk_read_rq_, _pblk_read_ppalist_rq_ 에서는 l2p 를 lookup 할때, pblk_lookup_l2p_seq()함수를 호출한다.

* 섹터 크기가 1보다 클 경우(_pblk_read_ppalist_rq_),

* 섹터 크기가 1보자 작을 경우(_pblk_read_rq_), ppa가 cache에 있는지 확인 후 있으면, 캐시에서, 없으면, pblk_lookup_l2p_seq()함수를 호출한다.

* 이후 io처리 시, bitmap 이 full 일 경우 io를 종료한다. 모든 sector가 device로 부터 읽기를 수행해야 하면, _pblk_submit_read_io_ 함수를 호출한다.

* read bio request가 부분적으로 write buffer에 의해 체워져 있을 수 있다. 즉, 디바이스로 부터 읽어들어져야 할 holes이 있으면, _pblk_fill_partial_read_bio_ 함수를 호출한다.



```c
static int pblk_submit_read_io(struct pblk *pblk, struct nvm_rq *rqd)
```
수행하는 기능 없음, just pass the parameter to _pblk_submit_io(**pblk**, rqd)_


```c
int pblk_submit_io(struct pblk *pblk, struct nvm_rq *rqd)
```
rqd->nr_ppas 만큼 bad ppa 검사, 이때 spin lock으로 synchronization구현.

_nvm_submit_io(**dev**, rqd)_ 함수를 호출한다.


```c
int nvm_submit_io(struct nvm_tgt_dev *tgt_dev, struct nvm_rq *rqd)
```
_submit_io(**pblk**, rqd)_ 함수 호출.


```c
static struct nvm_dev_ops nvme_nvm_dev_ops = {
      .
      .
  .submit_io    = nvme_nvm_submit_io,
      .
      .
};
```
위와 같이 submit_io는 nvme_nvm_submit_io 함수 포인터로 매핑되어 있다.

```c
static int nvme_nvm_submit_io(struct nvm_dev *dev, struct nvm_rq *rqd)
```
* io command 를 만들고(_kzalloc()_ 함수), rq에 request를 할당 해 준다. (_nvme_alloc_request_ 함수)
* _blk_excute_rq_nowwait()_ 함수를 호출하여 인자로 rq전달.


```c
void blk_execute_rq_nowait(struct request_queue *q, struct gendisk *bd_disk, struct request *rq, int at_head, rq_end_io_fn *done)
```


```c
void __blk_run_queue(struct request_queue *q)
```

```c
inline void __blk_run_queue_uncond(struct request_queue *q)
```
inset a request into queue for execution
Function Description: Insert a fully prepared request at the back of the I/O scheduler queue. This function will invoke "done" directly if the queue is dead.


   .
   .
   .
