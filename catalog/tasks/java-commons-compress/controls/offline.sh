#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/commons/compress/archivers/zip
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/compress/archivers/zip/ZipEightByteInteger.java <<'JAVA'
package org.apache.commons.compress.archivers.zip;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
public final class ZipEightByteInteger {
    public static final ZipEightByteInteger ZERO = new ZipEightByteInteger(0L);
    private static final BigInteger HIGH = BigInteger.ONE.shiftLeft(63);
    private final long value;
    public ZipEightByteInteger(long value) { this.value = value; }
    public ZipEightByteInteger(BigInteger value) { this.value = value.longValue(); }
    public ZipEightByteInteger(byte[] value) { this(value, 0); }
    public ZipEightByteInteger(byte[] value, int offset) { this.value = getLongValue(value, offset); }
    public static byte[] getBytes(long value) { return ByteBuffer.allocate(8).order(ByteOrder.LITTLE_ENDIAN).putLong(value).array(); }
    public static byte[] getBytes(BigInteger value) { return getBytes(value.longValue()); }
    public static long getLongValue(byte[] value) { return getLongValue(value, 0); }
    public static long getLongValue(byte[] value, int offset) { return ByteBuffer.wrap(value).order(ByteOrder.LITTLE_ENDIAN).getLong(offset); }
    public static BigInteger getValue(byte[] value) { return getValue(value, 0); }
    public static BigInteger getValue(byte[] value, int offset) { return unsigned(getLongValue(value, offset)); }
    private static BigInteger unsigned(long value) { return value >= 0 ? BigInteger.valueOf(value) : BigInteger.valueOf(value & Long.MAX_VALUE).add(HIGH); }
    public byte[] getBytes() { return getBytes(value); }
    public long getLongValue() { return value; }
    public BigInteger getValue() { return unsigned(value); }
    public boolean equals(Object other) { return other instanceof ZipEightByteInteger item && item.value == value; }
    public int hashCode() { return Long.hashCode(value); }
    public String toString() { return Long.toUnsignedString(value); }
}
JAVA
