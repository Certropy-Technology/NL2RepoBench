# Introduction and Goals of the Commons CLI Project

Apache Commons CLI is a Java library for describing command-line options and
parsing argument arrays into a queryable `CommandLine` result. This task
implements a bounded, deterministic slice of that behavior: option creation,
short and long option registration, required arguments, positional arguments,
value lookup, and parse errors. The result must be a normal single-module
Maven project using the public `org.apache.commons.cli` package.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons CLI that implements the
following public behavior:

1. Create flag and value-taking options using `Option.builder` and register
   them in an `Options` collection.
2. Support short names such as `-v` and long names such as `--verbose`.
3. Parse arguments with `DefaultParser` and expose presence and values through
   `CommandLine`.
4. Preserve positional arguments in their original order.
5. Enforce required options and required option arguments, reporting invalid
   input through the public `ParseException` hierarchy.
6. Keep the implementation under `src/main/java` in a single-module Maven
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

## Commons CLI Project Architecture

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
                        └── cli
                            ├── CommandLine.java
                            ├── CommandLineParser.java
                            ├── DefaultParser.java
                            ├── Option.java
                            ├── Options.java
                            └── ParseException.java
```

The candidate POM is metadata only. Do not use candidate-controlled build
plugins, dependencies, profiles, repositories, modules, or custom extensions.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
```

#### 2. Option.builder - Define an Option

```java
Option verbose = Option.builder("v")
    .longOpt("verbose")
    .desc("enable verbose output")
    .get();
Option output = Option.builder("o")
    .longOpt("output")
    .hasArg()
    .required()
    .get();
```

Signatures used by this contract:

```java
static Option.Builder builder(String option)
Option.Builder longOpt(String longOption)
Option.Builder hasArg()
Option.Builder required()
Option.Builder desc(String description)
Option get()
```

The builder preserves the short name, optional long name, argument requirement,
required flag, and description in the resulting option.

#### 3. Options.addOption - Register Options

```java
Options options = new Options();
options.addOption(verbose);
options.addOption(output);
```

Signature:

```java
Options addOption(Option option)
```

The same option can be resolved by its short or long name after registration.

#### 4. DefaultParser.parse - Parse Arguments

```java
CommandLine commandLine = new DefaultParser().parse(
    options, new String[] {"--verbose", "--output", "result.txt", "input.csv"});
```

Signature:

```java
CommandLine parse(Options options, String[] arguments) throws ParseException
```

The parser recognizes short and long options, consumes required values, and
keeps non-option arguments as positional arguments. Invalid input raises the
appropriate `ParseException` subtype.

#### 5. CommandLine - Query Parsed Results

```java
boolean verboseEnabled = commandLine.hasOption("verbose");
String outputPath = commandLine.getOptionValue("o");
String[] positional = commandLine.getArgs();
```

Signatures:

```java
boolean hasOption(String optionName)
String getOptionValue(String optionName)
String[] getArgs()
List<String> getArgList()
```

`getOptionValue` returns the parsed value for a value-taking option and null
when the option is absent and no default is supplied. Positional arguments
retain source order.

### Actual Usage Modes

#### Basic Flag

```java
Options options = new Options();
options.addOption(Option.builder("v").longOpt("verbose").get());
CommandLine line = new DefaultParser().parse(options, new String[] {"--verbose"});
line.hasOption("v"); // true
```

#### Required Value

```java
Options options = new Options();
options.addOption(Option.builder("o").longOpt("output").hasArg().required().get());
CommandLine line = new DefaultParser().parse(
    options, new String[] {"-o", "report.txt"});
line.getOptionValue("output"); // "report.txt"
```

#### Positional Arguments

```java
CommandLine line = new DefaultParser().parse(
    options, new String[] {"input-a", "input-b"});
line.getArgList(); // ["input-a", "input-b"]
```

### Supported Function Types

The supported function types are option builder configuration, option
registration, short/long name resolution, default argument parsing, presence
and value lookup, positional argument collection, and parse error handling.
Do not implement unrelated help formatting, type conversion, legacy parser
variants, or Maven publishing behavior in place of this contract.

### Error Handling

Missing required options, missing values, and unrecognized options must fail
through the public `ParseException` hierarchy. Do not silently discard invalid
tokens or invent fallback values. Empty positional input is valid when no
required option is configured.

## Detailed Implementation Nodes of Functions

### Node 1: Option Construction

Preserve short names, long names, descriptions, argument requirements, and
required flags through the builder API.

### Node 2: Option Registration

Register options in `Options` and resolve them consistently by short and long
name, including the leading-hyphen forms accepted by the public API.

### Node 3: Flag Parsing

Parse boolean flags without consuming the following positional token as a
value.

### Node 4: Value Parsing

Consume the next argument for a required value option and expose exactly that
string through `getOptionValue`.

### Node 5: Long and Short Forms

Support both `-o value` and `--output value` for an option configured with both
names, preserving equivalent results.

### Node 6: Positional Arguments

Collect non-option tokens in source order through both `getArgs()` and
`getArgList()`.

### Node 7: Parse Exceptions

Reject missing required options, missing option values, and unknown options with
the public `ParseException` contract.

### Node 8: Offline Maven Layout

Use the exact public package and standard Maven source layout. Compile with
Java 21, use no external runtime dependency, and do not access the network or
candidate-controlled Maven configuration.
