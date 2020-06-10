---
layout: article
title: "Linux System Programming [2]: File Input/Output"
date: 2017-07-29 13:44:20 Z
author: Rocky Lim
categories: book
excerpt: "리눅스 시스템 프로그래밍 [2]: 파일 입출력"
image:
  feature:
  teaser: lsp2.png
  path: /images/lsp2.png
comments: true
locale: "vn"
share: true
ads: true
---


<p style="text-align: center;">
	<img src="{{ site.url }}/images/lsp.gif" alt="Drawing" style="width: 380px;"/>
</p>

{% include toc.html %}

## 파일 입출력
파일은 읽거나 쓰기전에 반드시 열려있어야 한다. 커널은 파일 테이블이라고 하는, 프로세스별로 열린 파일 목록을 관리한다. 이 테이블은 음이 아닌 정수 값인, 파일 디스크립터(fd)로 인덱싱 되어 있다. 이 테이블의 각 항목은 열린 파일에 대한 정보(inode, 메타데이터)를 갖고있다.
프로세스는 3가지 파일 디스크립터(fd)를 기본적으로 가지고 있다. 이는 0(stdin), 1(stdout), 3(stderr) 이다.
즉, 파일 디스크립터는 단순히 일반 파일만을 나타내는 것이 아니라, 장치파일, 파이프, 디렉토리, 뮤텍스, FIFO, 소켓 접근에도 사용되며 "모든 것이 파일이다."라는 유니그 철학에 따라 읽고 쓸 수 있는 모든 것은 파일디스크립터로서 접근할 수 있다.

### 파일 열기
파일에 접근하는 가장 기본적인 방법은 read() 시스템 콜과 write()시스템 콜 이다. 물론 이에 앞서 open()이나 create()시스템콜을 사용하여 파일을 열어줘야 하고, 접근이 끝난 뒤에는 close()로 파일을 닫아주어야 한다.

* open() 시스템 콜

~~~ c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int open(const char *name, int flags);
int open(const char *name, int flags, mode_t mode);
~~~
open() 시스템 콜은 경로 이름이 name인 파일을 파일 디스크립터에 mapping 하고, 성공하면 이 파일 디스크립터를 반환한다. 파일 오프셋은 파일의 시작시점인 0으로 설정되며, 파일은 flags로 지정한 플래그에 대응하는 접근 모드로 열리게 된다.

* open()시스템 콜 access flag

flags parameter는 O_RDONLY, O_WRONLY, O_RDWR 중 하나를 포함해야 한다. 다음과 같은 코드는 읽기 전용 모드(O_RDONLY)로 파일을 열도록 요청한다.

~~~ c
int myFd

myFd = open("home/rocky/Document/foo.txt", O_RDONLY);
if (myFd == -1)
  /*
  ERROR
  */
~~~

다음과 같이 flags parameter에 비트 OR 연산을 통해 새로운 flag를 추가해서 열기 동작을 변경할 수 있다.

~~~ c
int myFd

myFd = open("home/rocky/Document/foo.txt", O_WRONLY | O_TRUNC);
if (myFd == -1)
  /*
  ERROR
  */
~~~
위 코드에서는 foo.txt파일을 쓰기모드로 연다. 파일이 이미 존재하면 길이를 0으로 잘라버린다. O_CREATE flag를 명시하지 않았기 때문에 파일이 존재하지 않으면 호출은 실패한다.

상세한 flag들과 description은 다음 링크를 참고하자.<br />
<http://man7.org/linux/man-pages/man2/open.2.html>

### 파일 생성
새로운 파일의 소유자는 그 파일을 생성한 프로세스의 uid를 따른다. 또한 새로운 파일의 그룹 역시 그 파일을 생성한 그룹의 gid를 따른다. 일부 리눅스 시스템에서는 다르게 동작하기도 하지만 흔치 않다.

새로운 파일이 생성되면 만들어진 파일의 접근 권한은 mode parameter에 따라 설정된다. mode parameter는 시스템 관리자에게는 낮익은 유닉스 접근권한 비트 집합이며 8진수 이다. 예를들어 접근권한 "0664"는 소유자는 읽기 쓰기가 가능하고, 나머지 모든 사용자는 읽기만 가능하다.  

~~~ c
int myFd

myFd = open("home/rocky/Document/foo.txt", O_WRONLY | O_CREATE | O_TRUNC, 0664 );
if (myFd == -1)
  /*
  ERROR
  */
~~~
위의 예제 코드는 쓰기 모드로 foo.txt파일을 연다. 파일이 존재하지 않는다면 접근권한이 0644인 파일을 생선한다. 그리고 파일이 존재하면 길이를 0으로 잘라버린다.

* creat()함수

O_WRONLY | O_CREATE | O_TRUNC 조합을 통해 파일을 생성하는 것은 너무나도 일반적인 경우여서 이러한 방식을 지원하는 시스템 콜로서 다음과 같은 함수가 존재한다.

~~~ c
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int creat(const char *name, mode_t mode);
~~~

** create가 아니라 creat이다, 유닉스 설계자의 인간적인 실수로 아직도 남아있다.
~~~ c
int myFd

myFd = open("home/rocky/Document/foo.txt", 0664);
if (myFd == -1)
  /*
  ERROR
  */
~~~
위와 같은 코드로 foo.txt라는 파일을 생성할 수 있다.

open()시스템 콜과 creat()시스템 콜은 성공하면 파일 디스크립터를 반환하고 실패할 경우 -1을 반환한다. 또한 적절한 값으로 errno 변수를 설정 해 준다.

This is a work in progress.
