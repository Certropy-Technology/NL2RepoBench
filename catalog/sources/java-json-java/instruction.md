## Project Description

JSON-java is a small Java library for producing JSON string literals from Java
strings. This task is a bounded recreation of one deterministic, dependency-free
operation from the `org.json` package. The intended user is a Java developer who
needs to place one Java `String` value into JSON text without losing characters or
leaving JSON-significant characters unescaped.

The deliverable is a single Maven project created from an empty workspace. Its
public behavior is the `org.json.JSONObject.quote(String)` operation. The method
returns a new `String` containing one JSON string literal, including its opening
and closing double quotes.

The project accepts Java `String` references, including `null`, empty strings,
ordinary text, punctuation, line separators, control characters, Unicode BMP
characters, and UTF-16 surrogate code units. It returns text and performs no file,
environment, network, process, or global-state operation.

### Natural Language Instruction (Prompt)

Create a Java 21 Maven project named `json-java` from an empty workspace.
Implement the public class `org.json.JSONObject` and its static method
`quote(String)` exactly as described in the API Usage Guide below.

Keep production code at `src/main/java/org/json/JSONObject.java` and keep the
package declaration exactly `package org.json;`.

The method must return a JSON string literal for every Java `String` input,
including a null reference. Preserve ordinary characters in their original order.
Escape quotes, backslashes, the required HTML-sensitive slash case, named control
characters, and the specified Unicode ranges according to the public contract.

Use only the Java 21 standard library. The candidate project must not require a
runtime dependency, a Maven plugin, a repository, a profile, a module, or a
network connection.

Do not copy a larger upstream checkout or add unrelated JSON-java classes. Do not
implement JSON parsing, object storage, serialization of Java objects, reflection,
XML support, HTTP support, filesystem helpers, or a command-line interface.

### Scope and Exclusions

In scope is one public class and one public static operation:

- `org.json.JSONObject`
- `org.json.JSONObject.quote(String)`

The task does not require a JSON parser or a mutable JSON object model.
The task does not require a `JSONArray`, `JSONTokener`, or other `org.json` type.
The task does not require configuration, logging, caching, or service providers.
The task does not require command-line flags or an executable main class.
The task does not require a test source tree in the candidate project.

## Supports

### Runtime and Build Environment

Use the following environment contract:

| Item | Required value |
| --- | --- |
| Language | Java |
| Runtime | Temurin JDK 21.0.12+8 |
| Compiler target | Java 21 (`--release 21`) |
| Package manager | Apache Maven 3.9.11 |
| Platform | Linux amd64 |
| C library | glibc |
| Runtime dependencies | None beyond the JDK |
| Network mode | No network during agent, build, candidate, or verifier execution |

The project is a single Maven module. Maven metadata may identify the project,
but the POM must remain metadata-only for this task. A minimal POM may contain
the model version, group ID, artifact ID, version, and packaging.

Do not declare dependencies, plugins, profiles, repositories, modules,
extensions, or custom build instructions in `pom.xml`. The implementation may
use `java.lang.String`, `StringBuilder`, primitive `char` operations, and other
JDK classes without declaring them as dependencies.

The implementation must compile with Java 21. It must not assume a locale,
timezone, filesystem layout, environment variable, external process, DNS
resolver, package registry, or source checkout is available.

### Project Directory Structure

Create this project layout, rooted at `workspace/`:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── json/
                    └── JSONObject.java
```

`pom.xml` is the single-module Maven metadata file. The Java source file must
declare the `org.json` package and the public `JSONObject` class. The source
layout must be Maven's standard `src/main/java` layout.

Do not add a second source root, generated source directory, resource directory,
module descriptor, shell script, executable entry point, or external library.
The directory tree and the API import path must remain consistent.

### Build and Installation Expectations

The project should be recognizable as a normal Maven project and should be
usable with an offline Maven invocation. A valid metadata-only POM is sufficient
for the bounded implementation; no dependency download is expected.

The implementation must be available to Java callers after compilation. A caller
may compile a small client with the project's compiled classes and import
`org.json.JSONObject` directly.

No installation-time network access is allowed. No API call may write a file or
contact a service. The method must work when invoked repeatedly in one JVM.

## API Usage Guide

### `org.json.JSONObject` Class

Import the class with its complete package path:

```java
import org.json.JSONObject;
```

The class is public and belongs to the `org.json` package. It is a stateless
namespace for the supported quote operation. Do not add unrelated public methods,
fields, overloads, or mutable configuration.

The source contract supplies a public class with the ordinary public no-argument
class construction behavior. Callers do not need to construct an instance to use
the supported operation; the documented operation is static.

### `JSONObject.quote(String)`

Complete signature:

```java
public static String quote(final String string)
```

The `final` parameter modifier is an implementation-level constraint and does
not change the Java call signature. The method accepts one nullable Java
`String` reference and returns one non-null Java `String`.

The returned value is a JSON string literal. It begins with a double quote and
ends with a double quote. The boundary quotes are part of the returned value,
not merely formatting around it.

For a null input reference, return exactly the two-character Java string whose
contents are `""`. Treat null the same as an empty input string.

For an empty input string, return exactly the same two-character value `""`.
The result is still a Java `String` and must not be a null sentinel.

For ordinary characters that do not require escaping, preserve each input
character and its original order inside the surrounding quotes. Do not trim,
normalize, lowercase, uppercase, transliterate, or otherwise rewrite text.

### Quote and Backslash Escaping

Escape an input double quote (`"`) as the two-character JSON escape `\"` in
the returned literal. For example:

```java
String result = JSONObject.quote("a\"b");
// result is "\"a\\\"b\""
```

Escape an input backslash (`\\`) as `\\\\` in the returned literal. The result
must not contain an input backslash as an unescaped JSON backslash.

```java
String result = JSONObject.quote("a\\b");
// result is "\"a\\\\b\""
```

The quote and backslash escapes preserve the logical input character while
ensuring that the resulting literal remains syntactically safe as JSON text.

### Slash After Less-Than Escaping

When an input slash (`/`) is immediately preceded in the input by a less-than
character (`<`), prefix that slash with a backslash in the returned literal.
Thus the input sequence `</` is represented as `<\/` inside the JSON literal.

```java
String result = JSONObject.quote("</");
// result is "\"<\\/\""
```

Only the immediately preceding input character controls this special case. A
slash not immediately preceded by `<` is preserved as `/`.

```java
String result = JSONObject.quote("a/b");
// result is "\"a/b\""
```

The special slash behavior is text escaping behavior; it does not perform HTML
encoding and does not alter any other less-than character.

### Named Control Character Escapes

Use the short JSON-style escape for each of these input characters:

| Input character | Returned escape |
| --- | --- |
| backspace U+0008 | `\\b` |
| horizontal tab U+0009 | `\\t` |
| line feed U+000A | `\\n` |
| form feed U+000C | `\\f` |
| carriage return U+000D | `\\r` |

For example:

```java
String result = JSONObject.quote("A\nB\tC");
// result is "\"A\\nB\\tC\""
```

These escapes represent the input control characters; do not emit a literal
line break or tab for them inside the returned JSON text.

### Unicode and Other Control Escapes

For every input character below U+0020 that is not one of the five named
controls, emit a lowercase four-digit Unicode escape in the form `\\uXXXX`.
The four hexadecimal digits must be zero-padded when necessary.

Also emit a lowercase four-digit Unicode escape for characters in U+0080 through
U+009F, inclusive, and for characters in U+2000 through U+20FF, inclusive.

Examples:

```java
String control = JSONObject.quote("\u0001");
// control is "\"\\u0001\""

String c1 = JSONObject.quote("\u0088");
// c1 is "\"\\u0088\""

String c2 = JSONObject.quote("\u2000");
// c2 is "\"\\u2000\""
```

Use lowercase hexadecimal letters (`a` through `f`) in these escapes. Do not
emit a variable-width escape, an uppercase hexadecimal escape, or an octal
escape.

Characters outside the specified ranges are preserved. In particular, U+1234
is not in the U+2000..U+20FF range and therefore remains as the original
character:

```java
String result = JSONObject.quote("\u1234");
// result contains the original U+1234 character between the quote boundaries
```

### UTF-16 and Supplementary Characters

The input domain is Java's UTF-16 `String` domain. Process the input as Java
`char` values in their existing order. Do not decode, normalize, replace, or
drop surrogate code units.

A supplementary character represented by a valid surrogate pair is preserved as
the same pair because neither surrogate is in a required escape range.

```java
String input = "\uD83D\uDE00";
String result = JSONObject.quote(input);
// result is the two original UTF-16 code units surrounded by quotes
```

An isolated surrogate code unit is likewise part of the Java input domain and
must be handled deterministically without an exception or replacement policy
being invented by the implementation.

### Return Shape, Ordering, and State

The return type is always `String`. For non-null input, the content is one
opening quote, the escaped or preserved input characters in left-to-right
order, and one closing quote.

The method must not reorder characters, remove duplicates, trim whitespace, or
perform Unicode normalization. It must return the same text for repeated calls
with equal input strings.

The input object is read only. The method must not mutate or retain the input,
modify static state, consult a clock or random source, or depend on locale.

The method performs no I/O, does not create files, launches no process, and makes
no network request. It has no observable side effect beyond allocation of its
returned string.

### Exceptions and Invalid Inputs

`null` is a valid input and is not an error. Empty strings, punctuation, quotes,
backslashes, slash characters, control characters, all Java `char` values,
Unicode text, and surrogate code units are valid inputs.

The documented contract declares no checked exception and no sentinel error
return. No input in the supported Java `String` domain should be rejected by
adding an undocumented validation rule.

### Small API Examples

The following ordinary call preserves plain text:

```java
String plain = JSONObject.quote("hello/world");
// plain is "\"hello/world\""
```

The following boundary calls return the same empty JSON string literal:

```java
String fromNull = JSONObject.quote(null);
String fromEmpty = JSONObject.quote("");
// fromNull.equals(fromEmpty) is true, and both contents are ""
```

The following call combines multiple independent escape categories:

```java
String mixed = JSONObject.quote("</a\"b\\c\n");
// mixed starts and ends with quotes and contains <\\/, \\", \\\\, and \\n+```

## Implementation Notes

### Public Surface and Package Boundaries

Keep the source in the exact `org.json` package. The class name is
`JSONObject`, with the capitalization shown in the import path. The supported
static method takes exactly one `String` parameter and returns exactly one
`String`.

Do not add alternate overloads such as `quote(Object)`, `quote(CharSequence)`,
or `quote(String, ...)`. Do not expose a mutable encoder object, configuration
field, or additional JSON type as a substitute for the required method.

### Left-to-Right Character Processing

The observable output follows the input's left-to-right Java `char` order. An
implementation may use any internal buffering strategy that produces this
contract, but it must preserve that order and must inspect the immediately
preceding input character for the special `</` case.

The special slash decision is based on adjacent input characters, not on the
already escaped output. A less-than character remains ordinary, while the slash
that follows it receives the additional backslash.

### Determinism

Equal input strings must produce equal output text in every invocation. The
result must not vary with locale, platform path, current time, thread schedule,
randomness, or JVM-global configuration.

The method should be safe to invoke repeatedly and concurrently because its
contract contains no mutable shared state. No cache is necessary and no cache
may change the observable result.

### Maven and Offline Constraints

Use standard Maven source layout and Java 21-compatible syntax. Keep the POM
minimal and dependency-free. The project must remain buildable when Maven is
run in offline mode with no package registry or source host available.

Do not solve a build problem by adding a repository, downloading an artifact at
runtime, or embedding a larger project. The JDK supplies all required types.

### Verifiable Behavior Examples

These examples are small public-behavior checks, not an implementation recipe:

```java
JSONObject.quote(null)       // "\"\""
JSONObject.quote("")         // "\"\""
JSONObject.quote("plain")   // "\"plain\""
JSONObject.quote("a\"b")    // "\"a\\\"b\""
```

```java
JSONObject.quote("a\\b")     // "\"a\\\\b\""
JSONObject.quote("</")       // "\"<\\/\""
JSONObject.quote("A\r\nB")  // "\"A\\r\\nB\""
JSONObject.quote("\u0088")  // "\"\\u0088\""
```

```java
JSONObject.quote("\u0000")   // "\"\\u0000\""
JSONObject.quote("\u1234")  // original U+1234 between quote boundaries
JSONObject.quote("\uD83D\uDE00") // original surrogate pair between boundaries
```

### Error and Resource Boundaries

Do not turn valid null or Unicode input into an exception. Do not silently
replace unsupported characters, because all Java `String` values are within the
specified input domain.

Do not write diagnostics into the returned string, standard output, standard
error, a file, or a network connection. Do not expose a test-only protocol or
grader-specific behavior in the public class.

The implementation must not depend on a candidate-side test directory or on
files outside `workspace/`. Its only required observable result is the returned
Java string.

### Completion Checklist

Before considering the project complete, confirm that the package declaration,
class name, method name, parameter type, and return type exactly match this
specification.

Confirm that null and empty inputs produce the same two-quote value.
Confirm that quotes and backslashes are escaped.
Confirm that only a slash immediately following `<` receives the special slash
escape.
Confirm the five named control escapes and lowercase four-digit Unicode escapes.
Confirm preservation of ordinary Unicode and supplementary UTF-16 characters.
Confirm deterministic repeated calls and absence of I/O or network behavior.
Confirm that the Maven project uses Java 21 and has no external dependency.
