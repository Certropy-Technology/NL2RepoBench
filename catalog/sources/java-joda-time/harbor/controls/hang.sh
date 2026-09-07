#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/joda/time/format
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>' > pom.xml
cat > src/main/java/org/joda/time/format/FormatUtils.java <<'JAVA'
package org.joda.time.format; import java.io.*;
public class FormatUtils { private FormatUtils(){} private static void waitForever(){for(;;){try{Thread.sleep(1000);}catch(InterruptedException ignored){}}}
 public static void appendPaddedInteger(StringBuffer b,int v,int s){waitForever();} public static void appendPaddedInteger(Appendable a,int v,int s)throws IOException{waitForever();}
 public static void appendPaddedInteger(StringBuffer b,long v,int s){waitForever();} public static void appendPaddedInteger(Appendable a,long v,int s)throws IOException{waitForever();}
 public static void writePaddedInteger(Writer w,int v,int s)throws IOException{waitForever();} public static void writePaddedInteger(Writer w,long v,int s)throws IOException{waitForever();}
 public static void appendUnpaddedInteger(StringBuffer b,int v){} public static void appendUnpaddedInteger(Appendable a,int v)throws IOException{} public static void appendUnpaddedInteger(StringBuffer b,long v){} public static void appendUnpaddedInteger(Appendable a,long v)throws IOException{}
 public static void writeUnpaddedInteger(Writer w,int v)throws IOException{} public static void writeUnpaddedInteger(Writer w,long v)throws IOException{} public static int calculateDigitCount(long v){return 0;}}
JAVA
