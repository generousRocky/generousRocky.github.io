---
layout: article
title:  "LightNVM: The Linux Open-Channel SSD Subsystem"
date:   2017-08-28 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "Experimental Evaluation of OCSSD(CNEX) and LightNVM"
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

# This is work in progress...

# Experimental Evaluation

Our exprimental setup consists of test PC equipped with an Intel ~~ , 8GB of DDR3 RAM, an Open-Channel SSD (CNEX Labs Westlake SDK) with 2TB NAND MLC FLASH.

The host runs Ubuntu 16.04 with Linux Kernel 4.12-12+ and pblk patches applied.

* Open-Channel SSD

| Header One     | Header Two     |
| :------------- | :------------- |
| Item One       | Item Two       |

* Parallel Unit Characteristics

| Header One     | Header Two     |
| :------------- | :------------- |
| Item One       | Item Two       |

* Bandwidth

| Header One     | Header Two     |
| :------------- | :------------- |
| Item One       | Item Two       |

Table 1~3 contains a general characterization for the eval- uated Open-Channel SSD. Per-PU sequential read and write bandwidth were gathered experimentally through a modified version of fio that uses the PPA I/O interface and issues vector I/Os directly to the device. The pblk factory state and steady state (where garbage collection is active) are measured experimentally through standard fio on top of pblk. [1]


# References
[1] Bjørling, Matias, Javier González, and Philippe Bonnet. "LightNVM: The Linux Open-Channel SSD Subsystem." FAST. 2017.
APA
