#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/example/text
cat > pom.xml <<'XML'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>example.text</groupId>
  <artifactId>java-ministats</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>
</project>
XML
cat > src/main/java/example/text/TextUtil.java <<'JAVA'
package example.text;

public final class TextUtil {
    private TextUtil() {}

    public static String normalize(String value) {
        return value == null ? null : value.trim();
    }
}
JAVA
