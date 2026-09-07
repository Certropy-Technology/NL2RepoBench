# Introduction and Goals of the GitHub API Project

## Natural Language Instruction (Prompt)

Implement the bounded public API slice below from the Hub4j GitHub API project. Create `org.kohsuke.github.GHCommitState` as a Java enum. This task concerns only deterministic commit-status values; do not implement a GitHub client, HTTP calls, authentication, JSON handling, or any other project types.

## Environment Configuration

The environment is Linux amd64 with Temurin JDK `21.0.12+8` and Maven `3.9.11`. All execution is offline. Maven is available only for candidate metadata validation. A candidate `pom.xml` may contain safe project metadata, but must not configure dependencies, plugins, repositories, profiles, modules, or build execution.

### Core Dependency Library Versions

The required implementation uses the Java 21 standard library only. No external Maven dependency is needed or allowed for this bounded slice.

## GitHub API Project Architecture

The upstream project exposes GitHub REST API domain objects in `org.kohsuke.github`. The selected type is an isolated value enum used to represent a commit's state. It has no mutable state, no I/O, and no connection to a GitHub service.

### Project Directory Structure

Place the implementation at:

```text
src/main/java/org/kohsuke/github/GHCommitState.java
```

## API Usage Guide

### Core APIs

Import the type with:

```java
import org.kohsuke.github.GHCommitState;
```

Implement exactly:

```java
public enum GHCommitState {
    ERROR, FAILURE, PENDING, SUCCESS
}
```

As a Java enum, the standard compiler-generated methods are part of the contract:

```java
public static GHCommitState[] values()
public static GHCommitState valueOf(String name)
public String name()
public int ordinal()
```

`values()` returns a new array ordered by declaration: `ERROR`, `FAILURE`, `PENDING`, `SUCCESS`. `name()` returns the exact uppercase identifier. The ordinal values are zero through three in that same order.

### Actual Usage Modes

```java
GHCommitState state = GHCommitState.SUCCESS;
String wireValue = state.name();              // "SUCCESS"
GHCommitState parsed = GHCommitState.valueOf("PENDING");
GHCommitState[] all = GHCommitState.values(); // ERROR, FAILURE, PENDING, SUCCESS
```

### Supported Function Types

The enum represents only these four values. It does not perform case folding, alias mapping, JSON serialization, network access, or status transitions.

### Error Handling

`GHCommitState.valueOf(null)` throws `NullPointerException`. `GHCommitState.valueOf` throws `IllegalArgumentException` for a string that is not one of the exact uppercase names, including lowercase names and strings with whitespace. Mutating the array returned by `values()` must not change a later `values()` call.

## Detailed Implementation Nodes of Functions

1. Declare the exact package `org.kohsuke.github`.
2. Declare `GHCommitState` as an enum, not a class with constants.
3. Preserve the four declaration names and their order exactly.
4. Do not add constructors, fields, methods, aliases, or external dependencies. Java supplies the required enum operations and exception behavior.
