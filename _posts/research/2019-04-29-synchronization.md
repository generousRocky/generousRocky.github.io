---
layout: article
title:  "performance Comparion of synchroniztion Operations + Intel Transactional Memory Operation"
date:   2019-04-29 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "멀티스레드 동기화 방법 비교"
image:
  feature:
  teaser: 2019-04-29-synchronization/sync.png
  path: images/2019-04-29-synchronization/sync.png
comments: true
locale: "vn"
share: true
ads: true
---

여러가지 멀티스레드 동기화 기법 중 어느 기법이 가장 성능이 좋을지 확인해봐라.

-- 교수님 --




{% include toc.html %}



## System Specification

### CPU

```sh
rocky@dum:~$ lscpu
Architecture:          	x86_64
CPU op-mode(s):        	32-bit, 64-bit
Byte Order:            	Little Endian
CPU(s):                	32
On-line CPU(s) list:   	0-31
Thread(s) per core:   	2
Core(s) per socket:    	8
Socket(s):             	2
NUMA node(s):          	2
Vendor ID:             	GenuineIntel
CPU family:            	6
Model:                 	79
Model name:            	Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz
Stepping:              	1
CPU MHz:               	1200.843
CPU max MHz:           	3000.0000
CPU min MHz:           	1200.0000
BogoMIPS:              	4201.30
Virtualization:        	VT-x
L1d cache:             	32K
L1i cache:             	32K
L2 cache:              	256K
L3 cache:              	20480K
NUMA node0 CPU(s):    	0-7,16-23
NUMA node1 CPU(s):     	8-15,24-31
```

### Memory

```sh
rocky@dum:~$ sudo dmidecode -t 17
# dmidecode 3.0
Getting SMBIOS data from sysfs.
SMBIOS 3.0.0 present.
Memory Device
Array Handle: 0x002A
Error Information Handle: Not Provided
Total Width: 72 bits
Data Width: 64 bits
Size: 8192 MB
Form Factor: DIMM
Set: None
Locator: P1-DIMMA1
Bank Locator: P0_Node0_Channel0_Dimm0
ype: DDR4
Type Detail: Synchronous
Speed: 2400 MHz
Manufacturer: Samsung
Serial Number: 2087B773
Asset Tag: P1-DIMMA1_AssetTag (date:17/38)
Part Number: M393A1G40EB1-CRC
Rank: 1
Configured Clock Speed: 2133 MHz
Minimum Voltage: Unknown
Maximum Voltage: Unknown
Configured Voltage: Unknown
```

- Summary: Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz. 64아키텍처의 16물리 코어(하이퍼 스레딩, 32 논리 코어) 머신.  NUMA 아키텍처로 2개의 socket(NUMA node)이 있으며, 각 socket당 8개 물리 코어가 있음. 메인 메모리는 DDR4의 8192MB 메모리가 4개 뱅크에 각각 위치하고 있으며 총 메인 메모리 공간은 32GB이다.

## Intel(R) Xeon(R) CPU E5-2620에서 제공하는 Synchronization operations

### 1. Fetch And Add계열

```c
type __sync_fetch_and_add (type *ptr, type value, ...)
type __sync_fetch_and_sub (type *ptr, type value, ...)
type __sync_fetch_and_or (type *ptr, type value, ...)
type __sync_fetch_and_and (type *ptr, type value, ...)
type __sync_fetch_and_xor (type *ptr, type value, ...)
type __sync_fetch_and_nand (type *ptr, type value, ...)
```

Note: These builtins perform the operation suggested by the name, and returns the value that had previously been in memory.

```sh
{ tmp = *ptr; *ptr op= value; return tmp; }
{ tmp = *ptr; *ptr = ~tmp & value; return tmp; }   // nand
```


### 2. Add And Fetch계열

```c
type __sync_add_and_fetch (type *ptr, type value, ...)
type __sync_sub_and_fetch (type *ptr, type value, ...)
type __sync_or_and_fetch (type *ptr, type value, ...)
type __sync_and_and_fetch (type *ptr, type value, ...)
type __sync_xor_and_fetch (type *ptr, type value, ...)
type __sync_nand_and_fetch (type *ptr, type value, ...)
```

Note: These builtins perform the operation suggested by the name, and return the new value.

```sh
{ *ptr op= value; return *ptr; }
{ *ptr = ~*ptr & value; return *ptr; }   // nand
```

### 3. Compare And Swap

```c
type __sync_val_compare_and_swap (type *ptr, type oldval type newval, ...)
```

Note: These builtins perform an atomic compare and swap. That is, if the current value of *ptr is oldval, then write newval into *ptr.

### 4. Memory Barrier

```c
__sync_synchronize (...)
```

Note: This builtin issues a full memory barrier.


### 5. Test And Set

```c
type __sync_lock_test_and_set (type *ptr, type value, ...)
```
Note: This builtin, as described by Intel, is not a traditional test-and-set operation, but rather an atomic exchange operation. It writes value into *ptr, and returns the previous contents of *ptr.

```c
void __sync_lock_release (type *ptr, ...)
```
Note: This builtin releases the lock acquired by __sync_lock_test_and_set. Normally this means writing the constant 0 to *ptr.

## Experimental Evaluation

single thread run과 동기화 기법들인 mutex lock, Compare-and-Swap, Fetch-and-Add, Add-and-Fetch, Test and Set(TAS를 이용한 mutual exclusion), Memory Barrier 총 6 가지를 사용하여 shared variable의 increment 성능 평가를 진행한다. Single thread를 제외한 6가지 방법에서는 32개 thread를 사용하였다.

| Method | Results(sec)|
|:--------|:--------|
| Single thread | 3.041056455s |
| Mutex lock | 133.816444880s |
| Fetch-and-Add | 26.720684224s |
| Add-and-Fetch| 26.909436926s |
| Compare-And-Swap| 101.935627317s |
| Test-and-Set| 1467.726637515s |
| Memory Barrier| 324.967494416s |

당연히, increment 같은 매우 짧은 task만 수행하므로 스레드 간 동기화 오버헤드가 성능의 대부분을 차지한다. 따라서 전체 elapse time은 single thread가 가장 짧다. 멀티 스레드 동기화가 오퍼레이션 중에는 fet and add 계열이 성능이 가장 좋아보이지만 thread contention 정도에 따라 결과가 다르게 나올 수 있다.
