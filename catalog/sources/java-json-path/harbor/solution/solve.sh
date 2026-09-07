#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/com/jayway/jsonpath
cat > /workspace/pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>json-path</artifactId><version>1.0.0</version></project>
XML
cat > /workspace/src/main/java/com/jayway/jsonpath/Predicate.java <<'JAVA'
package com.jayway.jsonpath;
public interface Predicate { boolean apply(Object value); }
JAVA
cat > /workspace/src/main/java/com/jayway/jsonpath/InvalidPathException.java <<'JAVA'
package com.jayway.jsonpath;
public class InvalidPathException extends RuntimeException { public InvalidPathException(String m){super(m);} public InvalidPathException(Throwable t){super(t);} }
JAVA
cat > /workspace/src/main/java/com/jayway/jsonpath/JsonPath.java <<'JAVA'
package com.jayway.jsonpath;
public final class JsonPath {
  private final String path; private final boolean definite;
  private JsonPath(String p){path=p; definite=classify(p);}
  public static JsonPath compile(String jsonPath, Predicate... filters){String p=normalize(jsonPath); validate(p); return new JsonPath(p);}
  public String getPath(){return path;}
  public boolean isDefinite(){return definite;}
  public static boolean isPathDefinite(String path){return compile(path).isDefinite();}
  private static String normalize(String s){if(s==null)throw new InvalidPathException("path can not be null or empty"); String p=s.trim(); if(p.isEmpty())throw new InvalidPathException("path can not be null or empty"); if(p.charAt(0)!='$'&&p.charAt(0)!='@')p="$."+p; return p;}
  private static void validate(String p){if(p.endsWith("."))throw new InvalidPathException("Path must not end with a '.' or '..'"); int depth=0; boolean quote=false; char q=0; for(int i=0;i<p.length();i++){char c=p.charAt(i); if(quote){if(c==q)quote=false; continue;} if(c=='\''||c=='\"'){quote=true;q=c;} else if(c=='[')depth++; else if(c==']'){if(--depth<0)throw new InvalidPathException("Unclosed bracket");}} if(depth!=0||quote)throw new InvalidPathException("Unclosed bracket");}
  private static boolean classify(String p){return !(p.contains("..")||p.contains("*")||p.matches(".*\\[[^]]*,[^]]*\\].*")||p.matches(".*\\[[^]]*:[^]]*\\].*")||p.contains("[?")||p.matches(".*\\.[A-Za-z_][A-Za-z0-9_]*\\(.*\\)$"));}
}
JAVA
