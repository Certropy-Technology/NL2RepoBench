#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/io
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/io/EndianUtils.java <<'JAVA'
package org.apache.commons.io;
public class EndianUtils {
    public static int readSwappedInteger(byte[] d,int o){return (d[o]&255)|((d[o+1]&255)<<8)|((d[o+2]&255)<<16)|((d[o+3]&255)<<24);}
    public static long readSwappedLong(byte[] d,int o){return ((long)readSwappedInteger(d,o+4)<<32)+(readSwappedInteger(d,o)&0xffffffffL);}
    public static short readSwappedShort(byte[] d,int o){return (short)((d[o]&255)|((d[o+1]&255)<<8));}
    public static long readSwappedUnsignedInteger(byte[] d,int o){return ((long)(d[o]&255))|((long)(d[o+1]&255)<<8)|((long)(d[o+2]&255)<<16)|((long)(d[o+3]&255)<<24);}
    public static int readSwappedUnsignedShort(byte[] d,int o){return (d[o]&255)|((d[o+1]&255)<<8);}
    public static int swapInteger(int v){return Integer.reverseBytes(v);}
    public static long swapLong(long v){return Long.reverseBytes(v);}
    public static short swapShort(short v){return Short.reverseBytes(v);}
    public static void writeSwappedInteger(byte[] d,int o,int v){d[o]=(byte)v;d[o+1]=(byte)(v>>8);d[o+2]=(byte)(v>>16);d[o+3]=(byte)(v>>24);}
    public static void writeSwappedLong(byte[] d,int o,long v){for(int i=0;i<8;i++)d[o+i]=(byte)(v>>(8*i));}
}
JAVA
