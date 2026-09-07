#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/codec/binary
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version><packaging>jar</packaging></project>' > pom.xml
cat > src/main/java/org/apache/commons/codec/binary/Base64.java <<'JAVA'
package org.apache.commons.codec.binary;
public final class Base64 {
    public static String encodeBase64String(byte[] value) { return "stub"; }
    public static byte[] decodeBase64(String value) { return new byte[0]; }
}
JAVA
cat > src/main/java/org/apache/commons/codec/binary/Hex.java <<'JAVA'
package org.apache.commons.codec.binary;
public final class Hex {
    public static String encodeHexString(byte[] value) { return "stub"; }
}
JAVA
