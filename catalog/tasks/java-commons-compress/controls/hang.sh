#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/compress/archivers/zip
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/compress/archivers/zip/ZipEightByteInteger.java <<'JAVA'
package org.apache.commons.compress.archivers.zip;
public final class ZipEightByteInteger {
  public ZipEightByteInteger(long value) { while (true) { Thread.yield(); } }
  public ZipEightByteInteger(java.math.BigInteger value) { while (true) { Thread.yield(); } }
  public ZipEightByteInteger(byte[] value) { while (true) { Thread.yield(); } }
  public ZipEightByteInteger(byte[] value, int offset) { while (true) { Thread.yield(); } }
  public static byte[] getBytes(long value) { while (true) { Thread.yield(); } }
  public static byte[] getBytes(java.math.BigInteger value) { while (true) { Thread.yield(); } }
  public static long getLongValue(byte[] bytes) { return 0L; }
  public static long getLongValue(byte[] bytes, int offset) { return 0L; }
  public static java.math.BigInteger getValue(byte[] bytes) { return java.math.BigInteger.ZERO; }
  public static java.math.BigInteger getValue(byte[] bytes, int offset) { return java.math.BigInteger.ZERO; }
  public byte[] getBytes() { return new byte[8]; }
  public long getLongValue() { return 0L; }
  public java.math.BigInteger getValue() { return java.math.BigInteger.ZERO; }
  public static final ZipEightByteInteger ZERO = null;
  public boolean equals(Object other) { return false; }
  public int hashCode() { return 0; }
  public String toString() { return "0"; }
}
JAVA
