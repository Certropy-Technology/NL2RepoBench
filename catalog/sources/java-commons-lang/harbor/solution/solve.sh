#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/apache/commons/lang3
cat > /workspace/src/main/java/org/apache/commons/lang3/StringUtils.java <<'JAVA'
package org.apache.commons.lang3;
import java.util.*;
public final class StringUtils {
    private StringUtils() {}
    public static boolean isEmpty(CharSequence cs) { return cs == null || cs.length() == 0; }
    public static boolean isBlank(CharSequence cs) { if (cs == null) return true; for (int i=0;i<cs.length();i++) if (!Character.isWhitespace(cs.charAt(i))) return false; return true; }
    public static boolean contains(CharSequence seq, int searchChar) { return seq != null && seq.length() > 0 && seq.toString().indexOf(searchChar) >= 0; }
    public static int countMatches(CharSequence str, char ch) { if (isEmpty(str)) return 0; int n=0; for(int i=0;i<str.length();i++) if(str.charAt(i)==ch)n++; return n; }
    public static int countMatches(CharSequence str, CharSequence sub) { if(isEmpty(str)||isEmpty(sub))return 0; int n=0,p=0; while((p=str.toString().indexOf(sub.toString(),p))>=0){n++;p+=sub.length();} return n; }
    public static String defaultString(String str) { return str == null ? "" : str; }
    public static String defaultString(String str, String fallback) { return str == null ? fallback : str; }
    public static String capitalize(String str) { if(isEmpty(str))return str; int cp=str.codePointAt(0), changed=Character.toTitleCase(cp); return cp==changed?str:new StringBuilder().appendCodePoint(changed).append(str.substring(Character.charCount(cp))).toString(); }
    public static String uncapitalize(String str) { if(isEmpty(str))return str; int cp=str.codePointAt(0), changed=Character.toLowerCase(cp); return cp==changed?str:new StringBuilder().appendCodePoint(changed).append(str.substring(Character.charCount(cp))).toString(); }
    public static String reverse(String str) { return str == null ? null : new StringBuilder(str).reverse().toString(); }
    public static String[] split(String str) { return splitWorker(str, null); }
    public static String[] split(String str, char separator) { return splitWorker(str, String.valueOf(separator)); }
    private static String[] splitWorker(String str, String separators) { if(str==null)return null; if(str.isEmpty())return new String[0]; List<String> out=new ArrayList<>(); int start=-1; for(int i=0;i<str.length();i++){ boolean sep=separators==null?Character.isWhitespace(str.charAt(i)):separators.indexOf(str.charAt(i))>=0; if(!sep&&start<0)start=i; if((sep||i==str.length()-1)&&start>=0){int end=sep?i:i+1;out.add(str.substring(start,end));start=-1;}} return out.toArray(String[]::new); }
    public static String substring(String str, int start) { if(str==null)return null; if(start<0)start=str.length()+start; if(start<0)start=0; return start>str.length()?"":str.substring(start); }
    public static String substring(String str, int start, int end) { if(str==null)return null; if(start<0)start=str.length()+start; if(end<0)end=str.length()+end; if(end>str.length())end=str.length(); if(start>end)return ""; if(start<0)start=0; if(end<0)end=0; return str.substring(start,end); }
    public static String left(String str,int len) { if(str==null)return null;if(len<0)return "";if(str.length()<=len)return str;int cut=len;if(cut>0&&cut<str.length()&&Character.isHighSurrogate(str.charAt(cut-1))&&Character.isLowSurrogate(str.charAt(cut)))cut--;return str.substring(0,cut); }
    public static String right(String str,int len) { if(str==null)return null;if(len<0)return "";if(str.length()<=len)return str;int start=str.length()-len;if(start>0&&start<str.length()&&Character.isHighSurrogate(str.charAt(start-1))&&Character.isLowSurrogate(str.charAt(start)))start++;return str.substring(start); }
}
JAVA
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>org.apache.commons</groupId><artifactId>commons-lang</artifactId><version>1.0.0</version></project>
XML
