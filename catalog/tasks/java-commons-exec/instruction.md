## Project Description

Apache Commons Exec is a Java library for representing command lines and for
performing the small, deterministic string operations needed to construct
them. In this task, implement a bounded, standard-library-only slice of the
library for a single-module Maven project.

The target users are Java programs that need to build a command description,
split command text into executable and arguments, quote an individual
argument, or expand named placeholders in command text. The implementation is
an in-memory value and string API. It must not launch a process, inspect the
host environment, discover a shell, start a watchdog thread, or access a
network service.

### Natural Language Instruction

Create the project in an empty `workspace/` directory. Use the public package
names and class names shown in the API Usage Guide. The project must compile
with JDK 21 and Maven 3.9.11 while offline, and it must have no runtime Maven
dependencies. Keep production Java sources under `src/main/java`; do not put
the implementation in a test-only source tree or replace the Java API with a
command-line-only program.

Implement these capabilities as one coherent contract:

1. Construct `org.apache.commons.exec.CommandLine` with an executable and
   preserve the order of every accepted argument.
2. Parse command text with `CommandLine.parse(String)`, treating quoted
   regions as one argument and making the first token the executable.
3. Quote arguments deterministically through
   `org.apache.commons.exec.util.StringUtils.quoteArgument(String)`.
4. Split and join strings without changing token order, and normalize file
   separator characters through the documented utility methods.
5. Expand `${name}` placeholders with strict and lenient missing-variable
   behavior through `StringUtils.stringSubstitution`.

The public contract is intentionally smaller than the complete upstream
project. Process execution, platform launcher selection, environment lookup,
external commands, shell integration, logging, and timeout management are
outside this task and must not be added as hidden substitutes for the API.

## Supports

### Runtime and Build Configuration

Use the following fixed environment:

```text
Language: Java
Runtime: Temurin JDK 21.0.12+8
Package manager: Maven 3.9.11
Platform: Linux amd64, glibc
Network: no-network during agent, candidate, verifier, and Oracle execution
Runtime dependencies: none; use the Java standard library only
```

Create a single-module Maven project. A minimal `pom.xml` is required so
`mvn --offline validate` can inspect the project. The POM is build metadata,
not an alternate API entry point: do not add profiles, plugins, repositories,
modules, custom extensions, or dependency downloads to bypass the contract.
The implementation must compile from a clean workspace with the fixed JDK and
must not assume access to GitHub, Maven Central, DNS, or any other service.

### Project Directory Structure

Use this layout, rooted at `workspace/`:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── exec/
                            ├── CommandLine.java
                            └── util/
                                └── StringUtils.java
```

`CommandLine.java` must declare package `org.apache.commons.exec` and
`StringUtils.java` must declare package `org.apache.commons.exec.util`.
There is no required CLI, shell script, resource directory, process runner,
or service entry point. If an additional file is necessary for Maven
metadata, keep it in the root and do not expose unlisted public behavior.

### Module Imports

Client code should be able to compile these imports:

```java
import java.util.Map;
import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.util.StringUtils;
```

Only the API described below is confidently bindable from the task-local
inventory. Other upstream Commons Exec classes and methods are intentionally
not part of this specification; their signatures are not confidently
bindable from the available local source bytes and must be omitted.

## API Usage Guide

### `org.apache.commons.exec.CommandLine` class

`CommandLine` is the mutable in-memory command representation. It stores one
executable string and an ordered sequence of argument strings. It does not
execute the represented command and must not create a process as a side
effect. Calls on one instance must not reorder arguments or consult global
state.

#### `CommandLine(String executable)`

Signature:

```java
public CommandLine(String executable)
```

The constructor accepts the executable text used as the first command token.
The normal input is a non-empty executable such as `"java"` or `"tool"`.
Preserve the supplied executable as the command identity; do not resolve it
through `PATH`. Invalid null or empty executable input must follow the class's
unchecked argument-validation behavior rather than being silently replaced.
The constructor has no filesystem, process, network, or environment side
effect.

Normal example:

```java
CommandLine command = new CommandLine("java");
String executable = command.getExecutable();
// executable is "java"
```

Edge example: constructing with an empty or null executable is invalid input;
the implementation must reject it consistently instead of creating a command
whose executable is missing.

#### `CommandLine.parse(String line)`

Signature:

```java
public static CommandLine parse(String line)
```

Parse whitespace-separated command text. The first parsed token becomes the
executable and later tokens become arguments in source order. Matching single
or double quotes group whitespace into one token; the quote delimiters are
syntax and are not separate tokens. The result is a new `CommandLine` and the
method does not mutate caller-owned state or run the command.

Normal example:

```java
CommandLine command = CommandLine.parse("tool --name \"hello world\"");
String[] args = command.getArguments();
// args contains "--name" followed by "hello world"
```

Edge example: `CommandLine.parse("tool 'two words'")` preserves the grouped
argument as one item. Null, blank, or unbalanced-quote input is invalid and
must produce the implementation's documented unchecked argument exception;
do not silently drop a non-quoted fragment.

#### `addArgument(String argument)`

Signature:

```java
public CommandLine addArgument(String argument)
```

Append one argument after all previously appended arguments and return this
same `CommandLine` instance for fluent use. A non-null argument remains one
logical argument even if it contains spaces; its serialized representation is
handled by the command's quoting rules. A null argument is ignored by the
bounded contract. The method changes only this object's in-memory argument
list and preserves insertion order.

Normal example:

```java
CommandLine command = new CommandLine("tool");
CommandLine returned = command.addArgument("hello world");
// returned == command and the argument is after the executable
```

Edge example: calling `addArgument(null)` must not create a literal string
`"null"` and must not shift existing arguments. Repeated calls append in
exact call order.

#### `getExecutable()`

Signature:

```java
public String getExecutable()
```

Return the executable string stored by the constructor or parser. The return
value is a scalar `String`, is deterministic for an unchanged object, and has
no side effect. It must not return the first argument or a shell-expanded
value.

Normal example:

```java
CommandLine command = CommandLine.parse("git status");
String executable = command.getExecutable();
// executable is "git"
```

Edge example: after adding arguments, `getExecutable()` remains unchanged;
adding `"--verbose"` must not change the executable to that argument.

#### `getArguments()`

Signature:

```java
public String[] getArguments()
```

Return the arguments in insertion or parse order, excluding the executable.
The result is an array whose element order is deterministic. Callers must be
able to inspect the result without changing the command's internal ordering;
do not expose a mutable internal collection as a substitute for the array.

Normal example:

```java
CommandLine command = CommandLine.parse("tool one \"two words\"");
String[] arguments = command.getArguments();
// arguments[0] is "one" and arguments[1] is "two words"
```

Edge example: a command with no arguments returns an empty array, not an array
containing the executable and not `null`. Repeated reads of an unchanged
command have the same values and order.

#### `toStrings()`

Signature:

```java
public String[] toStrings()
```

Return the complete command as an array whose first element is the executable
and whose remaining elements are serialized arguments in order. Arguments
requiring quoting must have a deterministic representation suitable for
passing as command tokens; this method does not launch a process or invoke a
shell.

Normal example:

```java
CommandLine command = new CommandLine("tool");
command.addArgument("hello world");
String[] tokens = command.toStrings();
// tokens[0] is "tool" and tokens[1] is a quoted form of the argument
```

Edge example: empty argument lists still return an array containing exactly
the executable. Two calls on an unchanged object must produce equal token
values in equal order.

### `org.apache.commons.exec.util.StringUtils` class

`StringUtils` contains static helpers for command-line strings. These methods
are pure with respect to files, processes, environment variables, and network
services. They must preserve deterministic source order and use the fixed
platform only where separator normalization explicitly requires it.

#### `quoteArgument(String argument)`

Signature:

```java
public static String quoteArgument(String argument)
```

Trim surrounding whitespace as required by the utility contract, then return
the argument unchanged when quoting is unnecessary or return a deterministic
quoted representation when spaces or special quote characters require it.
Use single quotes when the value contains double quotes, and double quotes
when it contains single quotes. An input containing both quote kinds cannot be
represented by this bounded quoting rule and must raise the documented
unchecked argument exception. Null handling must be consistent and must not
produce the text `"null"` accidentally.

Normal example:

```java
String quoted = StringUtils.quoteArgument("hello world");
```

Edge examples include `StringUtils.quoteArgument("plain")`, which does not
need a space-quoting wrapper, and a value containing both `'` and `"`, which
must be rejected rather than quoted ambiguously.

#### `isQuoted(String argument)`

Signature:

```java
public static boolean isQuoted(String argument)
```

Return whether the supplied value has matching single-quote or double-quote
delimiters according to the utility's quote detection rules. This is a pure
boolean query; it must not strip delimiters, mutate the input, or interpret
shell syntax beyond the documented outer delimiters.

Normal example:

```java
boolean quoted = StringUtils.isQuoted("\"hello world\"");
```

Edge example: a string with only one delimiter, or with mismatched first and
last delimiters, is not a correctly quoted value. Empty and null inputs must
follow the method's unchecked/null contract consistently.

#### `fixFileSeparatorChar(String argument)`

Signature:

```java
public static String fixFileSeparatorChar(String argument)
```

Normalize slash and backslash separators to the current Java platform file
separator. Return a string value and do not touch the filesystem. Preserve
non-separator characters, repeated separators, and token order.

Normal example:

```java
String normalized = StringUtils.fixFileSeparatorChar("a/b\\c");
```

Edge example: `"name"` has no separators and should remain unchanged. A path
containing repeated separators must not be interpreted as a real path or
canonicalized through filesystem access.

#### `split(String input, String separator)`

Signature:

```java
public static String[] split(String input, String separator)
```

Split the input using the supplied separator and return the resulting tokens
in their original order. The method is a string operation, not command-line
parsing and not regular-expression matching unless that is explicitly part of
the Java implementation's separator contract. It must not reorder or sort
tokens.

Normal example:

```java
String[] parts = StringUtils.split("a,b,c", ",");
// parts are "a", "b", and "c"
```

Edge example: an empty input or separator must follow the utility's defined
empty-input behavior and must not cause an unrelated filesystem or locale
lookup. Preserve empty fields only where the underlying public contract says
they are meaningful.

#### `toString(String[] strings, String separator)`

Signature:

```java
public static String toString(String[] strings, String separator)
```

Join the supplied array in its existing order, inserting the separator between
adjacent elements, and return one `String`. This method does not sort, quote,
or mutate the array. It must be deterministic for the same array contents and
separator.

Normal example:

```java
String joined = StringUtils.toString(new String[] {"a", "b", "c"}, ":");
// joined is the separator-joined representation
```

Edge example: a zero-length array has no elements to join. Null arrays,
null elements, and null separators must follow the utility's unchecked input
contract; do not silently substitute an unrelated delimiter.

#### `stringSubstitution(String input, Map<? super String, ?> variables, boolean isLenient)`

Signature:

```java
public static StringBuffer stringSubstitution(
    String input,
    Map<? super String, ?> variables,
    boolean isLenient)
```

Replace `${name}` placeholders using the supplied map and return a mutable
`StringBuffer` containing the expanded text. Convert replacement values using
their normal string representation. Do not mutate the map, perform
environment lookup, or access a file. Replacement order follows the input
text from left to right and repeated placeholders are handled consistently.

With `isLenient == false`, an unknown variable or malformed delimiter is an
error and must be reported through the method's unchecked substitution
exception behavior. With `isLenient == true`, an unresolved placeholder is
preserved rather than replaced with an invented value. Null or empty input
returns an empty buffer under the bounded contract.

Normal example:

```java
StringBuffer expanded = StringUtils.stringSubstitution(
    "run ${name}", Map.of("name", "demo"), false);
// expanded contains "run demo"
```

Edge examples include a missing key in lenient mode, which preserves its
placeholder, and a malformed `${` sequence in strict mode, which must not be
silently truncated. A null map must not be populated as a side effect.

### Actual Usage Modes

Construct and inspect a command without executing it:

```java
CommandLine command = new CommandLine("java");
command.addArgument("-version");
String[] tokens = command.toStrings();
```

Parse a quoted command and then inspect the stable token sequence:

```java
CommandLine command = CommandLine.parse(
    "tool --label \"hello world\"");
String executable = command.getExecutable();
String[] arguments = command.getArguments();
```

Build a command fragment after substitution without starting a child process:

```java
StringBuffer text = StringUtils.stringSubstitution(
    "tool --root ${root}", Map.of("root", "/opt/app"), false);
CommandLine command = CommandLine.parse(text.toString());
```

### Supported Function Types

The supported function types are command representation, quote-aware command
parsing, argument serialization, argument quoting, quote detection, file
separator normalization, ordered string splitting and joining, and map-based
placeholder substitution. All supported behavior is synchronous and local to
the calling JVM.

### Error Handling and Boundaries

Reject null, blank, malformed, or otherwise invalid inputs according to the
individual method contracts above. Do not convert an invalid command into an
empty command, do not reorder valid tokens, and do not swallow strict
substitution failures. Checked exceptions are not part of the selected API
signatures; report invalid arguments through the corresponding unchecked
library behavior.

No API in this task launches `Runtime.exec`, `ProcessBuilder`, a shell, or a
watchdog. No API reads `PATH`, home directories, locale configuration, or
environment variables. No API performs network I/O. These exclusions are
cross-cutting requirements, not optional implementation choices.

## Implementation Notes

Keep the implementation deterministic across repeated calls and independent
of hash-map iteration order wherever the input is an ordered command or
string. `CommandLine` state must remain local to each instance. Mutating one
instance must not mutate arrays or maps supplied by the caller, and inspection
methods must not expose internal mutable state in a way that changes later
results.

Parsing and serialization are related but distinct operations: parsing removes
recognized grouping delimiters to form logical arguments, while `toStrings()`
must return tokens that retain enough quoting to represent spaces safely. Do
not execute a shell to obtain either result.

Substitution must occur only through the explicit map supplied by the caller.
Replacement values may contain spaces and must remain values that the parser
can process according to the documented command-text contract. Strict and
lenient modes must differ only in their handling of unresolved or malformed
placeholders, not in the treatment of known values.

Use only JDK APIs and keep Maven runtime dependencies empty. The fixed Linux
platform is relevant to `fixFileSeparatorChar`, but the implementation must
not read or canonicalize actual filesystem paths. Preserve Unicode text as
Java strings and avoid locale-dependent case or sorting behavior.

Small verifiable examples:

1. `CommandLine.parse("tool one two")` has executable `tool` and arguments in
   the order `one`, `two`.
2. `CommandLine.parse("tool \"two words\"")` has exactly one argument for
   `two words`, not two whitespace-separated arguments.
3. `StringUtils.toString(new String[] {"left", "right"}, ":")` joins the two
   values without changing their order.
4. Strict substitution of `"run ${missing}"` with an empty map fails, while
   lenient substitution preserves the unresolved placeholder.

Do not copy an upstream implementation verbatim, add private verifier
protocols, mention hidden test names, or rely on the unavailable source
archive path. The source archive is not materialized in the task-local
workspace used for this instruction handoff, so any public class or method
not listed in this document is not confidently bindable and must not be
invented. The deliverable is the Maven project and the listed public API only.
