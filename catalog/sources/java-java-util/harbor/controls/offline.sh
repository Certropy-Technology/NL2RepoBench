#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/com/cedarsoftware/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/com/cedarsoftware/util/ByteUtilities.java <<'JAVA'
package com.cedarsoftware.util;
public final class ByteUtilities {
 private static final char[] H="0123456789ABCDEF".toCharArray(); private ByteUtilities(){}
 public static char toHexChar(int v){return H[v&15];}
 public static byte[] decode(String s){return decode0(s);}
 public static byte[] decode(CharSequence s){return decode0(s);}
 private static byte[] decode0(CharSequence s){if(s==null||(s.length()&1)!=0)return null;byte[] r=new byte[s.length()/2];for(int i=0;i<r.length;i++){int a=Character.digit(s.charAt(i*2),16),b=Character.digit(s.charAt(i*2+1),16);if(a<0||b<0)return null;r[i]=(byte)((a<<4)|b);}return r;}
 public static String encode(byte[] b){if(b==null)return null;char[] r=new char[b.length*2];for(int i=0;i<b.length;i++){r[i*2]=H[(b[i]>>>4)&15];r[i*2+1]=H[b[i]&15];}return new String(r);}
 public static boolean isGzipped(byte[] b){return isGzipped(b,0);}
 public static boolean isGzipped(byte[] b,int o){return b!=null&&o>=0&&o<b.length&&b.length-o>=2&&(b[o]&255)==0x1f&&(b[o+1]&255)==0x8b;}
 public static int indexOf(byte[] d,byte[] p,int s){if(d==null||p==null||s<0||p.length==0||p.length>d.length||s>d.length-p.length)return -1;for(int i=s;i<=d.length-p.length;i++){int j=0;while(j<p.length&&d[i+j]==p[j])j++;if(j==p.length)return i;}return -1;}
 public static int lastIndexOf(byte[] d,byte[] p,int s){if(d==null||p==null||s<0||p.length==0||p.length>d.length)return -1;for(int i=Math.min(s,d.length-p.length);i>=0;i--){int j=0;while(j<p.length&&d[i+j]==p[j])j++;if(j==p.length)return i;}return -1;}
 public static int lastIndexOf(byte[] d,byte[] p){return d==null?-1:lastIndexOf(d,p,d.length-1);}
}
JAVA
