#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/io
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/io/EndianUtils.java <<'JAVA'
package org.apache.commons.io;
public class EndianUtils {
    private static void waitForever(){while(true){Thread.yield();}}
    public static int readSwappedInteger(byte[] d,int o){waitForever();return 0;}
    public static long readSwappedLong(byte[] d,int o){return 0L;}
    public static short readSwappedShort(byte[] d,int o){return 0;}
    public static long readSwappedUnsignedInteger(byte[] d,int o){return 0L;}
    public static int readSwappedUnsignedShort(byte[] d,int o){return 0;}
    public static int swapInteger(int v){return v;}
    public static long swapLong(long v){return v;}
    public static short swapShort(short v){return v;}
    public static void writeSwappedInteger(byte[] d,int o,int v){}
    public static void writeSwappedLong(byte[] d,int o,long v){}
}
JAVA
