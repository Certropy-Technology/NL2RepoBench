#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/commons/exec src/main/java/org/apache/commons/exec/util
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/exec/CommandLine.java <<'JAVA'
package org.apache.commons.exec;
import java.util.ArrayList;
import java.util.List;
public class CommandLine {
    private final String executable;
    private final List<String> arguments = new ArrayList<>();
    public CommandLine(String executable) { this.executable = executable; }
    public static CommandLine parse(String line) {
        String trimmed = line.trim();
        int split = trimmed.indexOf(' ');
        CommandLine command = new CommandLine(split < 0 ? trimmed : trimmed.substring(0, split));
        if (split >= 0) {
            String argument = trimmed.substring(split + 1).trim();
            command.arguments.add(argument);
        }
        return command;
    }
    public CommandLine addArgument(String value) { arguments.add(value); return this; }
    public String getExecutable() { return executable; }
    public String[] getArguments() { return arguments.toArray(String[]::new); }
    public String[] toStrings() {
        String[] result = new String[arguments.size() + 1];
        result[0] = executable;
        for (int i = 0; i < arguments.size(); i++) {
            String value = arguments.get(i);
            result[i + 1] = value.indexOf(' ') >= 0 ? "\"" + value + "\"" : value;
        }
        return result;
    }
}
JAVA
cat > src/main/java/org/apache/commons/exec/util/StringUtils.java <<'JAVA'
package org.apache.commons.exec.util;
public final class StringUtils {
    private StringUtils() {}
    public static String quoteArgument(String value) { return value.indexOf(' ') >= 0 ? "\"" + value + "\"" : value; }
    public static boolean isQuoted(String value) { return value.length() >= 2 && ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))); }
    public static String fixFileSeparatorChar(String value) { return value.replace('\\', '/'); }
    public static String[] split(String value, String separator) { return value.split(separator); }
    public static String toString(String[] values, String separator) { return String.join(separator, values); }
    public static StringBuffer stringSubstitution(String value, java.util.Map<? super String, ?> vars, boolean lenient) {
        StringBuilder result = new StringBuilder();
        int offset = 0;
        while (true) {
            int start = value.indexOf("${", offset);
            if (start < 0) { result.append(value, offset, value.length()); break; }
            result.append(value, offset, start);
            int end = value.indexOf('}', start + 2);
            if (end < 0) { result.append(value.substring(start)); break; }
            String name = value.substring(start + 2, end);
            Object replacement = vars.get(name);
            if (replacement == null) {
                if (!lenient) throw new java.util.NoSuchElementException(name);
                result.append(value, start, end + 1);
            } else {
                result.append(replacement);
            }
            offset = end + 1;
        }
        return new StringBuffer(result.toString());
    }
}
JAVA
