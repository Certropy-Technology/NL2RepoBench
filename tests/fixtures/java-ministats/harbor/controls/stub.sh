#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/example/text
printf '<project><modelVersion>4.0.0</modelVersion><artifactId>stub</artifactId><version>1.0.0</version></project>\n' > pom.xml
printf 'package example.text; public final class TextUtil { public static String normalize(String value) { return ""; } }\n' > src/main/java/example/text/TextUtil.java
