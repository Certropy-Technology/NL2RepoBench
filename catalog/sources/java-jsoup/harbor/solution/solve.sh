#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/jsoup/nodes
cat > /workspace/src/main/java/org/jsoup/nodes/Attribute.java <<'JAVA'
package org.jsoup.nodes;
public class Attribute implements java.util.Map.Entry<String,String>, Cloneable {
  private String key; private String value;
  public Attribute(String key,String value){setKey(key);this.value=value;}
  public String getKey(){return key;}
  public void setKey(String key){if(key==null)throw new IllegalArgumentException(); key=key.trim(); if(key.isEmpty())throw new IllegalArgumentException(); this.key=key;}
  public String getValue(){return value==null?"":value;}
  public boolean hasDeclaredValue(){return value!=null;}
  public String setValue(String value){String old=getValue();this.value=value;return old;}
  public String prefix(){int p=key.indexOf(':');return p<0?"":key.substring(0,p);}
  public String localName(){int p=key.indexOf(':');return p<0?key:key.substring(p+1);}
}
JAVA
cat > /workspace/pom.xml <<'POM'
<project><modelVersion>4.0.0</modelVersion><groupId>org.jsoup</groupId><artifactId>jsoup</artifactId><version>1.21.1</version></project>
POM
