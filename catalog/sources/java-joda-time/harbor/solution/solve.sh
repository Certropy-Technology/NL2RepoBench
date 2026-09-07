#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/joda/time/format
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>joda-time</artifactId><version>1.0.0</version></project>
XML
cat > /workspace/src/main/java/org/joda/time/format/FormatUtils.java <<'JAVA'
package org.joda.time.format;
import java.io.*;
public class FormatUtils {
 private FormatUtils() {}
 public static void appendPaddedInteger(StringBuffer b,int v,int s){try{appendPaddedInteger((Appendable)b,v,s);}catch(IOException e){throw new AssertionError(e);}}
 public static void appendPaddedInteger(Appendable a,int v,int s)throws IOException{append(a,Integer.toString(v),s);}
 public static void appendPaddedInteger(StringBuffer b,long v,int s){try{appendPaddedInteger((Appendable)b,v,s);}catch(IOException e){throw new AssertionError(e);}}
 public static void appendPaddedInteger(Appendable a,long v,int s)throws IOException{append(a,Long.toString(v),s);}
 public static void writePaddedInteger(Writer w,int v,int s)throws IOException{appendPaddedInteger((Appendable)w,v,s);}
 public static void writePaddedInteger(Writer w,long v,int s)throws IOException{appendPaddedInteger((Appendable)w,v,s);}
 public static void appendUnpaddedInteger(StringBuffer b,int v){b.append(v);}
 public static void appendUnpaddedInteger(Appendable a,int v)throws IOException{a.append(Integer.toString(v));}
 public static void appendUnpaddedInteger(StringBuffer b,long v){b.append(v);}
 public static void appendUnpaddedInteger(Appendable a,long v)throws IOException{a.append(Long.toString(v));}
 public static void writeUnpaddedInteger(Writer w,int v)throws IOException{w.write(Integer.toString(v));}
 public static void writeUnpaddedInteger(Writer w,long v)throws IOException{w.write(Long.toString(v));}
 public static int calculateDigitCount(long v){if(v==Long.MIN_VALUE)return 19; return Long.toString(Math.abs(v)).length();}
 private static void append(Appendable a,String text,int size)throws IOException{int digits=text.charAt(0)=='-'?text.length()-1:text.length(); if(text.charAt(0)=='-'){a.append('-'); for(int i=digits;i<size;i++)a.append('0'); a.append(text,1,text.length());}else{for(int i=digits;i<size;i++)a.append('0'); a.append(text);}}
}
JAVA
