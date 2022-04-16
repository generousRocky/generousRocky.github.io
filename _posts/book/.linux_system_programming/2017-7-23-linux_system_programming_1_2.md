---
layout: article
title: "Linux System Programming [1-2]: Error handling"
date: 2017-07-23 13:44:20 Z
author: Rocky Lim
categories: book
excerpt: "리눅스 시스템 프로그래밍 [1-2]: 에러처리 - errno 변수를 활용한 에러 확인 및 처리"
image:
  feature:
  teaser: lsp1_1.png
  path: /images/lsp1.png
comments: true
locale: "vn"
share: true
ads: false
---


<p style="text-align: center;">
	<img src="{{ site.url }}/images/lsp.gif" alt="Drawing" style="width: 380px;"/>
</p>

{% include toc.html %}

시스템 프로그래밍에서 에러는 함수 리턴값으로 확인이 가능하며 특수한 변수인 errno로 에러가 발생한 구체적인 이유를 알 수 있다. glibc에서는 라이브러리와 시스템 콜 양쪽을 지원하도록 errno 값을 제공한다. 정확한 값은 함수에 따라 다르겠지만 보통 에러가 발생하면 -1을 반환한다. 이 에러값은 호출한 측에 에러가 발생했음을 알려주지만, 자세한 에러 이유는 알려주지 않는다. 이때 에러의 원인을 찾아내기 위해 errno 변수를 사용한다.

* errno 변수는 <errno.h> 헤더에 다음과 같이 정의되어 있다.

~~~ c
extern int errno;
~~~
이 값은 errno에 값을 대입한 함수를 호출한 직후에만 유효하다. 연이어 다른 함수를 실행하면 이 값이 바뀌므로 주의해야 한다.

errno 변수는 직접 읽고 쓸 수 있으며, 변경 가능한 변수(Variable)이다. errno 값은 그 에러에 대한 설명이 다음과 같이  mapping되어 있다.

| 선행처리기 문자열 정의 | 설명 |
| :---: | :---: |
| EPERM | /* Operation not permitted */ |
| ENOENT | /* No such file or directory */ |
| ESRCH | /* No such process */ |
| EINTR | /* Interrupted system call */ |
| EIO | /* I/O error */ |
| ENXIO | /* No such device or address */ |
| E2BIG | /* Arg list too long */ |
| ENOEXEC | /* Exec format error */ |
| EBADF | /* Bad file number */ |
| ECHILD | /* No child processes */ |
| EAGAIN | /* Try again */ |
| ENOMEM | /* Out of memory */ |
| EACCES | /* Permission denied */ |
| EFAULT | /* Bad address */ |
| ENOTBLK | /* Block device required */ |
| EBUSY | /* Device or resource busy */ |
| EEXIST | /* File exists */ |
| EXDEV | /* Cross-device link */ |
| ... | ... |

C 라이브러리에는 errno 값을 그에 맞는 문자열 표현으로 변환하는 함수를 몇 가지 제공하고 있다. 이런 함수는 사용자에게 에러를 알려줄 때 사용한다.

* perror() 함수

~~~ c
#include <stdio.h>
void perror (const char *str)
~~~
이 함수는 str이 가르키는 문자열 뒤에 콜론(:)을 붙인 다음에 errno가 기술하는 현재 에러를 문자열로 바꿔 표준 에러(stderr: standard error)로 내보낸다. 활용도를 높이려면 다음과 같이 함수 이름을 문자열에 포함 해 주면 좋다.
~~~ c
if(close(fd) == -1)
  perror("close");
~~~

* strerror()와 strerror_r()함수

~~~ c
#include <string.h>
char * strerror(int errnum);
~~~
~~~ c
#include <string.h>
int strerroe_r(int errnum, char *buf, size_t len);
~~~
strerror()함수는 errno 에러에 대한 설명이 담긴 문자열 포인터를 반환한다. 비슷하게 strerror_r()함수는 buf가 가르키는 지점부터 len만큼 버퍼를 체운다.

흔히 하는 실수로, 라이브러리나 시스템 콜에서 errno 값을 바꿀 수 있다는 사실을 잊은 채 errno 값을 검사하는 경우가 있다.
~~~ c
if(fsync(fd) == -1){
  fprintf(stderr, "fsync failed!\n");
  if(errno == EIO)
    fprintf(stderr, "I/O error on %d!\n", fd);
}
~~~
위 코드에는 다음과 같이 수정되어야 한다.
~~~ c
if(fsync(fd) == -1){
  const int err = errno;
  fprintf(stderr, "fsync failed: %s\n", stderror(errno));
  if(errno == EIO){
    // I/O와 관련된 에러라면 exit
    fprintf(stderr, "I/O error on %d!\n", fd);
    exit(EXIT_FAILURE)
  }
}
~~~
싱글스레드 프로그램에서 errno는 전역변수 이지만, 멀티스레드 프로그램에서 errno는 스레드 별로 저장되므로 스레드에서 역시 사용가능하다.
