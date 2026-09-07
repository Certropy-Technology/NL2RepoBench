#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/joda/time/format
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>offline</artifactId><version>1</version></project>' > pom.xml
cat > src/main/java/org/joda/time/format/FormatUtils.java <<'JAVA'
package org.joda.time.format; import java.io.*;
public class FormatUtils { private FormatUtils(){} private static void p(Appendable a,String s)throws IOException{a.append(s);} private static void pad(Appendable a,String s,int n)throws IOException{if(s.startsWith("-")){a.append('-');for(int i=s.length()-1;i<n;i++)a.append('0');a.append(s,1,s.length());}else{for(int i=s.length();i<n;i++)a.append('0');a.append(s);}}
 public static void appendPaddedInteger(StringBuffer b,int v,int s){try{pad(b,Integer.toString(v),s);}catch(IOException e){throw new AssertionError(e);}} public static void appendPaddedInteger(Appendable a,int v,int s)throws IOException{pad(a,Integer.toString(v),s);}
 public static void appendPaddedInteger(StringBuffer b,long v,int s){try{pad(b,Long.toString(v),s);}catch(IOException e){throw new AssertionError(e);}} public static void appendPaddedInteger(Appendable a,long v,int s)throws IOException{pad(a,Long.toString(v),s);}
 public static void writePaddedInteger(Writer w,int v,int s)throws IOException{pad(w,Integer.toString(v),s);} public static void writePaddedInteger(Writer w,long v,int s)throws IOException{pad(w,Long.toString(v),s);}
 public static void appendUnpaddedInteger(StringBuffer b,int v){b.append(v);} public static void appendUnpaddedInteger(Appendable a,int v)throws IOException{p(a,Integer.toString(v));} public static void appendUnpaddedInteger(StringBuffer b,long v){b.append(v);} public static void appendUnpaddedInteger(Appendable a,long v)throws IOException{p(a,Long.toString(v));}
 public static void writeUnpaddedInteger(Writer w,int v)throws IOException{w.write(Integer.toString(v));} public static void writeUnpaddedInteger(Writer w,long v)throws IOException{w.write(Long.toString(v));} public static int calculateDigitCount(long v){return v==Long.MIN_VALUE?19:Long.toString(Math.abs(v)).length();}}
JAVA
