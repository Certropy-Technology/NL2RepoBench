#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/bcel/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/bcel/util/ByteSequence.java <<'JAVA'
package org.apache.bcel.util;
import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
public final class ByteSequence extends DataInputStream {
    private static final class Bytes extends ByteArrayInputStream {
        Bytes(byte[] value) { super(value); }
        int position() { return pos; }
    }
    private final Bytes bytes;
    public ByteSequence(byte[] value) { this(new Bytes(value)); }
    private ByteSequence(Bytes value) { super(value); bytes = value; }
    public int getIndex() { return bytes.position(); }
}
JAVA
