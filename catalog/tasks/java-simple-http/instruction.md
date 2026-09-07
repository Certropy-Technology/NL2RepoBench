# Introduction and Goals of the Simple HTTP Project

Simple HTTP provides a small Java HTTP wrapper. This task isolates deterministic value-object and utility behavior that can be implemented without making network requests.

## Natural Language Instruction (Prompt)

Create a Java Maven project implementing the bounded public API below. Preserve the exact package names, class names, method signatures, return types, and exception behavior. Place sources under `src/main/java/de/svenkubiak/http` and `src/main/java/de/svenkubiak/utils`. Do not implement HTTP request execution or TLS configuration.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies, plugins, profiles, repositories, modules, extensions, or custom test commands. The verifier compiles candidate code separately and owns grading, collection, JUnit, and reward reports.

## Simple HTTP Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/de/svenkubiak/
    ├── http/Result.java
    └── utils/Utils.java
```

The bounded slice contains `Result` response state and four deterministic `Utils` helpers. HTTP clients, sockets, TLS trust managers, and request execution are outside this task.

## API Usage Guide

### Core APIs

Implement `de.svenkubiak.http.Result` with these exact methods:

```java
public static Result create()
public Result withBody(String body)
public Result withBinaryBody(byte[] binaryBody)
public Result withStatus(int status)
public Result withHeader(String key, String value)
public String body()
public byte[] binaryBody()
public String header(String key)
public String error()
public int status()
public boolean isValid()
public boolean isValid(int... expectedStatus)
```

`create` returns a fresh result with body `""` and status `-1`. The `with*` methods mutate that result and return the same instance. `withBody` converts null and empty input to `""`; other strings are preserved. `withBinaryBody` stores bytes and `binaryBody` returns a defensive copy, or null before bytes are set. `withStatus` stores any integer. `withHeader` associates a key with a value and later `header` returns the value or null when absent. `error` returns the current body. `isValid()` recognizes the HTTP success statuses 200 through 208 and 226. The varargs overload returns true exactly when the current status equals at least one supplied expected status.

Implement these exact static methods on `de.svenkubiak.utils.Utils`:

```java
public static boolean isSuccessCode(int statusCode)
public static String getFormDataAsString(java.util.Map<String,String> formData)
public static String clean(String string)
public static java.net.URI toAllowedUri(String url) throws java.net.URISyntaxException
```

`isSuccessCode` is deterministic and returns true only for 200, 201, 202, 203, 204, 205, 206, 207, 208, and 226. `getFormDataAsString` URL-encodes each map key and value as UTF-8, joins entries with `&`, and preserves the map iteration order. `clean` removes every character except ASCII letters, digits, and spaces. `toAllowedUri` parses the input and accepts only `http` or `https` schemes, case-insensitively; null input raises `NullPointerException`, malformed input raises `URISyntaxException`, and another scheme raises `URISyntaxException`.

### Actual Usage Modes

Create a `Result`, chain setters, then inspect status, body, headers, binary bytes, and validity. Use `Utils` for status classification, form encoding, message cleaning, and URL scheme validation. All operations are local and deterministic.

### Supported Function Types

Support fresh mutable result instances, fluent setters, header lookup, defensive binary-array reads, status predicates, ordered form encoding, ASCII cleaning, and URI parsing. No network, filesystem, clock, thread, TLS, or external dependency behavior is required.

### Error Handling

Follow the Java standard-library exceptions described above. Do not silently accept unsupported URI schemes. A null body is normalized by `Result.withBody`, while null arguments to `Utils.clean`, `Utils.getFormDataAsString`, and `Result.withHeader` are not part of the supported domain.

## Detailed Implementation Nodes of Functions

### Node 1: Result creation and fluent state

`Result.create()` must return independent objects. Each fluent setter updates only its receiver and returns that same receiver.

### Node 2: Result body, headers, and bytes

Body normalization, header replacement, error aliasing, and defensive copies must remain observable through the getters.

### Node 3: Result status predicates

Default status is -1. The no-argument predicate uses the fixed success set, while the varargs predicate compares exact integer values.

### Node 4: Utility transformations

Implement UTF-8 form encoding with map order, removal-based ASCII cleaning, and strict HTTP(S) URI validation without performing a request.
