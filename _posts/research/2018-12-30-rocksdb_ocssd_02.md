---
layout: article
title:  "KSC'18 accepted paper"
date:   2018-12-30 10:00:00 Z
author: Rocky Lim
categories: research
excerpt: "플래시 내 I/O 분리 처리를 통한 LSM-tree 기반 데이터베이스 성능 최적화"
image:
  feature: rocksdb_02.png
  teaser: rocksdb_02.png
  path: images/rocksdb_02.png
comments: true
locale: "vn"
share: true
ads: true
---

{% include toc.html %}

# 1. Abstract
고성능 저장장치의 역할은 웹-스케일 인프라에서 점차 더 중요해 지고 있다. 특히 NVMe(Non-Volatile Memory Express) 기반 SSD(Solid State Device)로 대표되는 차세대 저장장치는 데이터센터에 적극적으 로 도입되고 있다. 하지만 데이터센터에서 실행되는 응용프로그램은 이러한 고성능 저장장치의 특징을 고려하지 않는다. 본 논문에서는 NVMe SSD와 같은 고성능 저장장치를 사용하는 LSM-tree(LogStructured Merge tree) 기반의 데이터베이스 시스템에서, 읽기와 쓰기 요청이 혼재되어 있는 워크로드에 서의 성능 저하 현상에 집중한다. 이 문제를 해결하기 위해 본 연구에서는 I/O 작업을 분리하여 처리하 도록 어플리케이션 계층에서의 플래시 관리 기법을 제시한다.

# 2. get paper from here

LINK: [here](https://github.com/RockyLim92/RockyLim92.github.io/blob/master/publication/Open%20Channel%20SSD%20%ED%94%8C%EB%9E%AB%ED%8F%BC%EC%97%90%EC%84%9C%20%EC%93%B0%EA%B8%B0%20%EB%B2%84%ED%8D%BC%20%EB%B0%8F%20%EC%8A%A4%EB%A0%88%EB%93%9C%20%EA%B5%AC%EC%84%B1%EC%97%90%20%EB%94%B0%EB%A5%B8%20%EC%84%B1%EB%8A%A5%20%EB%B6%84%EC%84%9D.pdf)

or

LINK: [here](https://github.com/RockyLim92/RockyLim92.github.io/blob/master/publication/rocky_kcs18.pdf)
