# Introduction and Goals of the Jackson Annotations Project

Jackson Annotations supplies small Java annotations used to declare JSON-facing
metadata. This task recreates the deterministic creator declaration slice:
`JsonCreator`, its nested `Mode` enum, and the `JacksonAnnotation` marker.
It does not implement JSON parsing, serialization, object mapping, or any
Jackson module outside this annotation metadata.

## Natural Language Instruction (Prompt)

Create a single-module Java Maven project that provides
`com.fasterxml.jackson.annotation.JsonCreator` and
`com.fasterxml.jackson.annotation.JacksonAnnotation`. Recreate the exact
annotation metadata and nested `JsonCreator.Mode` enum described below. Keep
implementation source under `src/main/java` and use only the Java standard
library.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11 (offline metadata validation)
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies,
plugins, profiles, repositories, modules, extensions, or custom test commands.
The verifier compiles the candidate in a separate JVM and owns all grading
reports.

## Jackson Annotations Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/com/fasterxml/jackson/annotation/
    ├── JacksonAnnotation.java
    └── JsonCreator.java
```

The contract contains only annotation declarations and reflection-visible
metadata. It does not require a filesystem, network, native library, or an
external Maven artifact.

## API Usage Guide

### Core APIs

#### `JacksonAnnotation`

```java
package com.fasterxml.jackson.annotation;

public @interface JacksonAnnotation
```

`JacksonAnnotation` is a runtime-retained marker annotation. Its target is
only `ElementType.ANNOTATION_TYPE`. It declares no members and has no state.

#### `JsonCreator`

```java
package com.fasterxml.jackson.annotation;

public @interface JsonCreator {
    JsonCreator.Mode mode() default JsonCreator.Mode.DEFAULT;
}
```

`JsonCreator` is itself marked with `@JacksonAnnotation`. It has runtime
retention and may be applied only to an annotation type, a method, or a
constructor: `ElementType.ANNOTATION_TYPE`, `ElementType.METHOD`, and
`ElementType.CONSTRUCTOR`. The sole member has exactly the return type
`JsonCreator.Mode`, and its default is `Mode.DEFAULT`.

```java
import com.fasterxml.jackson.annotation.JsonCreator;

final class Entry {
    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    Entry(String name) { }
}
```

#### `JsonCreator.Mode`

```java
public enum JsonCreator.Mode {
    DEFAULT,
    DELEGATING,
    PROPERTIES,
    DISABLED
}
```

The constants occur in exactly this declaration order. Standard Java enum
behavior applies: `values()` returns a new array in declaration order;
`valueOf(String)` returns the exact matching constant and throws
`IllegalArgumentException` for an unknown name; null input follows normal JDK
enum behavior. The enum has no additional public methods in this task.

### Actual Usage Modes

Use `DEFAULT` when normal creator-selection heuristics should apply,
`DELEGATING` for a single delegated input, `PROPERTIES` for named creator
properties, and `DISABLED` to explicitly disable a creator. This task stores
only the metadata; it does not choose or invoke a constructor.

### Supported Function Types

Supported behavior is Java annotation declaration and reflection: retention,
target set, marker presence, a member default, enum ordering, enum lookup, and
reading an explicitly supplied `mode`. JSON binding, annotation scanning
frameworks, parameter-name inference, mix-ins, and serialization rules are
outside this contract.

### Error Handling

`JsonCreator.Mode.valueOf` must reject a name that is not one of the four exact
constant names with `IllegalArgumentException`. Do not add aliases, change the
enum order, or silently coerce invalid names. Annotation use outside the
declared Java target set must be rejected by normal Java compilation.

## Detailed Implementation Nodes of Functions

### Node 1: Marker annotation metadata

Declare `JacksonAnnotation` as a no-member annotation with runtime retention
and annotation-type-only target. Its purpose is metadata marking only.

### Node 2: Creator annotation metadata

Declare `JsonCreator` with runtime retention, the three supported targets, and
the `JacksonAnnotation` marker. It contains exactly one member named `mode`.

### Node 3: Default creator mode

The `mode()` member returns `JsonCreator.Mode` and defaults to `DEFAULT` when
an annotation use omits the member.

### Node 4: Creator mode constants

Expose `DEFAULT`, `DELEGATING`, `PROPERTIES`, and `DISABLED` in that order.
Do not replace the enum with strings or another type.

### Node 5: Explicit mode binding

An annotation use such as `@JsonCreator(mode = Mode.PROPERTIES)` must retain
the specified enum value so standard Java reflection reads `PROPERTIES`.

### Node 6: Enum lookup boundaries

Use normal Java enum lookup semantics. Exact names are accepted; an unknown
name is an error instead of a fallback to `DEFAULT`.

### Node 7: Determinism and state

All contract behavior is immutable declaration metadata. No API performs I/O,
uses time, reads environment state, or contacts a network service.

### Node 8: Offline build behavior

Keep the Maven dependency closure empty and do not download artifacts at run
time. The trusted verifier invokes candidate code through a JSON/JVM adapter;
it does not import candidate classes into its own process.
