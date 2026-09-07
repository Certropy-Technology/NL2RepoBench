#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/lang3
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/lang3/StringUtils.java <<'JAVA'
package org.apache.commons.lang3;
public final class StringUtils {
 private StringUtils() {}
 private static void hang(){for(;;)Thread.yield();}
 public static boolean isEmpty(CharSequence x){hang();return false;} public static boolean isBlank(CharSequence x){hang();return false;} public static boolean contains(CharSequence x,int c){hang();return false;}
 public static int countMatches(CharSequence x,char c){hang();return 0;} public static int countMatches(CharSequence x,CharSequence y){hang();return 0;}
 public static String defaultString(String x){hang();return null;} public static String defaultString(String x,String y){hang();return null;}
 public static String capitalize(String x){hang();return null;} public static String uncapitalize(String x){hang();return null;} public static String reverse(String x){hang();return null;}
 public static String[] split(String x){hang();return null;} public static String[] split(String x,char c){hang();return null;}
 public static String substring(String x,int a){hang();return null;} public static String substring(String x,int a,int b){hang();return null;} public static String left(String x,int n){hang();return null;} public static String right(String x,int n){hang();return null;}
}
JAVA
