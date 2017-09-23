---
layout: article
title:  "세상의 모든 개발환경 팁:Tips for vim, tmux, ctags, cscope, etc."
date:   2017-9-20 10:00:00 Z
author: Rocky Lim
categories: whatever
excerpt: "Collection of all tips I've read and found"
image:
  feature:
  teaser: devEnvTip_01.png
  path: images/devEnvTip_01.png
comments: true
locale: "vn"
share: true
ads: true
---


<p style="text-align: center;">
  <img src="{{ site.url }}/images/devEnvTip_01.png " alt="Drawing" style="width: 600;"/>
</p>

{% include toc.html %}

본 포스팅에서는 개발환경 자체에 대한 설치 및 세팅 과정은 다루지 않고, 효과적인 활용법에 대해서만 정리 했습니다.


# vim
## 기본 단축키
<p style="text-align: center;">
  <img src="{{ site.url }}/images/devEnvTip_02.png " alt="Drawing" style="width: 600;"/>
</p>
<https://kldp.org/node/102947>

## 창 생성
* CTRL-W s
:[N]sp[plit]
현재 파일을 두 개의 수평 창으로 나눔
* CTRL-W v
:[N]vs[plit]
현재 파일을 두 개의 수직 창으로 나눔
* CTRL-W n
:new
새로운 수평 창 생성
* CTRL-W ^ 또는 CTRL-W CTRL-^ 수평 창으로 나누고 이전 파일의 오픈
* CTRL-W f 창을 수평으로 나누고 커서 위치의 파일 오픈
* CTRL-W i 커서 위치의 단어가 정의된 파일을 오픈

## 창삭제
* CTRL-W q :q[uit]! 현재 커서의 창을 종료
* CTRL-W c :close 현재 커서의 창 닫기
* CTRL-W o :on[ly] 현재 커서의 창만 남기고 모든 창 삭제

## 창이동
* CTRL-W h 왼쪽 창으로 커서 이동
* CTRL-W j 아래쪽 창으로 커서 이동
* CTRL-W k 위쪽 창으로 커서 이동
* CTRL-W l 오른쪽 창으로 커서 이동
* CTRL-W w 창을 순차적으로 이동
* CTRL-W p 가장 최근에 이동한 방향으로 이동
* CTRL-W t 최상위 창으로 이동
* CTRL-W b 최하위 창으로 이동

## 창이동
* CTRL-W r 순착으로 창의 위치를 순환
* CTRL-W x 이전 창과 위치를 바꿈
* CTRL-W H 현재창을 왼쪽 큰화면으로 이동
* CTRL-W J 현재창을 아래쪽 큰화면으로 이동
* CTRL-W K 현재창을 위쪽 큰화면으로 이동
* CTRL-W L 현재창을 오른쪽 큰화면으로 이동

## 창 크기 조정
* CTRL-W + 창의 크기를 모두 균등하게 함
* CTRL-W _ 수평 분할에서 창의 크기를 최대화
* CTRL-W | 수직 분할에서 창의 크기를 최대화


* CTRL-W [N]+
창의 크기를 N행 만큼 증가

* CTRL-W [N]-
창의 크기를 N행 만큼 감소

* CTRL-W [N]>
창의 크기를 오른쪽으로 N칸 만큼 증가

* CTRL-W [N]<
창의 크기를 오른쪽으로 N칸 만큼 감소

## 실행 취소
* u 실행 취소
* ctrl-r 재실행(실행취소의 취소)

## 탭생성, 이동
* tabnew [file path] 탭생성
* gt, gT 탭 간 이동

## 기타

* [찾고 싶은 글자 찾기] 찾으려는 문자열에 커서를 두고** * ** 나  #을 누른다. 검색 결과를 왔다갔다 하려면, n또는 N으로 이동 할 수 있다.




# ctags
