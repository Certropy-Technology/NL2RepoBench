#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/apache/bcel/util
cat > /workspace/src/main/java/org/apache/bcel/util/ByteSequence.java <<'JAVA'
package org.apache.bcel.util;

import java.io.ByteArrayInputStream;
import java.io.DataInputStream;

public final class ByteSequence extends DataInputStream {
    private static final class ByteArrayStream extends ByteArrayInputStream {
        ByteArrayStream(byte[] bytes) { super(bytes); }
        int position() { return pos; }
    }
    private final ByteArrayStream byteStream;
    public ByteSequence(byte[] bytes) {
        super(new ByteArrayStream(bytes));
        byteStream = (ByteArrayStream) in;
    }
    public int getIndex() { return byteStream.position(); }
}
JAVA
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd"><modelVersion>4.0.0</modelVersion><groupId>org.apache.bcel</groupId><artifactId>bcel</artifactId><version>6.13.0</version><packaging>jar</packaging></project>
XML
