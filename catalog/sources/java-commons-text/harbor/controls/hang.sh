#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/text/similarity
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/text/similarity/HammingDistance.java <<'JAVA'
package org.apache.commons.text.similarity;
public class HammingDistance {
    public HammingDistance() {}
    public Integer apply(CharSequence left, CharSequence right) { while (true) Thread.yield(); }
}
JAVA
