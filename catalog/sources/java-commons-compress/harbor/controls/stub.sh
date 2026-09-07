#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/compress/archivers/zip
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/compress/archivers/zip/ZipEightByteInteger.java <<'JAVA'
package org.apache.commons.compress.archivers.zip;
public final class ZipEightByteInteger {
  public static final ZipEightByteInteger ZERO = new ZipEightByteInteger(0L);
  private final long value;
  public ZipEightByteInteger(long value) { this.value = 0L; }
  public ZipEightByteInteger(java.math.BigInteger value) { this.value = 0L; }
  public ZipEightByteInteger(byte[] value) { this.value = 0L; }
  public ZipEightByteInteger(byte[] value, int offset) { this.value = 0L; }
  public byte[] getBytes() { return new byte[8]; }
  public long getLongValue() { return value; }
  public java.math.BigInteger getValue() { return java.math.BigInteger.ZERO; }
  public static byte[] getBytes(long value) { return new byte[8]; }
  public static byte[] getBytes(java.math.BigInteger value) { return new byte[8]; }
  public static long getLongValue(byte[] bytes) { return 0L; }
  public static long getLongValue(byte[] bytes, int offset) { return 0L; }
  public static java.math.BigInteger getValue(byte[] bytes) { return java.math.BigInteger.ZERO; }
  public static java.math.BigInteger getValue(byte[] bytes, int offset) { return java.math.BigInteger.ZERO; }
  public boolean equals(Object other) { return other instanceof ZipEightByteInteger; }
  public int hashCode() { return 0; }
  public String toString() { return "0"; }
}
JAVA
