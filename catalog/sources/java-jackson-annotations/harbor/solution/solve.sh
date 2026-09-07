#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/com/fasterxml/jackson/annotation
cp "$tmp/src/main/java/com/fasterxml/jackson/annotation/JsonCreator.java" /workspace/src/main/java/com/fasterxml/jackson/annotation/
cp "$tmp/src/main/java/com/fasterxml/jackson/annotation/JacksonAnnotation.java" /workspace/src/main/java/com/fasterxml/jackson/annotation/
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.fasterxml.jackson.core</groupId>
  <artifactId>jackson-annotations</artifactId>
  <version>2.23.0</version>
</project>
POM
