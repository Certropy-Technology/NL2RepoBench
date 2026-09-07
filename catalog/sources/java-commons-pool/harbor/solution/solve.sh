#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
mkdir -p /workspace/src/main/java/org/apache/commons/pool3/impl /workspace/src/main/java/org/apache/commons/pool3
cp "$root/reference/org/apache/commons/pool3/PooledObjectState.java" /workspace/src/main/java/org/apache/commons/pool3/
cp "$root/reference/org/apache/commons/pool3/impl/EvictionConfig.java" /workspace/src/main/java/org/apache/commons/pool3/impl/
printf '%s\n' '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>org.apache.commons</groupId><artifactId>commons-pool3</artifactId><version>3.0.0</version></project>' > /workspace/pom.xml
