#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/net/sf/joptsimple
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/net/sf/joptsimple/KeyValuePair.java <<'JAVA'
package net.sf.joptsimple;
public record KeyValuePair(String key, String value) {
    public static KeyValuePair valueOf(String input) {
        int at = input.indexOf('=');
        return at < 0 ? new KeyValuePair(input, null) : new KeyValuePair(input.substring(0, at), input.substring(at + 1));
    }
}
JAVA
