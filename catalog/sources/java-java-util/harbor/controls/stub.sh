#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/cedarsoftware/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/cedarsoftware/util/ByteUtilities.java <<'JAVA'
package com.cedarsoftware.util;
public final class ByteUtilities {
 private ByteUtilities() {}
 public static char toHexChar(int v){return '0';}
 public static byte[] decode(String s){return new byte[0];}
 public static byte[] decode(CharSequence s){return new byte[0];}
 public static String encode(byte[] b){return "";}
 public static boolean isGzipped(byte[] b){return false;}
 public static boolean isGzipped(byte[] b,int o){return false;}
 public static int indexOf(byte[] d,byte[] p,int s){return -1;}
 public static int lastIndexOf(byte[] d,byte[] p,int s){return -1;}
 public static int lastIndexOf(byte[] d,byte[] p){return -1;}
}
JAVA
