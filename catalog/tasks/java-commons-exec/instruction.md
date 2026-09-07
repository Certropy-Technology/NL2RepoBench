# Introduction and Goals of the Commons Exec Project

Apache Commons Exec is a Java library for constructing command lines and
reliably launching external processes. This task focuses on a deterministic,
portable public slice: command-line tokenization and quoting plus the small
string substitution helpers used by command construction. Process launching,
platform-specific launcher selection, environment discovery, and watchdog
threads are outside this task's contract.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Exec that implements the
following public behavior:

1. Construct a `CommandLine` from an executable and add individual or grouped
   arguments.
2. Parse whitespace-separated command text, honoring single and double quotes.
3. Return executable and argument arrays with deterministic quoting for spaces
   and embedded quote characters.
4. Support variable substitution in command text using a map, including strict
   and lenient handling of missing variables.
5. Provide the public `StringUtils` helpers for quoting, quote detection,
   separator normalization, splitting, and joining.
6. Keep all implementation under `src/main/java` in a single-module Maven
   project. Do not add external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime
Maven 3.9.11                # Offline project tooling
Linux amd64                 # Fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # Agent and verifier are offline
```

## Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── commons
                        └── exec
                            ├── CommandLine.java
                            └── util
                                └── StringUtils.java
```

The public packages are `org.apache.commons.exec` and
`org.apache.commons.exec.util`. The candidate POM is metadata only; do not use
plugins, repositories, dependencies, profiles, modules, or custom extensions
to control the verifier.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import java.util.Map;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.util.StringUtils;
```

#### 2. CommandLine.parse() - Parse Command Text

```java
CommandLine command = CommandLine.parse("tool --name \"hello world\"");
```

Signatures:

```java
static CommandLine parse(String line)
static CommandLine parse(String line, Map<String, ?> substitutionMap)
```

The first token becomes the executable. Single- and double-quoted groups are
one argument, and unmatched quotes or null/blank command text follow the
public `IllegalArgumentException` contract.

#### 3. CommandLine Construction and Arguments

```java
CommandLine command = new CommandLine("tool");
command.addArgument("hello world");
command.addArguments("--mode fast");
String executable = command.getExecutable();
String[] arguments = command.getArguments();
String[] tokens = command.toStrings();
```

Signatures:

```java
CommandLine(String executable)
CommandLine addArgument(String argument)
CommandLine addArgument(String argument, boolean handleQuoting)
CommandLine addArguments(String arguments)
CommandLine addArguments(String[] arguments)
String getExecutable()
String[] getArguments()
String[] toStrings()
```

Null individual arguments are ignored. Arguments containing spaces are quoted
when quoting is enabled. `toString()` presents the command as a deterministic
bracketed token list.

#### 4. StringUtils.quoteArgument() - Quote One Argument

```java
String value = StringUtils.quoteArgument("hello world");
```

Signature:

```java
static String quoteArgument(String argument)
```

Trim surrounding whitespace and add quotes only when needed. An argument with
double quotes uses single quotes; an argument with single quotes uses double
quotes; both quote kinds together raise `IllegalArgumentException`.

#### 5. StringUtils.isQuoted() and fixFileSeparatorChar()

```java
boolean quoted = StringUtils.isQuoted("\"hello\"");
String normalized = StringUtils.fixFileSeparatorChar("a/b\\c");
```

Signatures:

```java
static boolean isQuoted(String argument)
static String fixFileSeparatorChar(String argument)
```

`isQuoted` recognizes matching single or double quote delimiters. Separator
normalization maps both slash forms to the current platform separator.

#### 6. StringUtils.split() and toString()

```java
String[] words = StringUtils.split("a,b,c", ",");
String joined = StringUtils.toString(words, ":");
```

Signatures:

```java
static String[] split(String input, String separator)
static String toString(String[] strings, String separator)
```

Splitting returns tokens in source order. Joining inserts the supplied
separator between tokens.

#### 7. StringUtils.stringSubstitution() - Expand Variables

```java
String result = StringUtils.stringSubstitution(
    "${HOME}/bin/${tool}", Map.of("HOME", "/opt", "tool", "run"), false
).toString();
```

Signature:

```java
static StringBuffer stringSubstitution(
    String input, Map<? super String, ?> variables, boolean isLenient)
```

Replace `${name}` placeholders. In strict mode an unknown variable or malformed
delimiter raises a runtime exception; lenient mode preserves an unresolved
placeholder. Null or empty input returns an empty `StringBuffer`.

### Actual Usage Modes

#### Basic Command Construction

```java
CommandLine command = new CommandLine("java");
command.addArgument("-version");
System.out.println(command.toStrings()[0]);
```

#### Quoted Command Parsing

```java
CommandLine command = CommandLine.parse("tool 'hello world' \"fast mode\"");
// toStrings() contains tool, "hello world", and "fast mode".
```

#### Template Expansion

```java
Map<String, String> values = Map.of("name", "demo");
StringBuffer command = StringUtils.stringSubstitution("run ${name}", values, false);
```

### Supported Function Types

The supported function types are command tokenization, command argument
construction, deterministic quoting, separator normalization, token splitting
and joining, and map-based string substitution. Process execution and
platform-specific environment behavior are intentionally excluded.

### Error Handling

Null or blank commands, unbalanced quotes, conflicting quote characters,
missing variables in strict mode, and malformed substitution delimiters must
follow the public exception behavior. Do not silently discard non-null input or
reorder tokens.

## Detailed Implementation Nodes of Functions

### Node 1: Command Tokenization

Implement the quote-aware finite-state parsing used by `CommandLine.parse`,
including whitespace boundaries and unmatched-quote errors.

### Node 2: Argument Construction

Preserve executable order, ignore null arguments, support string and array
argument overloads, and return defensive arrays where required.

### Node 3: Argument Quoting

Apply the public single- versus double-quote rules for spaces and embedded quote
characters, including rejection of both quote kinds in one argument.

### Node 4: Variable Substitution

Expand valid `${name}` placeholders from the supplied map and distinguish strict
from lenient missing-variable behavior.

### Node 5: String Utilities

Implement quote detection, separator normalization, splitting, joining, and
the documented empty-input behavior.

### Node 6: Deterministic Output

Keep executable and argument order stable in `getArguments`, `toStrings`, and
`toString`; preserve spaces and non-ASCII characters.

### Node 7: Maven Project Layout

Use the exact public packages and standard source layout. Compile with Java 21
and no external runtime dependency.

### Node 8: Offline Build Behavior

Do not access the network or rely on candidate-controlled Maven configuration;
the implementation must work in the fixed offline verifier.
