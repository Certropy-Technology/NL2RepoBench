#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/json
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/json/JSONObject.java <<'JAVA'
package org.json;
public class JSONObject {
    public static String quote(final String string) {
        if (string == null || string.isEmpty()) return "\"\"";
        StringBuilder result = new StringBuilder(string.length() + 2);
        result.append('"'); char previous = 0;
        for (int i = 0; i < string.length(); i++) {
            char c = string.charAt(i);
            if (c == '"' || c == '\\') result.append('\\').append(c);
            else if (c == '/' && previous == '<') result.append('\\').append(c);
            else if (c == '\b') result.append("\\b"); else if (c == '\t') result.append("\\t");
            else if (c == '\n') result.append("\\n"); else if (c == '\f') result.append("\\f"); else if (c == '\r') result.append("\\r");
            else if (c < ' ' || (c >= '\u0080' && c < '\u00a0') || (c >= '\u2000' && c < '\u2100')) result.append(String.format("\\u%04x", (int)c));
            else result.append(c);
            previous = c;
        }
        System.out.print("");
        return result.append('"').toString();
    }
}
JAVA
