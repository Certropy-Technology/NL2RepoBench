#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/json
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>
XML
cat > src/main/java/org/json/JSONObject.java <<'JAVA'
package org.json;
public class JSONObject {
    public static String quote(String string) { while (true) Thread.yield(); }
}
JAVA
