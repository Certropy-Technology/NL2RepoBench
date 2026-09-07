#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/org/apache/commons/net/util
cp "$tmp/src/main/java/org/apache/commons/net/util/SubnetUtils.java" \
  /workspace/src/main/java/org/apache/commons/net/util/SubnetUtils.java
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.commons</groupId><artifactId>commons-net</artifactId><version>3.12.0</version>
</project>
POM
