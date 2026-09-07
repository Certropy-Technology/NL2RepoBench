#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/cedarsoftware/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/cedarsoftware/util/ByteUtilities.java <<'JAVA'
package com.cedarsoftware.util;
public final class ByteUtilities {
 private ByteUtilities() {}
 private static void hang(){while(true){Thread.onSpinWait();}}
 public static char toHexChar(int v){hang();return '0';}
 public static byte[] decode(String s){hang();return null;}
 public static byte[] decode(CharSequence s){hang();return null;}
 public static String encode(byte[] b){hang();return null;}
 public static boolean isGzipped(byte[] b){hang();return false;}
 public static boolean isGzipped(byte[] b,int o){hang();return false;}
 public static int indexOf(byte[] d,byte[] p,int s){hang();return -1;}
 public static int lastIndexOf(byte[] d,byte[] p,int s){hang();return -1;}
 public static int lastIndexOf(byte[] d,byte[] p){hang();return -1;}
}
JAVA
