---
layout: article
title:  "커멘드라인 개발환경 팁"
date:   2017-9-20 10:00:00 Z
author: Rocky Lim
categories: development
excerpt: "Tips for vim, tmux, ctags, cscope, etc."
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
* `:tabnew [file path]` 탭생성
* gt, gT 탭 간 이동

# Tips


## 헤더 파일 바로 읽어 오기
#include <linux/kernel.h> <- 헤더파일 이름에 커서를 위치 한후  `Ctrl + wf`를 누르면 창이 수평 분할되어 헤더파일이 열립니다


## [찾고 싶은 글자 찾기]
찾으려는 문자열에 커서를 두고 #을 누른다. 검색 결과를 왔다갔다 하려면, n또는 N으로 이동 할 수 있다.

# ctags

## 설치
```bash
sudo apt-get install ctags
```

## 시작
분석하려는 소스코드 최상위 디렉토리에서
```bash
ctags -R .
```

## 단축키

* `ctrl + ]` : 해당 함수나 변수의 정의 된 부분으로 이동
* `ctrl + t` : 이동하기 전으로 이동
* `:tags` : 명령어 모드에서 "tags"를 입력하면 현재 tags의 stack구조를 볼 수 있다.
* ctag는 앞의 두 단축키를 통해 c코드들의 호출 구조 또는 정의 구조를 따라 코드를 surfing할 수 있으며, 각각의 이동은 stack에 push, pop하는 구조로 구현되어 있다.
* `:tj` :  심볼 이름(함수, 변수명 등) 입력하면 찾고자하는 정보들이 나타난다.
* `:sts` : tj와 흡사하나, 새창에 관련 정보들이 나타난다.


# cscope


## 설치 및 편한 사용
`sudo apt-get install cscope` command를 통해 설치가 가능하다.

`mycscope.sh`와 같은 쉘 스크립트를 만들고 /usr/bin과 같은 디렉토리(맥의 경우 local/bin 이었던 것 같음.)에 복사 해 두면 편하게 사용 가능하다.

`mycscope.sh`의 내용은 다음과 같음.

```bash
#!/bin/sh
rm -rf cscope.files cscope.files
find . \( -name ‘*.c’ -o -name ‘*.cpp’ -o -name ‘*.cc’ -o -name ‘*.h’ -o -name ‘*.s’ -o -name ‘*.S’ \) -print>cscope.files
cscope -i cscope.files
```

## cscope with vim

vim에서 편리하게 cscope를 사용하기 위해 .vimrc 파일에 다음과 같은 내용을 추가한다.

```bash
set csprg=/usr/bin/cscope

set csto=0 “(숫자 0)
set cst
set nocsverb

if filereadable(“./cscope.out”)
cs add cscope.out
else
cs add /usr/src/linux/cscope.out
endif
set csverb
```


## 명령어

vim에서 cscope를 사용하기 위해 명령어 모드(:)에서 다음과 같은 명령어를 통해 사용이 가능하다.

```bash
:cs find {질의종류} {symbol_name}
ex) cs find s main
```

* `0 or s` : symbol_name 중 검색 (Cntl-‘' + s)<br />
* `1 or g` : symbol_name의 정의를 검색 (Cntl-‘' + g)<br />
* `2 or d` : symbol_name에 해당하는 함수에서 호출된 함수를 검색 (Cntl-‘' + d)<br />
* `3 or c` : symbol_name에 해당하는 함수를 호출하는 함수를 검색 (Cntl-‘' + c)<br />
* `4 or t` : symbol_name에 해당하는 text문자열을 검색 (Cntl-‘' + t)<br />
* `6 or e` : 확장 정규식을 사용하여 symbol_name을 검색 (Cntl-‘' + e)<br />
* `7 or f` : 파일 이름중에서 symbol_name을 검색 (Cntl-‘' + f)<br />
* `8 or i` : symbol_name을 include하는 파일을 검색 (Cntl-‘' + i)<br />

참고 - <http://hochulshin.com/tool-vi-ctags-cscope-on-osx/> 

# tmux

ssh원격 접속시 세션이 끊기면 사용하던 job들도 종료가 되는 것을 방지함 = 개꿀

## tmux 구성

* session : tmux 실행 단위. 여러개의 window로 구성.
* window : 터미널 화면. 세션 내에서 탭처럼 사용할 수 있음.
* pane : 하나의 window 내에서 화면 분할.
* status bar : 화면 아래 표시되는 상태 막대.

## 명령어

tmux는 prefix 키인 `ctrl+b`를 누른 후 다음 명령 키를 눌러야 동작할 수 있다.

### Session
```sh
# 새 세션 생성
$ tmux new -s <session-name>

# 세션 이름 수정
ctrl + b, $

# 세션 종료
$ (tmux에서) exit

# 세션 중단하기 (detached)
ctrl + b, d

# 세션 목록 보기 (list-session)
$ tmux ls

# 세션 다시 시작
$ tmux attach -t <session-number or session-name>
```

### Window
```sh
# 새 윈도우 생성
ctrl + b, c

# 세션 생성시 윈도우랑 같이 생성
$ tmux new -s <session-name> -n <window-name>

# 윈도우 이름 수정
ctrl + b, ,

# 윈도우 종료
ctrl + b, &
ctrl + d

# 윈도우 이동
ctrl + b, 0-9 : window number
n : next window
p : prev window
l : last window
w : window selector
f : find by name
```

### Pane

```
# 틀 나누기
ctrl + b, % : 횡 분할
          " : 종 분할

# 틀 이동
ctrl + b, q 그리고 화면에 나오는 숫자키
ctrl + b, o : 순서대로 이동
ctrl + b, arrow : 방향키로 숑숑

# 틀 삭제
ctrl + b, x
ctrl + d

# 틀 사이즈 조절
(ctrl + b, :)
resize-pane -L 10
-R 10
-D 10
-U 10

# 틀 레이아웃 변경
ctrl + b, spacebar
```

### Shortcut key

```sh
# 단축키 목록
ctrl + b, ?

# 키 연결 및 해제 bind and unbind
(ctrl + b, :)
bind-key [-cnr] [-t key-table] key command [arguments]
unbind-key [-acn] [t key-table] key

# 옵션 설정 `set` and `setw`
set -g <option-name> <option-value>  : set-option
setw -g <option-name> <option-value> : set-window-option
```

### Code Mode

```sh
# copy mode 진입
ctrl + b, [

# 빠져나오기
(copy mode에서) q or ESC

# 이동
arrow : 커서 이동
pageUp, pageDown : 페이지 이동 (iTerm에서는 fn + up, down, terminal에서는 alt + up, down)
```


