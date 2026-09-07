#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/com/jayway/jsonpath
printf '%s\n' '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/com/jayway/jsonpath/JsonPath.java <<'JAVA'
package com.jayway.jsonpath;
public final class JsonPath { public static JsonPath compile(String s, Predicate... p){ while(true){ try{Thread.sleep(1000);}catch(Exception e){} } } public String getPath(){return "";} public boolean isDefinite(){return false;} public static boolean isPathDefinite(String s){return false;} }
JAVA
cat > /workspace/src/main/java/com/jayway/jsonpath/Predicate.java <<'JAVA'
package com.jayway.jsonpath; public interface Predicate { boolean apply(Object value); }
JAVA
cat > /workspace/src/main/java/com/jayway/jsonpath/InvalidPathException.java <<'JAVA'
package com.jayway.jsonpath; public class InvalidPathException extends RuntimeException { public InvalidPathException(String m){super(m);} }
JAVA
