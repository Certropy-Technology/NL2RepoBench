#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/exec src/main/java/org/apache/commons/exec/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>stub</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/exec/CommandLine.java <<'JAVA'
package org.apache.commons.exec;
public class CommandLine {
    public CommandLine(String executable) {}
    public static CommandLine parse(String line) { return new CommandLine("stub"); }
    public CommandLine addArgument(String value) { return this; }
    public String getExecutable() { return "stub"; }
    public String[] getArguments() { return new String[0]; }
    public String[] toStrings() { return new String[] {"stub"}; }
}
JAVA
cat > src/main/java/org/apache/commons/exec/util/StringUtils.java <<'JAVA'
package org.apache.commons.exec.util;
public final class StringUtils {
    private StringUtils() {}
    public static String quoteArgument(String value) { return value; }
    public static boolean isQuoted(String value) { return false; }
    public static String fixFileSeparatorChar(String value) { return value; }
    public static String[] split(String value, String separator) { return new String[] {value}; }
    public static String toString(String[] values, String separator) { return "stub"; }
    public static StringBuffer stringSubstitution(String value, java.util.Map<? super String, ?> vars, boolean lenient) { return new StringBuffer("stub"); }
}
JAVA
