#!/usr/bin/env bash
set -euo pipefail
bundle_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
mkdir -p /workspace/src/main/java/org/apache/commons/logging/impl /workspace/src/main/java/org/apache/commons/logging
cp "$bundle_dir/source/NoOpLog.java" /workspace/src/main/java/org/apache/commons/logging/impl/
cp "$bundle_dir/source/Log.java" /workspace/src/main/java/org/apache/commons/logging/
printf '%s\n' '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>org.apache.commons</groupId><artifactId>commons-logging</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > /workspace/pom.xml
