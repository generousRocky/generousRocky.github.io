---
layout: article
title: "컴퓨터공학부 신입생 기초 시험"
date: 2017-07-22 13:44:20 Z
author: Rocky Lim
categories: whatever
excerpt: "합격하고 싶다."
image:
comments: true
locale: "vn"
share: true
ads: true
---

{% include toc.html %}
# 2015-2
i
1.

1.1 more powerful한 instruction의 예로 cisc ISA를 들 수 있다. CISC는 다양한 instruction 의 종류를 제공하기 때문에, 비교적 한 instruction에서 여러 기능을 수행할 수 있음. single instruction execution에서는 instruction의 개수가 적기 때문에 좋은 performance를 기대할 수 있지만, pipeline 을 할 경우, 복잡하고 긴 instruction으로 인해 효과적인 piplining이 힘들다. 따라서, 항상 performace가 증가한다고 볼 수 없다.


more powerful instruction은 하나의 instruction이 많은 일을 하는 instruction을 의미한다. 즉 CISC ISA를 의미한다. 실제 과거 메모리가 매우 느리고 캐시가 없는 환경의 컴퓨터 구조에서는 하나의 instruction이 많은 일을 할 수 있는 것이 느린 메모리의 접근을 줄일 수 있기때문에 더 좋은 컴퓨터 성능을 제공할 수 있다. 하지만, 캐시의 등장, 한칩에 프로세서의 모든 기능을 넣을 수 있는 기술의 등장, 그리고 파이프라이닝 기술의 등장으로 CISC보다 RISC가 효과적이다. 왜냐하면 캐시메모리가 있기때문에 하나의 instruction을 복잡하게 하는 것보다 간단한 instruction들을 파이프라인하는 것이 효과적이다. 또한 파이프라인을 효과적으로하기 위해 포맷도 간단히하고 소수의 instruction을 제공하는 RISC가 현재 컴퓨터 시스템에서는 더 강력한 컴퓨터 성능을 제공한다.


1.2 파이프라인의 깊이를 늘리는 방법은 슈퍼파이프라이닝 기법으로 파이프라이닝을 세세하게 잘라서 깊이를 증가시킨 방법이다. 이러한 방법은 사이클을 나눠서 명령어 수준의 병렬성을 증가시킨다. 이론적으로 파이프라인 깊이가 증가할 수록 하나의 인스트럭션을 수행하는 사이클 타임이 줄어들기 때문에 성능이 증가한다.
하지만, 사이클 타임이 줄어드는 것은 클럭이 증가하는 것을 의미하는데, 현재 하드웨어적으로 클럭의 한계가 4GHz로 파이프라인의 깊이의 증가는 제약이 있고, 깊이가 증가함에따라 클록 스큐 현상에 민감해지고 클럭 속도가 빨라지면서 발열등의 문제가 있다. 또한 컨트롤 해저드 처리시 실패 패널티 부담이 커지는 단점이 있다.

2.
load word execution에서, instruction이 가장 오랫동안 실행될 경우는 TLB(Translation Look-aside Buffer) 에서 miss가 발생하고, page table에서도 page가 부재 할 경우이다.
virtual address를 통해 TLB에서 miss가 발생하면, 2차적으로 page table을 참조하여 address translation을 해야 한다. 만약 page table에도 요청한 virtual address mapping이 존재하지 않는다면, 보조기억장치에서 page table write를 해 주고, 이를 TLB에 업데이트를 해 주어야 한다. 이 후에 virtual address는 physical address로 변환된다.

3.
tag = 16
index = 13
offset = 3


4.
control hazard는 pc값이 sequential 하게 incremet되지 않는 경우에 발생하는 문제로서 insttruction중 branch에 의해서 발생할 수 있다. 이를 해결하기 위한 방법은 다음과 같이 세 가지가 있다.
1. optimized branch processing
		branch가 발생하는지 아닌지 빨리 알아내는 방법으로서, branch condition을 간소화 하는 방법을 통해 해결 가능하다. 또는 branch target address를 초기에 계산하는 방식으로도 구현할 수 있는데, 이를 위해 adder와 같은 하드웨어의 지원이 필요하다.

2. branch prediction
		branch가일어나지 않을 것이라고 가정하여 인스트럭션들을 그대로 실행한다. 만약i번째 instruction인  branch가 실제로 일어난다면, i+1 instruction은 nop로 만들어버리면 된다.(state를 변화시키지 않는 방법으로 구현)
3. delayed branch
		i 번째 instruction이 branch라고 했을 때, branch가 실제로 이루어지는지와는 상관 없이 i+1 instruction을 실행하는 것, 만약 branch 가 발생하지 않는다면 그대로 instuction들을 수행하면 되고, branch 가 발생한다면, target address로 branch 하여 instruction을 수행한다.


# 2016-2 (김지홍 교수님)

1. Radix Sort, Quicksort 에서 Clock cycle, Instruction 그래프 보고 원인 찾고, Radix Sort에서의 개선책

2. 8 Way Set Associate Cache에서 전체 Cache Size는 1024 byte, Byte addressinng, Cache Block은 8 Byte. Cache Organization 그려라. 24bit Addressing에서 Cache Tag, Cache Index 는 24 bit 중에 얼마나 사용할 수 있나?






2015-2 (김지홍 교수님)

1. 맞으면 증명하고, 틀리면 반례를 들어라
 (1) more powerful instruction , more computer performance?
more powerful instruction은 하나의 instruction이 많은 일을 하는 instruction을 의미한다. 즉 CISC ISA를 의미한다. 실제 과거 메모리가 매우 느리고 캐시가 없는 환경의 컴퓨터 구조에서는 하나의 instruction이 많은 일을 할 수 있는 것이 느린 메모리의 접근을 줄일 수 있기때문에 더 좋은 컴퓨터 성능을 제공할 수 있다. 하지만, 캐시의 등장, 한칩에 프로세서의 모든 기능을 넣을 수 있는 기술의 등장, 그리고 파이프라이닝 기술의 등장으로 CISC보다 RISC가 효과적이다. 왜냐하면 캐시메모리가 있기때문에 하나의 instruction을 복잡하게 하는 것보다 간단한 instruction들을 파이프라인하는 것이 효과적이다. 또한 파이프라인을 효과적으로하기 위해 포맷도 간단히하고 소수의 instruction을 제공하는 RISC가 현재 컴퓨터 시스템에서는 더 강력한 컴퓨터 성능을 제공한다.
 (2) pipelining depth를 늘릴 수록 항상 퍼포먼스가 증가하는가?

파이프라인의 깊이를 늘리는 방법은 슈퍼파이프라이닝 기법으로 파이프라이닝을 세세하게 잘라서 깊이를 증가시킨 방법이다. 이러한 방법은 사이클을 나눠서 명령어 수준의 병렬성을 증가시킨다. 이론적으로 파이프라인 깊이가 증가할 수록 하나의 인스트럭션을 수행하는 사이클 타임이 줄어들기 때문에 성능이 증가한다.
하지만, 사이클 타임이 줄어드는 것은 클럭이 증가하는 것을 의미하는데, 현재 하드웨어적으로 클럭의 한계가 4GHz로 파이프라인의 깊이의 증가는 제약이 있고, 깊이가 증가함에따라 클록 스큐 현상에 민감해지고 클럭 속도가 빨라지면서 발열등의 문제가 있다. 또한 컨트롤 해저드 처리시 실패 패널티 부담이 커지는 단점이 있다.

 2. load word execution이 있다. 이 프로그램이 가장 오랫동안 실행될 경우에 대해서
 TLB, page table, cache, memory 등의 과정을 작성할 것\
load는 메모리의 데이터를 레지스터로 읽어오는 instruction으로 가장 오랫동안 실행되는 경우는 다음과같다. cpu가 virtual address를 mmu에 보내면 mmu 내부의 Translation Lookaside Buffer(TLB)에 접근하여 해당 가상 주소의에 대한 페이지 테이블 엔트리가 있는지 확인 -> tlb miss 발생 -> 페이지 테이블에서 해당하는 피지컬 어드레스 매핑을 통해 tlb 업데이트 해 주기 -> 만약 페이지 테이블에서도 miss (= page fault) -> 디스크의 swap 영역에서 페이지 어드레스 매핑 부분을 가져와서 페이지 테이블 업데이트 해 주고, tlb 도 이때 업데이트, -> 피지컬 어드레스를 통해 캐시에 접근,-> cache miss -> 메모리에서 해당주소에 있는 데이터 가져오기 -> cpu의 레지스테에 가져온 데이터 업데이트

 3. cache size 512KB, cache block size 8Byte, 8-way set associative mapped
 cache를 그리고
 tag bit, index bit를 구하시오.
512KB : 2^9*2^10 
index bit : 19 - 3 - 3 = 13
offset bit : 3
tag bit : 메모리 블록 개수가 2^m개로 가정했을때, m-13 

 4. control hazard를 처리하는 테크닉에는 여러가지가 있다. 3가지 서로다른 방법을 제시하고 설명하라.

Control hazard는 다음에 실행할 명령어가 결정되지 않거나 준비되지 않아 발생하는 문제로서 주로 branch에 의해 발생된다. 이를 해결하기 위한 방법은 다음과 같다.

1. optimized branch processing
   다음 instruction의 결정을 두 사이클안에 끝내는 방법으로서, branch 조건을 간소화 하는 방법으로 구현을 간단하게 하고 branch target address를 초기에 계산하는 방식으로 adder와 같은 추가적이 하드웨어로 해결하는 방법을 의미한다.

2. branch prediction
   branch의 분기 여부를 예측함으로써 branch 명령어 다음에 수행될 명령어를 미리 파악하는 방법으로 예측을 한가지로 설정하는 static branch prediction 방법과 런타임때 branch의 기록을 이용한 dynamic branch prediction이 있다.

3. delayed branch
   delayed branch는 branch 명령어 다음에 branch 결과와 관련 없는 하나 이상의 명령어를 재배치함으로써 branch hazard에 대한 영향을 줄이는 기법을 말함.

 2016-2 (김지홍 교수님)

 1. Radix Sort, Quicksort 에서 Clock cycle, Instruction 그래프 보고 원인 찾고, Radix
 Sort 에서 개선책

 2. 8 Way Set Associate Cache에서 전체 Cache Size는 1024 byte, Byte addressinng,
 Cache Block은 8 Byte. Cache Organization 그려라. 24bit Addressing에서 Cache Tag,
 Cache Index 는 24 bit 중에 얼마나 사용할 수 있나?
cache size = 2^10
cache block = 2^3 —> # of cache = 2^7
index = 7-3 = 4bit
offset = 3bit
tag = 17 bit

 3. Pipeline Depth 깊어질 수도록 Performance가 어떻게 되나? 왜 그렇게 되는지 밝혀라.

 4. Hazard Detection Unit, Forwarding Unit 각각 역할을 설명하고, MIPS Code Segment 써라.


Forwarding unit은 이전 명령어의 rd값과 다음 명령어의 rs, rt를 비교하여 포워딩의 여부를 결정함. 즉, 데이터 해저드와 같이 데이터 의존성이 있는 경우를 확인하여 연산의 결과를 마지막단계가 아닌 결과가 나오는 시점에서 미리 가져와 사용할 수 있게 해주는 것을 말한다.
그러나 이전 명령어가 lw인 경우에는 Hazard detection unit이 필요하다. 이 유닛은 ID 단계에서 동작하여 로드 명령어와 결과 값 사용 사이에 stall을 추가할 수 있도록 한다.
( 우선, control로 부터 명령어가 load 명령어인지 확인하고 EX단계에 있는 load 명령어의 rd값과 ID 단계에 있는 rs,rt 값이랑 같은지 확인함, 두 조건이 충족되면 한 클럭 사이클만큼 지연시밐. 이때,  ID 단계를 지연시킨다면 그 앞 단계인 IF 단계도 지연시켜야 하므로, control을 통해 0의 값의 신호를 보내고, PC와 ID/IF의 값을 업데이트하지 못하게함. )
( 포워딩을 통해서 결과가 나온시점에 곧장 다음 사이클 ALU 입력에 집어넣음.
