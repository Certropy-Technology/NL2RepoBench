#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/jsoup/nodes
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>org.jsoup</groupId><artifactId>jsoup</artifactId><version>1.21.1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/org/jsoup/nodes/Attribute.java <<'JAVA'
package org.jsoup.nodes;
public class Attribute implements java.util.Map.Entry<String,String>, Cloneable { private String k,v; public Attribute(String k,String v){if(k==null)throw new IllegalArgumentException(); k=k.trim(); if(k.isEmpty())throw new IllegalArgumentException();this.k=k;this.v=v;} public String getKey(){return k;} public void setKey(String k){if(k==null||k.trim().isEmpty())throw new IllegalArgumentException();this.k=k.trim();} public String getValue(){return v==null?"":v;} public boolean hasDeclaredValue(){return v!=null;} public String setValue(String v){String old=getValue();this.v=v;return old;} public String prefix(){int p=k.indexOf(':');return p<0?"":k.substring(0,p);} public String localName(){int p=k.indexOf(':');return p<0?k:k.substring(p+1);} }
JAVA
