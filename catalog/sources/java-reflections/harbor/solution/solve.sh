#!/usr/bin/env bash
set -euo pipefail

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
test -f "$tmp/src/main/java/org/reflections/util/FilterBuilder.java"
test -f "$tmp/src/main/java/org/reflections/ReflectionsException.java"
mkdir -p /workspace/src/main/java/org/reflections/util /workspace/src/main/java/org/reflections
cp "$tmp/src/main/java/org/reflections/util/FilterBuilder.java" /workspace/src/main/java/org/reflections/util/
cp "$tmp/src/main/java/org/reflections/ReflectionsException.java" /workspace/src/main/java/org/reflections/
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>org.reflections</groupId><artifactId>reflections</artifactId><version>0.11.0</version></project>
POM
