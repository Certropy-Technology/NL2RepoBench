#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/jexl3
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/jexl3/JexlArithmetic.java <<'JAVA'
package org.apache.commons.jexl3;
import java.lang.reflect.Array; import java.util.*;
public class JexlArithmetic {
 private final boolean strict; public JexlArithmetic(boolean strict){this.strict=strict;}
 public boolean toBoolean(Object v){if(v==null)return false;if(v instanceof Boolean b)return b;if(v instanceof Number n){double d=n.doubleValue();return !Double.isNaN(d)&&d!=0.0;}if(v instanceof CharSequence s)return s.length()>0&&!"false".equals(s.toString());return true;}
 public double toDouble(Object v){if(v==null)return 0.0;if(v instanceof Number n)return n.doubleValue();if(v instanceof Boolean b)return b?1.0:0.0;if(v instanceof Character c)return c;if(v instanceof CharSequence s){if(s.length()==0)return Double.NaN;try{return Double.parseDouble(s.toString());}catch(NumberFormatException e){throw new ArithmeticException();}}throw new ArithmeticException();}
 public int toInteger(Object v){if(v==null)return 0;if(v instanceof Number n)return Double.isNaN(n.doubleValue())?0:n.intValue();if(v instanceof Boolean b)return b?1:0;if(v instanceof Character c)return c;if(v instanceof CharSequence){double d=toDouble(v);if(Double.isNaN(d))return 0;if(d==Math.floor(d)&&d>=Integer.MIN_VALUE&&d<=Integer.MAX_VALUE)return(int)d;throw new ArithmeticException();}throw new ArithmeticException();}
 public long toLong(Object v){if(v==null)return 0;if(v instanceof Number n)return Double.isNaN(n.doubleValue())?0:n.longValue();if(v instanceof Boolean b)return b?1:0;if(v instanceof Character c)return c;if(v instanceof CharSequence){double d=toDouble(v);if(Double.isNaN(d))return 0;if(d==Math.floor(d))return(long)d;throw new ArithmeticException();}throw new ArithmeticException();}
 public String toString(Object v){if(v==null)return "";if(v instanceof Double d&&Double.isNaN(d))return "";return v.toString();}
 public static Integer parseIdentifier(Object v){if(v instanceof Number n)return n.intValue();if(!(v instanceof CharSequence s)||s.length()==0||s.length()>10)return null;String x=s.toString();if(!x.equals("0")&&x.charAt(0)=='0')return null;for(int i=0;i<x.length();i++)if(x.charAt(i)<'0'||x.charAt(i)>'9')return null;try{return Integer.valueOf(x);}catch(NumberFormatException e){return null;}}
 public Integer size(Object v){return size(v,v==null?0:1);} public Integer size(Object v,Integer d){if(v==null)return d;if(v instanceof CharSequence s)return s.length();if(v.getClass().isArray())return Array.getLength(v);if(v instanceof Collection<?> c)return c.size();if(v instanceof Map<?,?> m)return m.size();return d;}
 public Boolean empty(Object v){if(v==null)return true;Integer n=size(v,null);return n!=null&&n==0;} public Boolean startsWith(Object l,Object r){if(l==null&&r==null)return true;if(l==null||r==null)return false;return l instanceof CharSequence?toString(l).startsWith(toString(r)):null;}
}
JAVA
