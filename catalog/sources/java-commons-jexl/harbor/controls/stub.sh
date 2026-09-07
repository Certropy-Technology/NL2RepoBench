#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/jexl3
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/jexl3/JexlArithmetic.java <<'JAVA'
package org.apache.commons.jexl3;
import java.util.*;
public class JexlArithmetic {
 public JexlArithmetic(boolean strict) {}
 public boolean toBoolean(Object v){return false;} public double toDouble(Object v){return 0.0;}
 public int toInteger(Object v){return 0;} public long toLong(Object v){return 0L;} public String toString(Object v){return "stub";}
 public static Integer parseIdentifier(Object v){return null;} public Integer size(Object v){return 0;} public Integer size(Object v,Integer d){return d;}
 public Boolean empty(Object v){return true;} public Boolean startsWith(Object l,Object r){return false;}
}
JAVA
