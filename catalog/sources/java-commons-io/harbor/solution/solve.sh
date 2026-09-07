#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [[ -f "$root/source.tar" ]]; then
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  tar -xf "$root/source.tar" -C "$tmp"
  mkdir -p /workspace/src/main/java/org/apache/commons/io
  cp "$tmp/src/main/java/org/apache/commons/io/EndianUtils.java" /workspace/src/main/java/org/apache/commons/io/
  cat > /workspace/src/main/java/org/apache/commons/io/IOUtils.java <<'JAVA'
package org.apache.commons.io;
public final class IOUtils {
    public static final int EOF = -1;
    private IOUtils() {}
}
JAVA
fi
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.commons</groupId>
  <artifactId>commons-io</artifactId>
  <version>2.23.0</version>
</project>
POM
