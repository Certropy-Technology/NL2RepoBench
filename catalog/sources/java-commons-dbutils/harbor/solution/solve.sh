#!/usr/bin/env bash
set -euo pipefail

# The parent integrator places source.tar beside this script in the private
# Oracle bundle. Only the frozen main sources are copied into the candidate
# workspace; upstream tests and build configuration remain private.
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java
cp -a "$tmp/src/main/java/." /workspace/src/main/java/
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.commons</groupId>
  <artifactId>commons-dbutils</artifactId>
  <version>1.8.1</version>
  <packaging>jar</packaging>
</project>
POM
