#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/jsoup/nodes
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>stub</artifactId><version>1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/org/jsoup/nodes/Attribute.java <<'JAVA'
package org.jsoup.nodes;
public class Attribute implements java.util.Map.Entry<String,String>, Cloneable { private String k,v; public Attribute(String k,String v){this.k=k;this.v=v;} public String getKey(){return k;} public void setKey(String k){this.k=k;} public String getValue(){return v==null?"":v;} public boolean hasDeclaredValue(){return v!=null;} public String setValue(String v){return "";} public String prefix(){return "";} public String localName(){return k;} }
JAVA
