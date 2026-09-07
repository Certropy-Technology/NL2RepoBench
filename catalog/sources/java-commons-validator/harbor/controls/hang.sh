#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/validator/routines
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>hang</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/validator/routines/RegexValidator.java <<'JAVA'
package org.apache.commons.validator.routines;
import java.util.regex.Pattern;
public class RegexValidator {
 private static void hang() { while (true) Thread.yield(); }
 public RegexValidator(String regex) { hang(); } public RegexValidator(String... regexs) { hang(); }
 public RegexValidator(String regex, boolean caseSensitive) { hang(); } public RegexValidator(String[] regexs, boolean caseSensitive) { hang(); }
 public Pattern[] getPatterns() { return null; } public boolean isValid(String value) { return false; }
 public String[] match(String value) { return null; } public String validate(String value) { return null; }
 public String toString() { return ""; }
}
JAVA
