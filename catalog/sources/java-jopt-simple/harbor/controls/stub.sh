#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/net/sf/joptsimple
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/net/sf/joptsimple/KeyValuePair.java <<'JAVA'
package net.sf.joptsimple;
public record KeyValuePair(String key, String value) {
    public static KeyValuePair valueOf(String input) { return new KeyValuePair("", null); }
}
JAVA
