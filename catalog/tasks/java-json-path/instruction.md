# Introduction and Goals of the JsonPath Project

JsonPath provides a compact path language for selecting locations in JSON-like
documents. This task isolates deterministic path compilation and its
definiteness query. Implement a normal single-module Maven project using the
exact public package names below; JSON parsing, providers, mapping, mutation,
filesystem access, and network clients are outside this task.

## Natural Language Instruction (Prompt)

Create a Java Maven project implementing the bounded `JsonPath` API. The
compiled object preserves normalized path text and reports whether the path can
select at most one location. A path is definite when each step is one root,
property, or single numeric array index.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64 / glibc
Runtime dependencies: none
Network: unavailable during candidate, verifier, Oracle, and controls
```

The candidate `pom.xml` is metadata only. Do not add dependencies, plugins,
profiles, repositories, modules, or custom Maven extensions.

## JsonPath Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/com/jayway/jsonpath/
    ├── JsonPath.java
    ├── InvalidPathException.java
    └── Predicate.java
```

`Predicate` is the public filter placeholder accepted by the compiler; this
bounded contract does not invoke or inspect predicate objects.

## API Usage Guide

### Core APIs

#### Compile a path

```java
JsonPath path = JsonPath.compile("$.store.book[0].title");
```

Signature: `public static JsonPath compile(String jsonPath, Predicate... filters)`.
Input must be non-null and non-empty after trimming. It may begin with `$` or
`@`; a path without either marker is interpreted below `$`. Accepted segments
are dot properties, bracket-quoted properties, single non-negative indexes,
`*`, `..`, comma-separated indexes, slices, filter expressions, and
function-like suffixes. `filters` is accepted but not evaluated here.

Null or blank input, a trailing dot, or malformed bracket syntax throws
`InvalidPathException`.

#### Inspect compiled text

`public String getPath()` returns the normalized path. Surrounding whitespace
is removed and a bare property expression receives the `$.` prefix. Repeated
calls are deterministic and side-effect free.

#### Ask whether a path is definite

`public boolean isDefinite()` and `public static boolean isPathDefinite(String path)`
return true only for roots, property segments, and single non-negative indexes.
Scan (`..`), wildcard, multiple indexes, slice, filter, and function forms are
false. The static method has the same validation and exception behavior as
`compile(path).isDefinite()`.

### Actual Usage Modes

```java
JsonPath definite = JsonPath.compile("$.store.book[0].title");
definite.getPath();    // "$.store.book[0].title"
definite.isDefinite(); // true
JsonPath.compile("$.store.book[*].title").isDefinite(); // false
JsonPath.compile("store.book").getPath(); // "$.store.book"
```

### Supported Function Types

Support path normalization, syntax validation, deterministic text, and
definiteness classification. Reading JSON, evaluating predicates, mapping,
mutation, serialization, providers, caching, and URL/file/stream overloads
are excluded.

### Error Handling

Throw unchecked `InvalidPathException` for null, empty, blank, trailing-dot,
or malformed path input. Do not silently accept malformed brackets or return a
null path. Predicate objects are not dereferenced.

## Detailed Implementation Nodes of Functions

### Context Normalization

Trim surrounding whitespace; preserve `$` and `@` contexts; prefix a bare
property expression with `$.`.

### Syntax Validation

Reject empty input and a final `.` or `..`. Bracket expressions must close and
represent a quoted property, integer index, wildcard, slice, comma-separated
indexes, or filter expression.

### Definiteness Classification

Only property segments and single non-negative indexes are definite. Scan,
wildcard, multiple indexes, slice, filter, and function forms are indefinite.

### Stable Object State

Store normalized text and classification once. Accessors must not depend on
locale, time, randomness, thread identity, or external resources.

### Static Convenience Query

`isPathDefinite` must use the same validation and classification rules as
`compile`, with no second source of truth.
