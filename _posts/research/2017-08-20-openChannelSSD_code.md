---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-08-20 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "Kernel Code Analysis - Based on the functional elements of pblk"
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

{% include toc.html %}

# pblk: Physical Block Device Target

<p style="text-align: center;">
	<img src="{{ site.url }}/images/openChannelSSD_code.png" alt="Drawing" style="width: 600;"/>
</p>

pblk implements a fully associative, host-based FTL that exposes a traditional
block I/O interface. Its primary responsibilities are:

  - Map logical addresses onto physical addresses (4KB granularity) in a
    logical-to-physical (L2P) table.
  - Maintain the integrity and consistency of the L2P table as well as its
    recovery from normal tear down and power outage.
  - Deal with controller- and media-specific constrains.
  - Handle I/O errors.
  - Implement garbage collection.
  - Maintain consistency across the I/O stack during synchronization points.

For more information please refer to: <http://lightnvm.io>

## Source Code Overview

LightNVM와 관련된 중요한 기능의 대부분은 커널 소스코드의 /driver/lightnvm/에 구현되어 있으며 각 file별 주요 구현 내용은 다음과 같다.

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

## Overview of read flow (This is a work in progress.)

* _pblk_make_rq(pblk-init.c)_

* _pblk_rw_io(pblk-init.c)_

* _pblk_submit_read(pblk-read.c)_

_read_bitmap_ 변수에 최대 64개 까지의 read request에 대한 ppa가 저장된다. (_pblk_read_rq_ 함수 또는 _pblk_read_ppalist_rq_ 함수를 통해서).

이후 _pblk_submit_read_io_ 함수를 호출한다. 만약 write buffer가 다 차있지 않은 상태, 즉 모든 비트맵이 다 차있는 경우가 아닐 때 에는, _pblk_fill_partial_read_bio_함수를 호출한다.

* (_pblk_fill_partial_read_bio_)

* _pblk_submit_read_io(pblk-read.c)_

_rqd->flags = pblk_set_read_mode(pblk);_ 코드를 통해 read mode로 설정 해 주고, _pblk_submit_io_함수를 호출한다.

* _pblk_submit_io(pblk-core.c)_

_nvm_submit_io_함수 호출한다. DEBUG MODE configuration시 addtional code 있음(spin lock포함). nvm_submit_io_함수 호출.

* _nvm_submit_io_

## Overview of write flow (This is a work in progress.)

_pblk_setup_w_rq_ 함수(_pblk-write.c_) 에서 _pblk_map_rq_ 함수(_pblk-map.c_)를  호출하거나 _pblk_map_erase_rq_ 함수(_pblk-map.c_) 를 호출한다.

_pblk_map_erase_rq_ 함수는 _pblk_map_rq_ 함수를 호출하고, _pblk_map_rq_ 함수는 _pblk_map_page_data_ 함수를 호출하게 된다.


| name | call     |
| :-------------: | :-------------: |
| _pblk_setup_w_rq_       | _pblk_map_rq_       |
| ..      | _pblk_map_erase_rq_       |

| name | call     |
| :-------------: | :-------------: |
| _pblk_map_rq_       |    _pblk_map_erase_rq_    |

| name | call     |
| :-------------: | :-------------: |
| _pblk_map_rq_       | _pblk_map_page_data_       |
| _pblk_map_erase_rq_     | _pblk_map_page_data_      |

## Important data structure

* _struct rrpc(rrpc.h)_

~~~ c
struct rrpc {
	struct nvm_tgt_dev *dev;
	struct gendisk *disk;

	sector_t soffset; /* logical sector offset */

	int nr_luns;
	struct rrpc_lun *luns;

	/* calculated values */
	unsigned long long nr_sects;

	/* Write strategy variables. Move these into each for structure for each
	 * strategy
	 */
	atomic_t next_lun; /* Whenever a page is written, this is updated
			    * to point to the next write lun
			    */

	spinlock_t bio_lock;
	struct bio_list requeue_bios;
	struct work_struct ws_requeue;

	/* Simple translation map of logical addresses to physical addresses.
	 * The logical addresses is known by the host system, while the physical
	 * addresses are used when writing to the disk block device.
	 */
	struct rrpc_addr *trans_map;

	/* also store a reverse map for garbage collection */
	struct rrpc_rev_addr *rev_trans_map;
	spinlock_t rev_lock;

	struct rrpc_inflight inflights;

	mempool_t *addr_pool;
	mempool_t *page_pool;
	mempool_t *gcb_pool;
	mempool_t *rq_pool;

	struct timer_list gc_timer;
	struct workqueue_struct *krqd_wq;
	struct workqueue_struct *kgc_wq;
};
~~~

rrpc 구조체 자료구조 중 _struct rrpc_addr *trans_map;_, _struct rrpc_rev_addr *rev_trans_map;_ 멤버 변수를 사용하여 address mapping 을 manage 한다. 각 멤버 구조체는 같은 파일(rrpc.h)에 다음과 같이 정의되어 있다.

* _struct rrpc_addr & struct rrpc_rev_addr(rrpc.h)_

~~~ c
  /* Logical to physical mapping */
  struct rrpc_addr {
  	u64 addr;
  	struct rrpc_block *rblk;
  };

  /* Physical to logical mapping */
  struct rrpc_rev_addr {
  	u64 addr;
};
~~~

* _struct ppa_addr(lightnvm.h)_

~~~ c
struct ppa_addr {
	/* Generic structure for all addresses */
	union {
		struct {
			u64 blk		: NVM_BLK_BITS;
			u64 pg		: NVM_PG_BITS;
			u64 sec		: NVM_SEC_BITS;
			u64 pl		: NVM_PL_BITS;
			u64 lun		: NVM_LUN_BITS;
			u64 ch		: NVM_CH_BITS;
			u64 reserved	: 1;
		} g;

		struct {
			u64 line	: 63;
			u64 is_cached	: 1;
		} c;

		u64 ppa;
	};
};
~~~
physical page address space를 나타내는 포괄적인 자료구조로서 union(공용체)를 사용하므로 "structure g" 크기의 메모리 구조를 공용으로 사용함.


* _struct pblk(pblk)_

~~~ c
struct pblk {
	struct nvm_tgt_dev *dev;
	struct gendisk *disk;

	struct kobject kobj;

	struct pblk_lun *luns;

	struct pblk_line *lines;		/* Line array */
	struct pblk_line_mgmt l_mg;		/* Line management */
	struct pblk_line_meta lm;		/* Line metadata */

	int ppaf_bitsize;
	struct pblk_addr_format ppaf;

	struct pblk_rb rwb;

	int min_write_pgs; /* Minimum amount of pages required by controller */
	int max_write_pgs; /* Maximum amount of pages supported by controller */
	int pgs_in_buffer; /* Number of pages that need to be held in buffer to
			    * guarantee successful reads.
			    */

	sector_t capacity; /* Device capacity when bad blocks are subtracted */
	int over_pct;      /* Percentage of device used for over-provisioning */

	/* pblk provisioning values. Used by rate limiter */
	struct pblk_rl rl;

	struct semaphore erase_sem;

	unsigned char instance_uuid[16];
#ifdef CONFIG_NVM_DEBUG
	/* All debug counters apply to 4kb sector I/Os */
	atomic_long_t inflight_writes;	/* Inflight writes (user and gc) */
	atomic_long_t padded_writes;	/* Sectors padded due to flush/fua */
	atomic_long_t padded_wb;	/* Sectors padded in write buffer */
	atomic_long_t nr_flush;		/* Number of flush/fua I/O */
	atomic_long_t req_writes;	/* Sectors stored on write buffer */
	atomic_long_t sub_writes;	/* Sectors submitted from buffer */
	atomic_long_t sync_writes;	/* Sectors synced to media */
	atomic_long_t compl_writes;	/* Sectors completed in write bio */
	atomic_long_t inflight_reads;	/* Inflight sector read requests */
	atomic_long_t sync_reads;	/* Completed sector read requests */
	atomic_long_t recov_writes;	/* Sectors submitted from recovery */
	atomic_long_t recov_gc_writes;	/* Sectors submitted from write GC */
	atomic_long_t recov_gc_reads;	/* Sectors submitted from read GC */
#endif

	spinlock_t lock;

	atomic_long_t read_failed;
	atomic_long_t read_empty;
	atomic_long_t read_high_ecc;
	atomic_long_t read_failed_gc;
	atomic_long_t write_failed;
	atomic_long_t erase_failed;

	struct task_struct *writer_ts;

	/* Simple translation map of logical addresses to physical addresses.
	 * The logical addresses is known by the host system, while the physical
	 * addresses are used when writing to the disk block device.
	 */
	unsigned char *trans_map;
	spinlock_t trans_lock;

	struct list_head compl_list;

	mempool_t *page_pool;
	mempool_t *line_ws_pool;
	mempool_t *rec_pool;

	mempool_t *r_rq_pool;
	mempool_t *w_rq_pool;
	mempool_t *line_meta_pool;

	struct workqueue_struct *kw_wq;
	struct timer_list wtimer;

	struct pblk_gc gc;
};
~~~
pblk 구조체의 가장 중요한 멤버 변수로서 _unsigned char *trans_map_가 있다. logical address를 physical address로 mapping 해 주는 mapping table에 대한 포인터 변수로서, _pblk_trans_map_get_, _pblk_trans_map_set_ 과 같은 getter, setter 함수가 있다.
