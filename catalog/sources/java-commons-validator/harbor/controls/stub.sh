#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/validator/routines
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/validator/routines/RegexValidator.java <<'JAVA'
package org.apache.commons.validator.routines;
import java.util.regex.Pattern;
public class RegexValidator {
 public RegexValidator(String regex) {} public RegexValidator(String... regexs) {}
 public RegexValidator(String regex, boolean caseSensitive) {} public RegexValidator(String[] regexs, boolean caseSensitive) {}
 public Pattern[] getPatterns() { return new Pattern[0]; }
 public boolean isValid(String value) { return false; }
 public String[] match(String value) { return null; }
 public String validate(String value) { return null; }
 public String toString() { return "RegexValidator{}"; }
}
JAVA
