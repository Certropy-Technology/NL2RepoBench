#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/io/github/classgraph/viz
printf '%s\n' 'package io.github.classgraph.viz; public final class GraphVizDotFileOptions {}' > /workspace/src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>bad</artifactId><version>1</version><dependencies><dependency><groupId>x</groupId><artifactId>y</artifactId><version>1</version></dependency></dependencies></project>
POM
