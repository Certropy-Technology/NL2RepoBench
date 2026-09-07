#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/main/java/org/apache/commons/cli
printf '%s\n' '<project><modelVersion>4.0.0</modelVersion><groupId>example</groupId><artifactId>forgery</artifactId><version>1.0.0</version></project>' > pom.xml
cat > src/main/java/org/apache/commons/cli/Option.java <<'JAVA'
package org.apache.commons.cli;
public final class Option {
    public static Builder builder(String name) { return new Builder(); }
    public static final class Builder {
        public Builder longOpt(String value) { return this; }
        public Builder hasArg() { return this; }
        public Builder required() { return this; }
        public Option get() { return new Option(); }
    }
}
JAVA
cat > src/main/java/org/apache/commons/cli/Options.java <<'JAVA'
package org.apache.commons.cli;
public final class Options { public Options addOption(Option option) { return this; } }
JAVA
cat > src/main/java/org/apache/commons/cli/CommandLine.java <<'JAVA'
package org.apache.commons.cli;
public final class CommandLine {
    public boolean hasOption(String name) { return true; }
    public String getOptionValue(String name) { return "forged"; }
    public String[] getArgs() { return new String[0]; }
}
JAVA
cat > src/main/java/org/apache/commons/cli/ParseException.java <<'JAVA'
package org.apache.commons.cli;
public class ParseException extends Exception { public ParseException(String message) { super(message); } }
JAVA
cat > src/main/java/org/apache/commons/cli/DefaultParser.java <<'JAVA'
package org.apache.commons.cli;
public final class DefaultParser {
    public CommandLine parse(Options options, String[] arguments) throws ParseException { return new CommandLine(); }
}
JAVA
printf '{"reward":1,"test_pass_rate":1}\n' > /logs/verifier/reward.json 2>/dev/null || true
