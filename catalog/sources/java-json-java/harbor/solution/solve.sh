#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/main/java/org/json
cat > /workspace/pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>json-java</artifactId><version>1.0.0</version></project>
XML
cat > /workspace/src/main/java/org/json/JSONObject.java <<'JAVA'
package org.json;

public class JSONObject {
    public static String quote(final String string) {
        if (string == null || string.isEmpty()) return "\"\"";
        StringBuilder result = new StringBuilder(string.length() + 2);
        result.append('"');
        char previous = 0;
        for (int index = 0; index < string.length(); index++) {
            char current = string.charAt(index);
            switch (current) {
                case '\\': case '"': result.append('\\').append(current); break;
                case '/': if (previous == '<') result.append('\\'); result.append(current); break;
                case '\b': result.append("\\b"); break;
                case '\t': result.append("\\t"); break;
                case '\n': result.append("\\n"); break;
                case '\f': result.append("\\f"); break;
                case '\r': result.append("\\r"); break;
                default:
                    if (current < ' ' || (current >= '\u0080' && current < '\u00a0') || (current >= '\u2000' && current < '\u2100')) {
                        result.append(String.format("\\u%04x", (int) current));
                    } else result.append(current);
            }
            previous = current;
        }
        return result.append('"').toString();
    }
}
JAVA
