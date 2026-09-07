## Project Description

Recreate the bounded public value contract from the Hub4j GitHub API project.
The task contains one Java enum: `org.kohsuke.github.GHCommitState`.
It represents four deterministic commit-status values. This is a small,
compilable Java source task, not a complete GitHub client.

Create this source file:

```text
workspace/src/main/java/org/kohsuke/github/GHCommitState.java
```

The file must declare the exact package and public enum name. Declare these
constants in exactly this order:

```java
ERROR, FAILURE, PENDING, SUCCESS
```

Declaration order is part of the contract because Java assigns enum ordinals
from that order and `values()` returns the same order.

This bounded task must not implement a GitHub HTTP client, authentication,
credentials, REST requests, JSON mapping, repositories, commits, users,
status transitions, or any other Hub4j type. Do not add a command-line app.

The enum is a stateless value type. It performs no file I/O, network access,
environment inspection, clock access, random generation, or global mutation.

### Natural Language Instruction

Implement the public Java enum described in this document. A caller must be
able to import `org.kohsuke.github.GHCommitState`, use the four declared
constants, enumerate them in their fixed order, and perform exact-name lookup
with the standard Java enum behavior. Keep the implementation limited to the
specified source file and do not implement unrelated GitHub functionality.

## Supports

### Runtime and build environment

Use Temurin Java `21.0.12+8` on Linux amd64 with glibc. Maven `3.9.11` is
available for offline metadata validation. The source must compile with the
Java standard library alone.

Execution is offline. Do not configure repositories, dependency downloads,
plugins, profiles, modules, or build-time network access. A candidate POM may
contain project metadata only; no external dependency is needed or allowed.

### Project Directory Structure

Use this workspace layout:

```text
workspace/
└── src/
    └── main/
        └── java/
            └── org/
                └── kohsuke/
                    └── github/
                        └── GHCommitState.java
```

The source begins with:

```java
package org.kohsuke.github;
```

Callers import the public type as follows:

```java
import org.kohsuke.github.GHCommitState;
```

### Dependency and side-effect boundary

The implementation uses no runtime dependency beyond `java.lang.Enum`, which
Java supplies automatically for enums. Do not import JSON, HTTP, logging,
collection, or test libraries. Loading the class and calling its API must be
deterministic in an offline process.

### CLI boundary

This task defines no CLI, executable main class, shell command, or argument
format. Do not invent one. A separate caller should compile and invoke the
public type.

## API Usage Guide

The complete requested surface is the enum and its standard public methods.
Do not add application methods, public fields, constructors, aliases, or
additional project types.

### `GHCommitState`

Import the exact full package path:

```java
import org.kohsuke.github.GHCommitState;
```

Declare the type with exactly these constants:

```java
public enum GHCommitState {
    ERROR,
    FAILURE,
    PENDING,
    SUCCESS
}
```

Each constant is a singleton enum value. The accepted value domain is exactly
the four declared identifiers. Constants have no parameters, mutable fields,
external resources, or side effects.

Normal example:

```java
GHCommitState state = GHCommitState.SUCCESS;
```

Edge example:

```java
GHCommitState first = GHCommitState.ERROR;
GHCommitState last = GHCommitState.SUCCESS;
```

There are no `UNKNOWN`, `CANCELLED`, or other additional states.

### `values()`

The compiler-generated public static method has this signature:

```java
public static GHCommitState[] values()
```

It accepts no arguments and returns a new `GHCommitState[]` containing all
four constants in declaration order: `ERROR`, `FAILURE`, `PENDING`,
`SUCCESS`. Its length is always four. It performs no I/O and changes no
state.

Normal example:

```java
GHCommitState[] states = GHCommitState.values();
String firstName = states[0].name();
// firstName is "ERROR"
```

Edge example:

```java
GHCommitState[] states = GHCommitState.values();
states[0] = GHCommitState.SUCCESS;
String stillFirst = GHCommitState.values()[0].name();
// stillFirst is "ERROR"
```

Each call exposes an array that may be mutated by its caller without changing
the result of a later call. The result is ordered and deterministic.

### `valueOf(String)`

The compiler-generated public static lookup method has this signature:

```java
public static GHCommitState valueOf(String name)
```

Its input must be a non-null string exactly equal to one of the four constant
names. Matching is case-sensitive. The method does not trim whitespace,
fold case, accept aliases, or interpret alternate wire values.

Normal example:

```java
GHCommitState pending = GHCommitState.valueOf("PENDING");
```

The result is the declared `GHCommitState.PENDING` singleton. Lookup is
deterministic and has no I/O or other side effect.

Edge example:

```java
GHCommitState first = GHCommitState.valueOf("ERROR");
```

The following inputs are invalid and must not silently convert:

```java
GHCommitState.valueOf("pending");   // lowercase spelling
GHCommitState.valueOf(" PENDING");  // leading whitespace
GHCommitState.valueOf("UNKNOWN");   // undeclared name
```

For a non-null string that is not an exact name, Java throws
`IllegalArgumentException`. For null, Java throws `NullPointerException`.
No fallback value is returned.

### `name()`

The inherited public final instance method has this signature:

```java
public final String name()
```

It accepts no arguments and returns the exact source identifier of the
receiver: `"ERROR"`, `"FAILURE"`, `"PENDING"`, or `"SUCCESS"`. The result
is deterministic and does not change the receiver.

Normal example:

```java
String wireName = GHCommitState.FAILURE.name();
// wireName is "FAILURE"
```

Edge example:

```java
String boundaryName = GHCommitState.SUCCESS.name();
// boundaryName is "SUCCESS"
```

### `ordinal()`

The inherited public final instance method has this signature:

```java
public final int ordinal()
```

It accepts no arguments and returns the zero-based declaration position. The
required mapping is `ERROR -> 0`, `FAILURE -> 1`, `PENDING -> 2`, and
`SUCCESS -> 3`. It performs no I/O and has no side effects.

Normal example:

```java
int pendingOrdinal = GHCommitState.PENDING.ordinal();
// pendingOrdinal is 2
```

Edge example:

```java
int firstOrdinal = GHCommitState.ERROR.ordinal();
int lastOrdinal = GHCommitState.SUCCESS.ordinal();
// firstOrdinal is 0 and lastOrdinal is 3
```

### API boundary summary

The task documents only the constants, `values()`, `valueOf(String)`,
`name()`, and `ordinal()`. Do not customize inherited behavior or override
`toString()`, `equals(Object)`, or `hashCode()`. Do not add a CLI.

## Implementation Notes

1. Use package `org.kohsuke.github` exactly.
2. Use public enum type `GHCommitState` exactly.
3. Declare `ERROR`, `FAILURE`, `PENDING`, `SUCCESS` in that order.
4. Do not add a fifth constant or an `UNKNOWN` fallback.
5. Do not add custom fields, constructors, methods, aliases, or annotations.
6. Let Java provide the standard enum operations.
7. Preserve uppercase spelling exactly.
8. Do not trim or transform lookup input.
9. Do not add JSON or GitHub wire-protocol adapters.
10. Do not depend on a network service or GitHub client.
11. Do not use mutable static collections or caches.
12. Do not read configuration at class-load time.
13. Keep the source compatible with Java 21.
14. Keep the source under the specified `src/main/java` path.
15. A metadata-only POM is acceptable; no dependency is required.

These small checks should hold:

```java
GHCommitState.values().length == 4;
GHCommitState.values()[0] == GHCommitState.ERROR;
GHCommitState.valueOf("SUCCESS") == GHCommitState.SUCCESS;
GHCommitState.FAILURE.name().equals("FAILURE");
GHCommitState.PENDING.ordinal() == 2;
```

Also confirm the invalid-input contract:

```java
GHCommitState.valueOf("pending");   // throws IllegalArgumentException
GHCommitState.valueOf(" PENDING");  // throws IllegalArgumentException
GHCommitState.valueOf(null);        // throws NullPointerException
```

Confirm array isolation by replacing an element in one `values()` result and
checking that a fresh result still starts with `GHCommitState.ERROR` and
contains all four constants in the fixed order.

Keep implementation decisions limited to the public enum contract above.
Do not copy an upstream implementation, expose private tests, depend on
verifier internals, or add undocumented project behavior.
