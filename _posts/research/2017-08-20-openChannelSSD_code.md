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

#pblk: Physical Block Device Target

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

For more information please refer to: <http://lightnvm.io> or contact me
