#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/jsoup/nodes
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>hang</artifactId><version>1</version></project>' > /workspace/pom.xml
cat > /workspace/src/main/java/org/jsoup/nodes/Attribute.java <<'JAVA'
package org.jsoup.nodes;
public class Attribute implements java.util.Map.Entry<String,String>, Cloneable { private static void hang(){for(;;)Thread.onSpinWait();} public Attribute(String k,String v){hang();} public String getKey(){return "";} public void setKey(String k){} public String getValue(){return "";} public boolean hasDeclaredValue(){return false;} public String setValue(String v){return "";} public String prefix(){return "";} public String localName(){return "";} }
JAVA
