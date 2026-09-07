#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/apache/commons/text/similarity
cat > /workspace/pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>commons-text</artifactId><version>1.0.0</version></project>
XML
cat > /workspace/src/main/java/org/apache/commons/text/similarity/HammingDistance.java <<'JAVA'
package org.apache.commons.text.similarity;

public class HammingDistance {
    public HammingDistance() {}
    public Integer apply(final CharSequence left, final CharSequence right) {
        if (left == null || right == null || left.length() != right.length()) {
            throw new IllegalArgumentException("Inputs must be non-null and have equal length");
        }
        int distance = 0;
        for (int index = 0; index < left.length(); index++) {
            if (left.charAt(index) != right.charAt(index)) distance++;
        }
        return distance;
    }
}
JAVA
