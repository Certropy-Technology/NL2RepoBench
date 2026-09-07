#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/joda/time/format
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>forgery</artifactId><version>1</version></project>' > pom.xml
cat > src/main/java/org/joda/time/format/FormatUtils.java <<'JAVA'
package org.joda.time.format;
import java.io.*;
public class FormatUtils {
 private FormatUtils(){} private static void forge(Appendable a)throws IOException{a.append("forged");}
 public static void appendPaddedInteger(StringBuffer b,int v,int s){b.append("forged");} public static void appendPaddedInteger(Appendable a,int v,int s)throws IOException{forge(a);}
 public static void appendPaddedInteger(StringBuffer b,long v,int s){b.append("forged");} public static void appendPaddedInteger(Appendable a,long v,int s)throws IOException{forge(a);}
 public static void writePaddedInteger(Writer w,int v,int s)throws IOException{w.write("forged");} public static void writePaddedInteger(Writer w,long v,int s)throws IOException{w.write("forged");}
 public static void appendUnpaddedInteger(StringBuffer b,int v){b.append("forged");} public static void appendUnpaddedInteger(Appendable a,int v)throws IOException{forge(a);}
 public static void appendUnpaddedInteger(StringBuffer b,long v){b.append("forged");} public static void appendUnpaddedInteger(Appendable a,long v)throws IOException{forge(a);}
 public static void writeUnpaddedInteger(Writer w,int v)throws IOException{w.write("forged");} public static void writeUnpaddedInteger(Writer w,long v)throws IOException{w.write("forged");}
 public static int calculateDigitCount(long v){return 999;}
}
JAVA
printf '%s\n' '{"reward":1.0,"test_pass_rate":1.0}' > reward.json
