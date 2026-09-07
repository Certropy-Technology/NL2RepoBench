#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -xf "$root/source.tar" -C "$tmp"
mkdir -p /workspace/src/main/java/io/github/classgraph/viz /workspace/src/main/java/org/jspecify/annotations
cp "$tmp/classgraph-viz/src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java" \
  /workspace/src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java
cat > /workspace/src/main/java/org/jspecify/annotations/Nullable.java <<'JAVA'
package org.jspecify.annotations;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
@Retention(RetentionPolicy.CLASS)
@Target({ElementType.TYPE_USE, ElementType.TYPE_PARAMETER})
public @interface Nullable {}
JAVA
cat > /workspace/pom.xml <<'POM'
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>io.github.classgraph</groupId><artifactId>classgraph-options-contract</artifactId><version>1.0.0</version>
</project>
POM
