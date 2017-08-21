---
layout: article
title:  "번역) Open-Channel SSD Subsystem Docs"
date:   2017-08-18 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "Getting Started With Open Channel SSD"
comments: true
locale: "vn"
share: true
ads: true
---


{% include toc.html %}

# How to use

Open-Channel SSD를 사용하기 위해서는 운영체제 커널의 도움이 필요하다. 4.4 버전 이상의 리눅스 커널이 LightNVM subsystem을 포함한다. 이 프로젝트는 여전히 개발중에 있으므로 가장 최근에 릴리즈 된 버전을 사용하는 것을 추천한다. 가장 최신 버전의 소스코드는 다음 링크에서 사용 가능하다. [https://github.com/OpenChannelSSD/linux](https://github.com/OpenChannelSSD/linux).

지원하는 커널로 부팅한 후에 다음과 같은 세 가지 조건을 만족해야 한다.

1. A compatible device, such as QEMU NVMe or an Open-Channel SSD, such as the CNEX Labs LightNVM SDK.
2. A media manager on top of the device driver. The media manager manages the partition table for the device.
3. A target on top of the block manager that exposes the Open-Channel SSD.

## Install Kernel 4.12+

LightNVM is directly supported in Linux since kernel 4.4. Pblk, which is used to get started, is available since 4.12+. Make sure to install 4.12+ or later if you want to use pblk.

## Install nvme-cli tool

nvme-cli는 nvme devices를 관리하기 위한 도구로서 다음 명령어를 통해 설치될 수 있다.

    sudo apt-get install nvme-cli

또는 다음 url을 통해서 설치가 가능하다. [https://github.com/linux-nvme/nvme-cli](https://github.com/linux-nvme/nvme-cli)

만약 리눅스 우분투를 사용하고 있다면, nvme-cli 깃헙 프로젝트를 참고하면 좋을 것 같다.

## Open-Channel SSD 하드웨어 사용하기.

만약 CNEX Labs의 LightNVM SDK을 가지고 있거나 다른 Open-Channel SSD를 가지고 있다.면 다음 명령어를 통해 그것들을 확인 할 수 있다.

    sudo nvme lnvm list

결과는 예를들어 다음과 같은것이다:

    nvme lnvm list
    Number of devices: 1
    Device      	Block manager	Version
    nvme0n1     	gennvm      	(0,1,0)

만약 block manager가 아무것도 보여주지 않는다면, device는 초기화 작업이 필요하고, 다음과 같은 명령어를 사용할 수 있다.

    sudo nvme lnvm init -d nvme0n1

## QEMU 사용하기.

Keith Busch의 QEMU branch를 사용하면, 백앤드 파일을 사용하여 LightNVM와 호환 가능한 장치를 보일 수 있다.

### Configure QEMU

NVMe device를 위한 빈 파일 생성하기.

    dd if=/dev/zero of=blknvme bs=1M count=1024

이 명령어는 "blknvme"라고 하는 크기가 1GB인 빈 파일을 만들어 낸다. 다음 명령어를 통해 선호하는 리눅스 이미지로 부팅할 수 있다.

    qemu-system-x86_64 -m 4G -smp 1 --enable-kvm
    -hda $LINUXVMFILE -append "root=/dev/sda1"
    -kernel "/home/foobar/git/linux/arch/x86_64/boot/bzImage"
    -drive file=blknvme,if=none,id=mynvme
    -device nvme,drive=mynvme,serial=deadbeef,namespaces=1,lver=1,nlbaf=5,lba_index=3,mdts=10

$LINUXVMFILE 부분을 이미 설치 된 리눅스 가상머신으로 대신하면 된다.

QEMU는 다음과 같이 LightNVM의 파라미터를 지원한다:

    - lver=<int>       : version of the LightNVM standard to use, Default:1
    - lbbtable=<file>    : Load bad block table from file destination (Provide path to file. If no file is provided a bad block table will be generation. Look at lbbfrequency. Default: Null (no file).

이와 같은 QEMU안의 LightNVM 파라미터 리스트는 `$QUEMU_DIR/hw/block/nvme.c` 에서 추가 옵션을 통해 발견할 수 있을것이다.

## Instantiate media manager and target

설치가 끝나고 해당 커널로 부팅이 되었으면, 각 디바이스들은 다음과 같이 나타날 것이다.

    sudo nvme lnvm list

그리고 다음 명령어를 통해 초기화 된다:

    sudo nvme lnvm init -d nvme0n1
    sudo nvme lnvm create -d nvme0n1 --lun-begin=0 --lun-end=3 -n mydevice -t pblk

빠른 초기화를 위해서 -f을 사용하면 디바이스에서 L2P 테이블을 recovering 하는 것을 피할 수 있다.

    sudo nvme lnvm create -d nvme0n1 --lun-begin=0 --lun-end=3 -n mydevice -t pblk -f

--help를 통해 각 명령어에 대한 도움을 받을 수 있다. 예를 들어, sudo nvme lnvm create --help

Assuming nvme0n1 was shown during "nvme lnvm list", it will then expose /dev/mydevice as a block device using it as the backend. Please note that pblk is only available at the Linux kernel Github repository, and it yet to be upstream.

## Source install

### Compile latest kernel

최신 LightNVM 커널은 다음 깃 주소에서 받을 수 있다.:

   `git clone https://github.com/OpenChannelSSD/linux.git`

in the "for-next" branch.

Make sure that the .config file at least includes:

    CONFIG_NVM=y
    # Expose the /sys/module/lnvm/parameters/configure_debug interface
    CONFIG_NVM_DEBUG=y
    # Target support (required to expose the open-channel SSD as a block device)
    CONFIG_NVM_PBLK=y    
    # For NVMe support
    CONFIG_BLK_DEV_NVME=y

배포된 가이드를 따라서 커널을 컴파일하고 설치하면 된다.

### QEMU Installation

Open-Channel SSDs 를 위한 QEMU의 지원은 NVME 호환 디바이스를 구현한 Keith Busc의 qemu-nvme branch를 기본으로 한다.

Clone the qemu source from

    git clone https://github.com/OpenChannelSSD/qemu-nvme.git

and configure the QEMU source with

    ./configure --enable-linux-aio --target-list=x86_64-softmmu --enable-kvm

then install by "make" and "install"

# Common Problems

## Failed to open LightNVM mgmt /dev/lightnvm/control. Error: -1

Either you need to run nvme as root, or you are running an older kernel than 4.4.

## Kernel panic on boot using NVMe

 1. Zero out your nvme backend file.

    dd if=/dev/zero of=backend_file bs=1M count=X

 2. Remember to upgrade the qemu-nvme branch as well. The linux and qemu-nvme repos follow each other.
