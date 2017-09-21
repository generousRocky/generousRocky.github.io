---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-09-19 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "Kernel Code Analysis - Important data structure"
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

## FTL Mapping

pblk_lookup_l2p_seq 함수에서 parameter중 하나로 *sector_t blba* 가 주어지고, *pblk_trans_map_get()* 함수를 통해 각각의 해당하는 ppa(physical page address)로 변환된다.

* _pblk_lookup_l2p_seq(pblk-core.c)_
```c
void pblk_lookup_l2p_seq(struct pblk *pblk, struct ppa_addr *ppas, sector_t blba, int nr_secs)
{
	int i;

	spin_lock(&pblk->trans_lock);
	for (i = 0; i < nr_secs; i++) {
		struct ppa_addr ppa;

		ppa = ppas[i] = pblk_trans_map_get(pblk, blba + i);

		/* If the L2P entry maps to a line, the reference is valid */
		if (!pblk_ppa_empty(ppa) && !pblk_addr_in_cache(ppa)) {
			int line_id = pblk_dev_ppa_to_line(ppa);
			struct pblk_line *line = &pblk->lines[line_id];

			kref_get(&line->ref);
		}
	}
	spin_unlock(&pblk->trans_lock);
}
```
* _pblk_trans_map_get(pblk.h)_
```c
static inline struct ppa_addr pblk_trans_map_get(struct pblk *pblk, sector_t lba)
{
	struct ppa_addr ppa;

	if (pblk->ppaf_bitsize < 32) {
		u32 *map = (u32 *)pblk->trans_map;

		ppa = pblk_ppa32_to_ppa64(pblk, map[lba]);
	} else {
		struct ppa_addr *map = (struct ppa_addr *)pblk->trans_map;

		ppa = map[lba]; // logical block address to physical page address
	}

	return ppa;
}
```

## Important data structure


* _struct ppa_addr(lightnvm.h)_

```
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
```

physical page address space를 나타내는 포괄적인 자료구조로서 union(공용체)를 사용하므로 "structure g" 크기의 메모리 구조를 공용으로 사용함.


* _struct pblk(pblk.h)_

```
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
```
pblk 구조체의 가장 중요한 멤버 변수로서 _unsigned char *trans_map_가 있다. logical address를 physical address로 mapping 해 주는 mapping table에 대한 포인터 변수로서, _pblk_trans_map_get_, _pblk_trans_map_set_ 과 같은 getter, setter 함수가 있다.


* _struct pblk(include/linux/lightnvm.h)_
```
struct nvm_rq {
        struct nvm_tgt_dev *dev;

        struct bio *bio;

        union {
                struct ppa_addr ppa_addr;
                dma_addr_t dma_ppa_list;
        };

        struct ppa_addr *ppa_list;

        void *meta_list;
        dma_addr_t dma_meta_list;

        struct completion *wait;
        nvm_end_io_fn *end_io;

        uint8_t opcode;
        uint16_t nr_ppas;
        uint16_t flags;

        u64 ppa_status; /* ppa media status */
        int error;

        void *private;
};
```
nvme 디바이스 io요청에 대한 구조체, target device 에 대한 정보와 bio(block io 구조체) 정보를 갖고 있음.

```
struct bio {
	struct bio		*bi_next;	/* request queue link */
	struct gendisk		*bi_disk;
	u8			bi_partno;
	blk_status_t		bi_status;
	unsigned int		bi_opf;		/* bottom bits req flags,
						 * top bits REQ_OP. Use
						 * accessors.
						 */
	unsigned short		bi_flags;	/* status, etc and bvec pool number */
	unsigned short		bi_ioprio;
	unsigned short		bi_write_hint;

	struct bvec_iter	bi_iter;

	/* Number of segments in this BIO after
	 * physical address coalescing is performed.
	 */
	unsigned int		bi_phys_segments;

	/*
	 * To keep track of the max segment size, we account for the
	 * sizes of the first and last mergeable segments in this bio.
	 */
	unsigned int		bi_seg_front_size;
	unsigned int		bi_seg_back_size;

	atomic_t		__bi_remaining;

	bio_end_io_t		*bi_end_io;

	void			*bi_private;
#ifdef CONFIG_BLK_CGROUP
	/*
	 * Optional ioc and css associated with this bio.  Put on bio
	 * release.  Read comment on top of bio_associate_current().
	 */
	struct io_context	*bi_ioc;
	struct cgroup_subsys_state *bi_css;
#ifdef CONFIG_BLK_DEV_THROTTLING_LOW
	void			*bi_cg_private;
	struct blk_issue_stat	bi_issue_stat;
#endif
#endif
	union {
#if defined(CONFIG_BLK_DEV_INTEGRITY)
		struct bio_integrity_payload *bi_integrity; /* data integrity */
#endif
	};

	unsigned short		bi_vcnt;	/* how many bio_vec's */

	/*
	 * Everything starting with bi_max_vecs will be preserved by bio_reset()
	 */

	unsigned short		bi_max_vecs;	/* max bvl_vecs we can hold */

	atomic_t		__bi_cnt;	/* pin count */

	struct bio_vec		*bi_io_vec;	/* the actual vec list */

	struct bio_set		*bi_pool;

	/*
	 * We can inline a number of vecs at the end of the bio, to avoid
	 * double allocations for a small number of bio_vecs. This member
	 * MUST obviously be kept at the very end of the bio.
	 */
	struct bio_vec		bi_inline_vecs[0];
};
```
