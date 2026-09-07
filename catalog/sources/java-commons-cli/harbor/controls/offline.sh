#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'offline control uses the verifier network namespace'
mkdir -p src/main/java/org/apache/commons/cli
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>offline</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/cli/Option.java <<'JAVA'
package org.apache.commons.cli;
public final class Option {
    final String shortName; String longName; boolean hasArgument; boolean isRequired;
    private Option(String name) { shortName = name; }
    public static Builder builder(String name) { return new Builder(name); }
    public static final class Builder {
        private final Option option;
        Builder(String name) { option = new Option(name); }
        public Builder longOpt(String value) { option.longName = value; return this; }
        public Builder hasArg() { option.hasArgument = true; return this; }
        public Builder required() { option.isRequired = true; return this; }
        public Option get() { return option; }
    }
}
JAVA
cat > src/main/java/org/apache/commons/cli/Options.java <<'JAVA'
package org.apache.commons.cli;
import java.util.ArrayList; import java.util.List;
public final class Options {
    final List<Option> values = new ArrayList<>();
    public Options addOption(Option option) { values.add(option); return this; }
}
JAVA
cat > src/main/java/org/apache/commons/cli/CommandLine.java <<'JAVA'
package org.apache.commons.cli;
import java.util.*;
public final class CommandLine {
    final Set<String> present = new HashSet<>(); final Map<String,String> optionValues = new HashMap<>(); final List<String> args = new ArrayList<>();
    public boolean hasOption(String name) { return present.contains(name); }
    public String getOptionValue(String name) { return optionValues.get(name); }
    public String[] getArgs() { return args.toArray(String[]::new); }
}
JAVA
cat > src/main/java/org/apache/commons/cli/ParseException.java <<'JAVA'
package org.apache.commons.cli;
public class ParseException extends Exception { public ParseException(String message) { super(message); } }
JAVA
cat > src/main/java/org/apache/commons/cli/MissingOptionException.java <<'JAVA'
package org.apache.commons.cli;
public final class MissingOptionException extends ParseException { public MissingOptionException() { super("missing required option"); } }
JAVA
cat > src/main/java/org/apache/commons/cli/DefaultParser.java <<'JAVA'
package org.apache.commons.cli;
public final class DefaultParser {
    public CommandLine parse(Options options, String[] arguments) throws ParseException {
        CommandLine result = new CommandLine();
        for (int index = 0; index < arguments.length; index++) {
            String token = arguments[index]; Option match = null;
            for (Option option : options.values) if (token.equals("-" + option.shortName) || token.equals("--" + option.longName)) { match = option; break; }
            if (match == null) { result.args.add(token); continue; }
            result.present.add(match.shortName); if (match.longName != null) result.present.add(match.longName);
            if (match.hasArgument && index + 1 < arguments.length) {
                String value = arguments[++index]; result.optionValues.put(match.shortName, value); if (match.longName != null) result.optionValues.put(match.longName, value);
            }
        }
        for (Option option : options.values) if (option.isRequired && !result.present.contains(option.shortName)) throw new MissingOptionException();
        return result;
    }
}
JAVA
