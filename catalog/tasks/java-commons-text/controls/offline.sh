#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/text/similarity
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/text/similarity/HammingDistance.java <<'JAVA'
package org.apache.commons.text.similarity;
public class HammingDistance {
    public HammingDistance() {}
    public Integer apply(final CharSequence left, final CharSequence right) {
        if (left == null || right == null || left.length() != right.length()) throw new IllegalArgumentException();
        int result = 0;
        for (int i = 0; i < left.length(); i++) if (left.charAt(i) != right.charAt(i)) result++;
        return result;
    }
}
JAVA
