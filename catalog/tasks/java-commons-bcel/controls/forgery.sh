#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/bcel/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>forgery</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/bcel/util/ByteSequence.java <<'JAVA'
package org.apache.bcel.util;
public final class ByteSequence extends java.io.DataInputStream {
    public ByteSequence(byte[] bytes) { super(new java.io.ByteArrayInputStream(bytes)); }
    public int getIndex() { return 999; }
}
JAVA
