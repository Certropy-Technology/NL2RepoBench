#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/io/github/classgraph/viz
cat > /workspace/src/main/java/io/github/classgraph/viz/GraphVizDotFileOptions.java <<'JAVA'
package io.github.classgraph.viz;
public final class GraphVizDotFileOptions {
 public GraphVizDotFileOptions(){while(true){try{Thread.sleep(1000);}catch(InterruptedException ignored){}}}
}
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>
POM
