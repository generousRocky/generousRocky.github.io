---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-09-09 11:00:00 Z
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
