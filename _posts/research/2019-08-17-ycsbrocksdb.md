---
layout: article
title:  "YCSB benchmark for modified RocksDB(not for YCSB's default version)"
date:   2019-08-17 10:00:00 Z
author: generousRocky
categories: research
excerpt: "코드를 수정한 RocksDB 버전에 YCSB 벤치마크 돌리기"
image:
  feature:
  teaser: ycsbrocksdb1.png
  path: images/ycsbrocksdb1.png
comments: true
locale: "vn"
share: true
ads: false
---


{% include toc.html %}


facebook에서 배포하는 RocksDB버전을 수정 없이 그대로 성능평가하기 위해서는 그냥 YCSB의 [README](https://github.com/brianfrankcooper/YCSB/blob/master/rocksdb/README.md) 문서를 참고하면 된다. Maven이 알아서 RocksDB 패키지도 받아서 YCSB를 돌려볼 수 있다.

하지만 RocksDB의 코드를 고쳐서 내가 수정한 버전의 RocksDB의 성능을 평가하려면 RocksDB를 JAVA로 빌드하여 jni package를 만든 다음 그 패키지를 사용하여 YCSB를 동작시켜야 한다.

나의 경우 Open-Channel SSD를 RocksDB의 스토리지로 사용하기 위해 RocksDB 스토리지 백엔드를 posix i/o 가 아닌 외부 라이브러리(liblightnvm)을 사용하여 새로운 백엔드를 사용하도록 고쳤고, 앞으로 설명할 내용 외에도 jin function을 몇가지 직접 만드는 추가적인 작업이 필요했다. 하지만 일반적인 코드 수정이나 알고리즘적인 수정의 경우 본 글의 instruction이면 충분할 것 같다.

# RocksDB jni package generation

일단 어떤 버전을 어떻게 수정하였던 정상적으로 동작하는 RocksDB의 소스코드가 필요하다. 다음으로 넘어가기 전에 내가 가지고 있는 RocksDB 소스코드를 `make release` 해서 `db_bench`가 정상적으로 돌아가는지 확인 해 보자.

내가 수정한 버전의 RocksDB가 정상적으로 동작한다면, RocksDB를 JAVA compile해야한다.


RocsDB 소스코드에서 java 디렉토리는 jni package와 관련이 있다. compression method는 5가지를 모두 사용하지는 않으므로 필요한 것만 남기고 주석처리로 없애준다(시간 절약을 위해).

* 다음 예시와 같이 Makefile을 수정한다(snappy compression만 남김).

```make
# A version of each $(LIBOBJECTS) compiled with -fPIC and a fixed set of static compression libraries
java_static_libobjects = $(patsubst %,jls/%,$(LIBOBJECTS))
CLEAN_FILES += jls

ifneq ($(ROCKSDB_JAVA_NO_COMPRESSION), 1)
# JAVA_COMPRESSIONS = libz.a libbz2.a libsnappy.a liblz4.a libzstd.a
JAVA_COMPRESSIONS = libsnappy.a
endif

# JAVA_STATIC_FLAGS = -DZLIB -DBZIP2 -DSNAPPY -DLZ4 -DZSTD
JAVA_STATIC_FLAGS = -DSNAPPY
# JAVA_STATIC_INCLUDES = -I./zlib-$(ZLIB_VER) -I./bzip2-$(BZIP2_VER) -I./snappy-$(SNAPPY_VER) -I./lz4-$(LZ4_VER)/lib -I./ zstd-$(ZSTD_VER)/lib
JAVA_STATIC_INCLUDES = -I./snappy-$(SNAPPY_VER)
```

java compile을 위해서는 `Makefile`의 rocksdbjavastaticrelease rule을 사용한다. cross-platform이 아니므로 해당 line은 comment out 해준다. 이 라인을 지움으로써 cross-platform java package를 취소하였으므로, `ibrocksdbjni-*.jnilib`부분을 지워준다.

* 결과적으로 다음 예시와 같이 Makefile을 수정한다. 

```make
rocksdbjavastaticrelease: rocksdbjavastatic
  # cd java/crossbuild && vagrant destroy -f && vagrant up linux32 && vagrant halt linux32 && vagrant up linux64 && vagrant halt linux64
  cd java;jar -cf target/$(ROCKSDB_JAR_ALL) HISTORY*.md
  # cd java/target;jar -uf $(ROCKSDB_JAR_ALL) librocksdbjni-*.so librocksdbjni-*.jnilib
  cd java/target;jar -uf $(ROCKSDB_JAR_ALL) librocksdbjni-*.so
  cd java/target/classes;jar -uf ../$(ROCKSDB_JAR_ALL) org/rocksdb/*.class org/rocksdb/util/*.class
```

정상적으로 Makefile을 수정하였다면, `make rocksdbjavastaticrelease` 명령어를 통해 빌드를 해 보자. 만약 코어가 충분하다면 `-j16` 과 같은 옵션을 줄 수 있다.

성공적으로 빌드가 된다면, `rocksdb/java/target/rocksdbjni-5.18.3.jar`와 같이 jni package 파일이 생성될 것이다. 여기서 `5.18.3`과 같은 버전은 작업하는 RocksDB의 소스코드에 따라 다르게 생성 될 것이다.

이렇게 생성된 jni package는 이후 YCSB 동작에서 사용된다.

# YCSB compilation
## get YCSB code and configuation
다음과 같은 명령어를 통해 YCSB 코드를 받는다

```sh
git clone https://github.com/brianfrankcooper/YCSB.git
git checkout 0.15.0
```

YCSB의 code modle dependency들을 다운로드하기 위해 `YCSB/core/pom.xml` 파일에서 `<dependencies>` 하위 부분에 다음과 같은 내용을 추가한다.

```xml
<dependency>
      <groupId>org.apache.htrace</groupId>
      <artifactId>htrace-core4</artifactId>
      <version>4.1.0-incubating</version>
</dependency>
<dependency>
      <groupId>org.hdrhistogram</groupId>
      <artifactId>HdrHistogram</artifactId>
      <version>2.1.4</version>
</dependency>
```


## YCSB compilation

Maven을 통해 RocksDB 를 바인딩 한다. 주의할 점은 단순히`mvm clean package`명령어를 사용하면 모든 데이터베이스 어플리케이션(HBase, MongoDB 등등)의 모듈을 위한 dependency들을 다운로드 하기 때문에 시간이 매우 오래 걸린다.

* 다음 명령어는 RocksDB를 바인딩 하기위한 명령어 이다.

```sh
mvn -pl com.yahoo.ycsb:rocksdb-binding -am clean package
```

dependency 추가로 인해 `YCSB/rocksdb/target/dependency/` 경로에 `htrace-core4-4.1.0-incubating.jar` `HdrHistogram-2.1.4.jar` 파일이 생성되어 있는것을 확인할 수 있다.

YCSB 디렉토리의 *YCSB/pom.xml* 파일에서 `<rocksdb.version>5.11.3</rocksdb.version>`부분을 보면, YCSB가 RocksDB의 5.11.3 버전의 jni package를 다운로드 받아 사용한다는 것을 알 수 있다. 이 부분을 수정하면 원하는 버전의 jni package를 받아 YCSB를 돌려볼 수 있다. (하지만 여전히 facebook에서 배포한 버전 그대로이다. 우리가 원하는 것은 직접 소스코드를 수정하여 빌드한 RocksDB의 성능을 평가하고싶은것이다.)

리눅스 시스템에서는 `bin/ycsb.sh` 파일을 실행하여 여러가지 YCSB 벤치마크를 조작할 수 있다. 

* 다음 명령어를 통해 YCSB-workloada의 데이터를 로드 해 본다. workloada에 대한 configuration은 `workloads/workloada` 파일에 명세되어 있으며, 데이터가 저장될 디렉토리도 함께 옵션으로 준다.

```sh
bin/ycsb.sh load rocksdb -s -P workloads/workloada -p rocksdb.dir=/home/rocky/ycsbdata
```

LOG파일을 앞 부분을 확인해 보면 아직 YCSB의 디폴트 버전인 5.11.3 버전의 RocksDB가 동작하고 있음을 확인할 수 있다.

**(중요!) 이전 과정에서 생성된 jni package 파일인 `rocksdb/java/target/rocksdbjni-5.18.3.jar` 을 `YCSB/rocksdb/target/dependency/` 경로에 복사한다. 그리고 기존의 `rocksdbjni-5.11.3.jar` 파일은 삭제한다.**

이후 RocksDB 데이터 경로인 `rocsdb.dir`에 지정 해 주었던 디렉토리 경로의 파일들을 모두 지우고 다시 laod 명령을 해 본다.

```sh
bin/ycsb.sh load rocksdb -s -P workloads/workloada -p rocksdb.dir=/home/rocky/ycsbdata
```

LOG파일의 앞 부분을 보면 원하는 버전의(내가 코드를 고치고 빌드한 버전의) RocksDB가 나타난 것을 확인할 수 있다.

데이터를 load한 이후에는 여러 workload들을 돌려 성능 평가를 해볼수 있다.

* 다음 명령어는 `home/rocky/ycsbdata` 디렉토리에 존재하는 데이터베이스에 workload-a를 수행한다.

```sh
bin/ycsb.sh run rocksdb -s -P workloads/workloada -p rocksdb.dir=/home/rocky/ycsbdata
```

## parameter settings under YCSB

workload들의 default configuration은 Fieldcount와 Filelength가 작아 매우 짧은시간 내에 끝나버리니 충분한 크기로 변경 해 주어야한다. 각 workload 의 parameter는 `YCSB/worklaods/` 경로의 파일들을 수정해 변경할 수 있다.

RocksDB의 여러 parameter및 configuration은 `YCSB\rocksdb\src\main\java\com\yahoo\ycsb\db\rocksdb\RocksDBClient.java` 파일에서 설정 해 줄 수 있다.

`initRocksDB()` 함수 아래 위치한 다음의 코드들은 RocksDB의 option들과 관련된 부분이다. RocksDB 소스코드에서 `java/src/main/java/org/rocksdb/Options.java` 파일과 `java/src/main/java/org/rocksdb/DBOptions.java` 파일에서 함수의 원형을 참고하여 option을 변경하는 함수를 찾아 원하는 옵션을 변경한다.

```java
    if(cfDescriptors.isEmpty()) {
      final Options options = new Options()
          .optimizeLevelStyleCompaction()
          .setCreateIfMissing(true)
          .setCreateMissingColumnFamilies(true)
          .setIncreaseParallelism(rocksThreads)
          .setMaxBackgroundCompactions(rocksThreads)
          .setInfoLogLevel(InfoLogLevel.INFO_LEVEL);
      dbOptions = options;
      return RocksDB.open(options, rocksDbDir.toAbsolutePath().toString());
    } else {
      final DBOptions options = new DBOptions()
          .setCreateIfMissing(true)
          .setCreateMissingColumnFamilies(true)
          .setIncreaseParallelism(rocksThreads)
          .setMaxBackgroundCompactions(rocksThreads)
          .setInfoLogLevel(InfoLogLevel.INFO_LEVEL);
      dbOptions = options;

      final List<ColumnFamilyHandle> cfHandles = new ArrayList<>();
      final RocksDB db = RocksDB.open(options, rocksDbDir.toAbsolutePath().toString(), cfDescriptors, cfHandles);
      for(int i = 0; i < cfNames.size(); i++) {
        COLUMN_FAMILIES.put(cfNames.get(i), new ColumnFamily(cfHandles.get(i), cfOptionss.get(i)));
      }
      return db;
    }
```

만약 `RocksDBClient.java` 파일을 수정하였다면 아래 커멘드를 입력하여 다시 바인딩을 한다.(`mvn -pl com.yahoo.ycsb:rocksdb-binding -am clean package` 커멘드에서 `clean`이 빠졌음.)

```sh
mvn -pl com.yahoo.ycsb:rocksdb-binding -am package
```

이후 다시 생성된 `rocksdb/java/target/rocksdbjni-5.11.3.jar` 파일을 삭제한다.
`load`나 `run` 커멘드를 실행하면, 원하는 옵션으로 RocksDB가 동작하는것을 확인활 수 있을것이다.
