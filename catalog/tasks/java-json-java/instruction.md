# Introduction and Goals of the JSON-java Project

JSON-java is a small Java library for deterministic JSON text processing. This task focuses on the self-contained `JSONObject.quote(String)` string encoder. Create a normal single-module Maven project from an empty workspace and expose the documented public API without external runtime dependencies.

## Natural Language Instruction (Prompt)

Create a Java Maven project named JSON-java. Implement the public `JSONObject` class described below. The project must compile with Java 21, use the exact package name, and keep production code under `src/main/java`. Do not copy the upstream project, add unrelated JSON-java classes, or use network access at build or run time.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compiler and runtime
Maven 3.9.11                # offline metadata validation
Linux amd64 / glibc         # fixed platform
Runtime dependencies: none  # java.lang and java.io-compatible behavior only
Network access: unavailable # candidate and verifier execution is offline
```

The candidate `pom.xml` is metadata only. It may contain the model version, coordinates, packaging, and harmless project metadata, but must not contain dependencies, plugins, profiles, repositories, modules, extensions, or custom build instructions.

## JSON-java Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/org/json/JSONObject.java
```

Use a single Maven module and the exact public class and package above. No generated sources or test implementation is required in the candidate project.

## API Usage Guide

### Core APIs

#### JSONObject class

Import the class as follows:

```java
import org.json.JSONObject;
```

The class must be public and provide the static method below. No constructor or other public API is part of this task.

#### quote(String)

Signature:

```java
public static String quote(String string)
```

The method returns a JSON string literal surrounded by double quotes. A `null` reference and an empty string both return exactly `"\"\""` (two quote characters in the returned value). For non-empty input, preserve ordinary characters and escape JSON-significant characters. Escape a double quote as `\"`, a backslash as `\\`, and a slash immediately preceded by `<` as `<\/` in the returned literal. Escape backspace, tab, newline, form feed, and carriage return as `\b`, `\t`, `\n`, `\f`, and `\r`. Other control characters and the ranges U+0080 through U+009F and U+2000 through U+20FF are represented as lowercase four-digit `\uXXXX` sequences. Characters outside those ranges are preserved, including supplementary characters as their original UTF-16 code units.

Examples:

```java
JSONObject.quote("");       // "\"\""
JSONObject.quote(null);      // "\"\""
JSONObject.quote("a\"b");   // "\"a\\\"b\""
JSONObject.quote("</");     // "\"<\\/\""
JSONObject.quote("A\nB");   // "\"A\\nB\""
JSONObject.quote("\u0088"); // "\"\\u0088\""
```

The input is read only, the method has no observable state, performs no I/O, and returns the same result for repeated calls with the same input. The returned string is newly produced and contains no unescaped JSON quote or backslash.

### Actual Usage Modes

Use this method when embedding a Java string as one JSON string value, including text with punctuation, HTML-like `</` sequences, line breaks, and control characters. The input may contain any UTF-16 `char` values. This bounded task does not include parsing JSON, object mutation, XML conversion, HTTP helpers, reflection, files, or collection APIs.

### Supported Function Types

The supported behavior is limited to the static `JSONObject.quote(String)` method. Do not add alternate overloads, constructors used as a service, global configuration, random behavior, locale behavior, or network behavior.

### Error Handling

`null` is valid input and is treated exactly like the empty string, returning `"\"\""`. There are no checked exceptions and no sentinel error result. All other inputs, including strings containing control characters, quotes, backslashes, slashes, Unicode characters, and supplementary characters, must return a JSON string literal.

## Detailed Implementation Nodes of Functions

### Node 1: Exact public surface

Provide public `org.json.JSONObject` and exact `public static String quote(String)`; keep unrelated public surface out of scope.

### Node 2: Literal boundaries

Return a two-quote JSON literal for null and empty input. For non-empty input, begin and end with one unescaped double quote.

### Node 3: Character escaping

Process input left to right. Escape quotes and backslashes, apply the five named control escapes, and escape `<`-preceded slash for safe JSON text delivery in HTML contexts.

### Node 4: Unicode behavior

Use four lowercase hexadecimal digits for required Unicode escapes. Preserve characters outside the specified escape ranges, including UTF-16 surrogate units.

### Node 5: Determinism and state

Do not mutate input, retain input between calls, use locale or randomness, or perform I/O. Results depend only on the current argument.

### Node 6: Boundary behavior

Cover null, empty, ordinary ASCII, embedded quote, backslash, `<` followed by slash, each named control character, a generic control character, U+0088, U+1234, and a supplementary character.

### Node 7: Offline Maven layout

Use the standard source layout, Java 21, a metadata-only candidate POM, and no third-party dependency. The project must remain buildable in a no-network environment.
