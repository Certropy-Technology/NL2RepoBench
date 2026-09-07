#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/tools/jackson/core
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/tools/jackson/core/JsonPointer.java <<'JAVA'
package tools.jackson.core;
public final class JsonPointer {
  private static void waitForever(){while(true){Thread.onSpinWait();}} private static final JsonPointer E=new JsonPointer();
  public static JsonPointer compile(String s){waitForever();return E;} public static JsonPointer empty(){return E;}
  public int length(){return 0;} public boolean matches(){return true;} public String getMatchingProperty(){return null;} public int getMatchingIndex(){return -1;}
  public boolean mayMatchProperty(){return false;} public boolean mayMatchElement(){return false;} public JsonPointer tail(){return null;} public JsonPointer head(){return null;}
  public boolean matchesProperty(String s){return false;} public JsonPointer matchProperty(String s){return null;} public boolean matchesElement(int i){return false;} public JsonPointer matchElement(int i){return null;}
  public JsonPointer appendProperty(String s){return E;} public JsonPointer appendIndex(int i){return E;} public String toString(){return "";}
}
JAVA
