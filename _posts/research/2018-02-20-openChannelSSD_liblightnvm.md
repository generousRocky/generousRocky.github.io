---
layout: article
title:  "liblightnvm(work in progress)"
date:   2018-02-20 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "유저스페이스에서 Open Channel SSD 컨트롤 하기"
image:
comments: true
locale: "vn"
share: true
ads: true
---

{% include toc.html %}


# Obtaining device information

다음과 같은 명령어를 통해서 Open Channel SSD의 physical geometry를 알 수 있다. 즉, 디바이스의 정보를 얻을 수 있음.

~~~sh
nvm_dev info /dev/nvme0n1
~~~

~~~sh
# Device information -- nvm_dev_pr
dev:
  verid: 0x02
  be_id: 0x02
  name: 'nvme0n1'
  path: '/dev/nvme0n1'
  fd: 3
  ssw: 12
  pmode: 'DUAL'
  erase_naddrs_max: 64
  read_naddrs_max: 64
  write_naddrs_max: 64
  meta_mode: 0
  bbts_cached: 0
dev_geo:
  nchannels: 16
  nluns: 8
  nplanes: 2
  nblocks: 1020
  npages: 512
  nsectors: 4
  page_nbytes: 16384
  sector_nbytes: 4096
  meta_nbytes: 16
  tbytes: 2190433320960
  tmbytes: 2088960
dev_ppaf:
  ch_off: 25
  ch_len: 04
  lun_off: 22
  lun_len: 03
  pl_off: 02
  pl_len: 01
  blk_off: 12
  blk_len: 10
  pg_off: 03
  pg_len: 09
  sec_off: 00
  sec_len: 02
dev_ppaf_mask:
  ch:  '0000000000000000000000000000000000011110000000000000000000000000'
  lun: '0000000000000000000000000000000000000001110000000000000000000000'
  pl:  '0000000000000000000000000000000000000000000000000000000000000100'
  blk: '0000000000000000000000000000000000000000001111111111000000000000'
  pg:  '0000000000000000000000000000000000000000000000000000111111111000'
  sec: '0000000000000000000000000000000000000000000000000000000000000011'
~~~

# Physical Addressing

struct nvm_addr 라는 자료구조로 물리 페이지 주소가 표현된다.

Construct an address for sector 3 within page 11 in block 200 on plane 0 of LUN 1 in channel 4:

~~~
nvm_addr from_geo /dev/nvme0n1 4 1 0 200 10 3
~~~

Yielding:

~~~
0x04010003000a00c8: {ch: 04, lun: 01, pl: 0, blk: 0200, pg: 010, sec: 3}
~~~

플래시 메모리에 I/O 할 수 있도록 해주는  유저스페이스 라이브러리, I/O 인텐시브한 어플리케이션이 어플리케이션에서 FTL을 구현할 수 있도록 도와줄 수 있다.

liblightnvm is a user space library that manages provisioning of and I/O submission to physical flash. The motivation is to enable I/O-intensive applications to implement their own Flash Translation Layer (FTLs) using the internal application data structures. The design is based on the principle that high-performance I/O applications often use structures that assimilates structures found within a Flash translation layer. This include log-structured data structures that provides their own mechanisms for data placement, garbage collection, and I/O scheduling strategies.

For example, popular key-value stores often use a form of Log Structured Merge Trees (LSMs) as their base data structure (including RocksDB, MongoDB, Apache Cassandra). The LSM is in itself a form of FTL, which manages data placement and garbage collection. This class of applications can benefit from a direct path to physical flash to take full advantage of the optimizations they do and spend host resources on, instead of missing them through the several levels of indirection that the traditional I/O stack imposes to enable genericity: page cache, VFS, file system, and device physical - logical translation table. liblightnvm exposes append-only primitives using direct physical flash to support this class of applications.

<https://github.com/OpenChannelSSD/liblightnvm>

# vectorized IO

## write constraint

1. Erase before write
2. they must be at the granularity of a full flash page
3. they must be contiguous within a block
4. writes must be performed to the block accross all planes(minimum write)
  한 die에 plane이 두 개 있을때, 쓰기는 이 plane에 모두 이루어져야 한다. 따라서, 이 조건을 만족하도록 쓰기를 하거나 *plane-mode*를 꺼 주는 옵션을 써야 한다.
5. we can construct a command with 64 addresses.(maximum write)
  한 nvme command에 64개의 ppa를 지정 해 줄 수 있다. 따라서, 4k X 64크기 만큼의 데이터 쓰기를 한 커멘드를 통해 요청할 수 있다.


## read constraint

1. The granularity of a read is a single sector (the smallest addressable unit) and can be performed non-contiguously.
2. The primary constraint for a read to adhere to is that the block which is read from must be closed. That is, all pages within the block must have been written
  읽기 전에 해당 블록은 모든 페이지가 다 쓰여져 있는 상태 이어야 한다.

# virtual block
  liblightnvm, therefore, introduces a pure software abstraction, a virtual block, to reduce the cognitive load for application developers.

 A virtual block behaves as a physical, that is, the constraints of working with NAND media also apply to a virtual block. However, the abstraction encapsulates the command and address construction of parallel vectorized IO and exposes a flat address space which is read/written in a manner equivalent to the read/write primitives offered by libc.


# Block Line

 













































