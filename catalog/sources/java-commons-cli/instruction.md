## Project Description

Create a small, single-module Java Maven project that recreates the bounded
option-definition and argument-parsing contract of Apache Commons CLI.

The project is for callers that need to declare command-line options and then
inspect parsed flags, option values, and positional arguments.

The public package is `org.apache.commons.cli`.

The implementation must be usable from ordinary Java code compiled with JDK
21.

The project must support the following observable workflow:

1. Build a flag or value-taking `Option` with its builder.
2. Add the option to an `Options` registry.
3. Parse a `String[]` argument vector with `DefaultParser`.
4. Query the resulting `CommandLine` for presence, values, and positional
   arguments.
5. Reject invalid input with the public `ParseException` contract.

Keep this task focused on option declaration and deterministic parsing.

The implementation must preserve short option names such as `v` and long
option names such as `verbose`.

An option may be a flag, or it may consume one following argument as its
value.

Required options and required option arguments must be enforced.

Non-option tokens must remain available as positional arguments in their
original order.

Do not silently discard unknown options, missing values, or missing required
options.

Do not implement unrelated help rendering, type conversion, legacy parser
variants, Maven publishing, or a network-backed package service.

The implementation boundary is the public API described in this document.
Private upstream classes and behavior outside that boundary are not required.

## Supports

### Natural Language Instruction

Create the project from an empty `workspace/` directory.

Use a normal single-module Maven layout with production sources under
`src/main/java`.

Put the public implementation in the exact package `org.apache.commons.cli`.

Provide the public classes named in the API Usage Guide.

Make the implementation compile with Java 21 and Maven 3.9.11.

The candidate POM is metadata only. Do not rely on candidate-controlled Maven
plugins, profiles, repositories, modules, or extensions.

The runtime implementation must use only the Java standard library.

No third-party runtime dependency is needed for this bounded contract.

### Environment Configuration

The fixed runtime is Temurin JDK `21.0.12+8`.

The fixed build tool is Apache Maven `3.9.11`.

The target platform is Linux `amd64` with glibc.

Agent, candidate, verifier, Oracle, and controls run with no network access.

Do not access GitHub, Maven Central, DNS, or any external service at runtime.

The Maven project must work with offline validation and no downloaded runtime
dependency.

Use a Java release level compatible with JDK 21.

The expected project is one Maven module, not a Maven reactor.

### Project Directory Structure

Create this structure under the supplied workspace:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── cli/
                            ├── CommandLine.java
                            ├── CommandLineParser.java
                            ├── DefaultParser.java
                            ├── Option.java
                            ├── Options.java
                            └── ParseException.java
```

`pom.xml` must describe a single Java Maven project.

The package declarations in the six public source files must be
`org.apache.commons.cli`.

The source file names must match their public class names.

No public API file may be placed outside the package tree shown above.

## API Usage Guide

### `Option.builder`: construct an option

Import the type with:

```java
import org.apache.commons.cli.Option;
```

The factory signature is:

```java
public static Option.Builder builder(String option)
```

`option` is the short option name without its leading hyphen.

For example, `"v"` represents `-v`.

The returned `Option.Builder` is mutable builder state and is completed with
`get()`.

The builder method signatures used by this contract are:

```java
public Builder longOpt(String longOption)
public Builder hasArg()
public Builder required()
public Builder desc(String description)
public Option get()
```

`longOpt` accepts the long name without its leading two hyphens.

`hasArg` marks the option as consuming one argument value.

`required` marks the option as required during parsing.

`desc` stores descriptive metadata and does not change parsing semantics.

`get` returns the configured `Option`.

The builder methods return the same builder type so calls can be chained.

Normal example:

```java
Option verbose = Option.builder("v")
    .longOpt("verbose")
    .desc("enable verbose output")
    .get();
```

The resulting option is a flag with short name `v` and long name `verbose`.

Value-taking example:

```java
Option output = Option.builder("o")
    .longOpt("output")
    .hasArg()
    .required()
    .get();
```

The resulting option requires one value and must be present in a successful
parse.

Edge behavior: a builder configured with only a short name is valid and must
still be resolvable by that short name.

Do not add implicit names, invented defaults, or type conversion to the
builder contract.

### `Options.addOption`: register options

Import the registry with:

```java
import org.apache.commons.cli.Options;
```

Construct an empty registry with:

```java
public Options()
```

Register an option with:

```java
public Options addOption(Option option)
```

The `option` argument is the `Option` returned by `Option.Builder.get()`.

The method returns the `Options` registry so registration can be chained when
the implementation supports that ordinary usage.

Normal example:

```java
Options options = new Options();
options.addOption(verbose);
options.addOption(output);
```

After registration, an option configured with both names must be addressable
by either its short name or its long name during parsing and querying.

Registration order must not change the meaning of a previously registered
distinct option.

The registry is in-memory object state; `addOption` must not write files,
read the environment, or access the network.

Edge behavior: an empty `Options` registry is valid to construct, but parsing
an unknown option against it must fail rather than silently accept the token.

### `DefaultParser.parse`: parse an argument vector

Import the parser with:

```java
import org.apache.commons.cli.DefaultParser;
```

Construct a parser with:

```java
public DefaultParser()
```

Parse with:

```java
public CommandLine parse(Options options, String[] arguments)
    throws ParseException
```

`options` supplies the recognized short and long option definitions.

`arguments` is the ordered command-line token vector, excluding the program
name.

The returned value is a new `CommandLine` containing the parse result.

For a flag, the parser records presence without consuming the next positional
token as a value.

For an option marked with `hasArg`, the parser consumes its required following
value and preserves that value as a string.

Both `-o value` and `--output value` must work when the option has short name
`o` and long name `output`.

Normal example:

```java
Options options = new Options();
options.addOption(Option.builder("v").longOpt("verbose").get());
options.addOption(Option.builder("o").longOpt("output").hasArg().get());
CommandLine line = new DefaultParser().parse(
    options,
    new String[] {"--verbose", "--output", "report.txt", "input.csv"});
```

This result reports the flag, the output value, and one positional input.

The parser must preserve positional tokens in source order.

Edge example: parsing `new String[] {"--unknown"}` against a registry that
does not contain `unknown` must throw a `ParseException` rather than return a
partial result.

Missing values and missing required options are also parse failures.

Parsing must be deterministic: equal option definitions and equal argument
arrays produce equivalent query results without using time, randomness,
locale, environment variables, or network state.

The parser must not mutate the caller's `String[]` contents.

### `CommandLine`: query a successful parse

Import the result type with:

```java
import org.apache.commons.cli.CommandLine;
```

Check option presence with:

```java
public boolean hasOption(String optionName)
```

`optionName` is a registered short or long name without its leading hyphens.

The return value is `true` when that option was present in the parsed input.

For an absent option it is `false`.

Normal example:

```java
boolean enabled = line.hasOption("verbose");
boolean alsoEnabled = line.hasOption("v");
```

When both names identify one registered option, both queries report the same
presence state.

Get an option value with:

```java
public String getOptionValue(String optionName)
```

For a present value-taking option, the return value is its exact parsed
string, including ordinary punctuation and case.

For an absent option with no configured value, the return value is `null`.

Normal example:

```java
String outputPath = line.getOptionValue("output");
```

The value is `"report.txt"` for the parse shown above.

Edge example: querying an absent optional option returns `null`; it must not
invent an empty string or a filesystem default.

Get positional arguments as an array with:

```java
public String[] getArgs()
```

The returned array contains every non-option token in original order.

Get the same positional sequence as a list with:

```java
public java.util.List<String> getArgList()
```

The list order must match `getArgs()` exactly.

Normal example:

```java
String[] args = line.getArgs();
java.util.List<String> argList = line.getArgList();
```

For input positional tokens `input-a` and `input-b`, the array and list are
`["input-a", "input-b"]` in that order.

Edge example: when there are no positional tokens, both accessors return an
empty sequence, not a sequence containing `null`.

Querying a `CommandLine` is in-memory and must not perform I/O or mutate the
parser's option definitions.

### `ParseException`: invalid input contract

Import the checked exception type with:

```java
import org.apache.commons.cli.ParseException;
```

`DefaultParser.parse` declares:

```java
throws ParseException
```

Throw this public exception hierarchy for an unrecognized option, a missing
value for an option marked with `hasArg`, or a missing required option.

The exception must be observable by the caller and must not be replaced by a
silent fallback result.

Normal handling example:

```java
try {
    CommandLine line = new DefaultParser().parse(options, argv);
} catch (ParseException error) {
    // Report invalid command-line input to the caller.
}
```

Edge behavior: an empty positional argument vector is valid when the option
registry has no required option and no option token is missing a value.

Do not expose private verifier details or depend on a particular unchecked
exception when the public `ParseException` contract applies.

## Implementation Notes

Keep all public classes in `org.apache.commons.cli` and keep the Maven source
layout identical to the directory tree in `Supports`.

Use only standard-library facilities and deterministic in-memory data
structures.

Short and long aliases for one option must remain equivalent throughout
registration, parsing, and querying.

A flag must not consume a following positional token.

An argument-taking option must consume exactly its value token and leave later
non-option tokens available through the positional accessors.

Required-option checks happen before returning a successful `CommandLine`.

Unknown options, missing values, and missing required options must not produce
partial successful results.

Preserve the exact spelling and contents of option values; do not normalize
paths, case, whitespace, or punctuation.

Preserve positional argument order exactly as supplied by the caller.

Repeated calls to query methods on one result must be stable.

Equivalent parsing of short and long aliases must produce equivalent values
and presence states.

Do not use network access, process execution, wall-clock time, randomness,
locale-sensitive behavior, or environment-dependent defaults.

The POM must remain a single-module build descriptor with no required runtime
dependency outside the JDK.

Small verifiable examples:

```java
Options flags = new Options();
flags.addOption(Option.builder("v").longOpt("verbose").get());
CommandLine flagLine = new DefaultParser().parse(
    flags, new String[] {"--verbose", "input.txt"});
// hasOption("v") is true and getArgs() is ["input.txt"].
```

```java
Options values = new Options();
values.addOption(Option.builder("o").longOpt("output").hasArg().get());
CommandLine valueLine = new DefaultParser().parse(
    values, new String[] {"-o", "report.txt", "a.csv", "b.csv"});
// getOptionValue("output") is "report.txt" and args stay ordered.
```

```java
Options required = new Options();
required.addOption(Option.builder("o").hasArg().required().get());
// Parsing an empty vector raises ParseException because -o is required.
```

```java
Options unknown = new Options();
// Parsing ["--not-declared"] raises ParseException.
```

These examples describe observable behavior; they do not prescribe an
algorithm or a particular internal representation.

Before finishing, verify the project with offline Maven validation and a
clean Java compilation using the fixed JDK 21 toolchain.

Do not copy upstream source, upstream tests, hidden assertions, verifier
protocols, or private artifact references into the project or this instruction.

If a behavior is outside the five evidence-backed contract areas described
above, it is not confidently bindable for this task and should be omitted
rather than guessed.
