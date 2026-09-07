#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/lang3
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/lang3/StringUtils.java <<'JAVA'
package org.apache.commons.lang3;
public final class StringUtils {
 private StringUtils() {}
 public static boolean isEmpty(CharSequence x){return false;} public static boolean isBlank(CharSequence x){return false;} public static boolean contains(CharSequence x,int c){return false;}
 public static int countMatches(CharSequence x,char c){return 0;} public static int countMatches(CharSequence x,CharSequence y){return 0;}
 public static String defaultString(String x){return "";} public static String defaultString(String x,String y){return "";}
 public static String capitalize(String x){return "";} public static String uncapitalize(String x){return "";} public static String reverse(String x){return "";}
 public static String[] split(String x){return new String[0];} public static String[] split(String x,char c){return new String[0];}
 public static String substring(String x,int a){return "";} public static String substring(String x,int a,int b){return "";} public static String left(String x,int n){return "";} public static String right(String x,int n){return "";}
}
JAVA
