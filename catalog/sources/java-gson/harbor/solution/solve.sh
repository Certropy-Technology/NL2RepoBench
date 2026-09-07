#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/com/google/gson /workspace/src/main/java/com/google/gson/annotations
cp "$tmp/gson/src/main/java/com/google/gson/FieldNamingPolicy.java" /workspace/src/main/java/com/google/gson/
cp "$tmp/gson/src/main/java/com/google/gson/FieldNamingStrategy.java" /workspace/src/main/java/com/google/gson/
cp "$tmp/gson/src/main/java/com/google/gson/annotations/SerializedName.java" /workspace/src/main/java/com/google/gson/annotations/
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.code.gson</groupId><artifactId>gson-slice</artifactId><version>2.14.1</version>
</project>
POM
