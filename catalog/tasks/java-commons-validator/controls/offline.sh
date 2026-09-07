#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/validator/routines
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/validator/routines/RegexValidator.java <<'JAVA'
package org.apache.commons.validator.routines;
import java.util.regex.*;
public class RegexValidator {
 private final Pattern[] patterns;
 public RegexValidator(String regex) { this(true, new String[] {regex}); }
 public RegexValidator(String... regexs) { this(true, regexs); }
 public RegexValidator(String regex, boolean sensitive) { this(sensitive, new String[] {regex}); }
 public RegexValidator(String[] regexs, boolean sensitive) { this(sensitive, regexs); }
 private RegexValidator(boolean sensitive, String[] regexs) { if (regexs == null || regexs.length == 0) throw new IllegalArgumentException(); patterns = new Pattern[regexs.length]; for (int i = 0; i < regexs.length; i++) { if (regexs[i] == null || regexs[i].isEmpty()) throw new IllegalArgumentException(); patterns[i] = Pattern.compile(regexs[i], sensitive ? 0 : Pattern.CASE_INSENSITIVE); } }
 public Pattern[] getPatterns() { return patterns.clone(); }
 public boolean isValid(String value) { return value != null && first(value) != null; }
 public String[] match(String value) { Matcher m = first(value); if (m == null) return null; String[] out = new String[m.groupCount()]; for (int i = 0; i < out.length; i++) out[i] = m.group(i + 1); return out; }
 public String validate(String value) { Matcher m = first(value); if (m == null) return null; if (m.groupCount() == 1) return m.group(1) == null ? "" : m.group(1); StringBuilder out = new StringBuilder(); for (int i = 1; i <= m.groupCount(); i++) if (m.group(i) != null) out.append(m.group(i)); return out.toString(); }
 public String toString() { StringBuilder out = new StringBuilder("RegexValidator{"); for (int i = 0; i < patterns.length; i++) { if (i > 0) out.append(','); out.append(patterns[i].pattern()); } return out.append('}').toString(); }
 private Matcher first(String value) { if (value == null) return null; for (Pattern p : patterns) { Matcher m = p.matcher(value); if (m.matches()) return m; } return null; }
}
JAVA
