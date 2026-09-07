#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/bcel/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/bcel/util/ByteSequence.java <<'JAVA'
package org.apache.bcel.util;
public final class ByteSequence extends java.io.DataInputStream {
    public ByteSequence(byte[] bytes) { super(new java.io.ByteArrayInputStream(new byte[0])); }
    public int getIndex() { return 0; }
}
JAVA
