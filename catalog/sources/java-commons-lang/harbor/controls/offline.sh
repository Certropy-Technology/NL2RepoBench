#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/lang3
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/apache/commons/lang3/StringUtils.java <<'JAVA'
package org.apache.commons.lang3;
import java.util.*;
public final class StringUtils {
 private StringUtils() {}
 public static boolean isEmpty(CharSequence x){return x==null||x.length()==0;} public static boolean isBlank(CharSequence x){if(x==null)return true;for(int i=0;i<x.length();i++)if(!Character.isWhitespace(x.charAt(i)))return false;return true;} public static boolean contains(CharSequence x,int c){return x!=null&&x.toString().indexOf(c)>=0;}
 public static int countMatches(CharSequence x,char c){if(isEmpty(x))return 0;int n=0;for(int i=0;i<x.length();i++)if(x.charAt(i)==c)n++;return n;} public static int countMatches(CharSequence x,CharSequence y){if(isEmpty(x)||isEmpty(y))return 0;int n=0,p=0;while((p=x.toString().indexOf(y.toString(),p))>=0){n++;p+=y.length();}return n;}
 public static String defaultString(String x){return x==null?"":x;} public static String defaultString(String x,String y){return x==null?y:x;} public static String capitalize(String x){if(x==null||x.isEmpty())return x;int c=x.codePointAt(0),d=Character.toTitleCase(c);return c==d?x:new StringBuilder().appendCodePoint(d).append(x.substring(Character.charCount(c))).toString();} public static String uncapitalize(String x){if(x==null||x.isEmpty())return x;int c=x.codePointAt(0),d=Character.toLowerCase(c);return c==d?x:new StringBuilder().appendCodePoint(d).append(x.substring(Character.charCount(c))).toString();} public static String reverse(String x){return x==null?null:new StringBuilder(x).reverse().toString();}
 public static String[] split(String x){return split(x,'\0',true);} public static String[] split(String x,char c){return split(x,c,false);} private static String[] split(String x,char c,boolean white){if(x==null)return null;if(x.isEmpty())return new String[0];List<String>o=new ArrayList<>();int s=-1;for(int i=0;i<x.length();i++){boolean q=white?Character.isWhitespace(x.charAt(i)):x.charAt(i)==c;if(!q&&s<0)s=i;if((q||i==x.length()-1)&&s>=0){o.add(x.substring(s,q?i:i+1));s=-1;}}return o.toArray(String[]::new);}
 public static String substring(String x,int a){if(x==null)return null;if(a<0)a=x.length()+a;if(a<0)a=0;return a>x.length()?"":x.substring(a);} public static String substring(String x,int a,int b){if(x==null)return null;if(a<0)a=x.length()+a;if(b<0)b=x.length()+b;if(b>x.length())b=x.length();if(a>b)return "";if(a<0)a=0;if(b<0)b=0;return x.substring(a,b);} public static String left(String x,int n){if(x==null)return null;if(n<0)return "";if(x.length()<=n)return x;int c=n;if(c>0&&c<x.length()&&Character.isHighSurrogate(x.charAt(c-1))&&Character.isLowSurrogate(x.charAt(c)))c--;return x.substring(0,c);} public static String right(String x,int n){if(x==null)return null;if(n<0)return "";if(x.length()<=n)return x;int s=x.length()-n;if(s>0&&s<x.length()&&Character.isHighSurrogate(x.charAt(s-1))&&Character.isLowSurrogate(x.charAt(s)))s++;return x.substring(s);}
}
JAVA
