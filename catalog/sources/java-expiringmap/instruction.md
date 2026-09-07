# Introduction and Goals of the ExpiringMap Project

This task recreates a small, deterministic Java value-object slice of
ExpiringMap. The project is intended for a caller that needs to carry a value,
an optional expiration policy, and optional duration metadata together. It is
not an implementation of the map, timer, listener, executor, or background
expiration system.

The public deliverable is a single-module Maven project whose public package is
`net.jodah.expiringmap`. The candidate must compile on the declared JDK and
must work without runtime network access or third-party dependencies.

## Project Description

The project models expiration metadata without performing expiration. A caller
can construct an `ExpiringValue<V>`, retrieve the exact fields later, compare
two values, use them as hash keys, and obtain a deterministic diagnostic string.
The value is generic and may be null. A duration is stored as supplied rather
than converted, rounded, decremented, or checked against the current clock.

The supported public types are:

- `net.jodah.expiringmap.ExpirationPolicy`, an enum with `ACCESSED` and
  `CREATED` constants.
- `net.jodah.expiringmap.ExpiringValue<V>`, an immutable-style metadata holder
  with the constructors and accessors specified below.

The input boundary is ordinary Java values, a `long` duration, an
`java.util.concurrent.TimeUnit`, and the two declared enum values. The output
boundary is the stored object identity, the stored metadata, Java equality and
hashing, and a stable string representation. No file, environment variable,
clock, thread, executor, network, database, or global state is part of the
contract.

The wider upstream ExpiringMap API is outside this task. Do not add map
storage, expiration scheduling, listeners, concurrency controls, cache
eviction, or a command-line interface. No public class or method beyond the
two types and the members documented here is confidently bindable from the
available task evidence, so those broader APIs should be omitted.

## Supports

### Natural Language Instruction

Create a normal Maven project with Java sources under
`src/main/java/net/jodah/expiringmap/`. Implement the two public types and
their exact public contracts. Keep the implementation within the Java
standard library. The project must provide:

1. The `ExpirationPolicy` enum with exactly the two supported policy constants.
2. The four `ExpiringValue<V>` construction forms, including the documented
   unset-field defaults and null-unit validation.
3. Direct accessors that return the stored fields without conversion or time
   calculations.
4. Null-safe value-object equality, a consistent hash code, and deterministic
   field-labelled string output.

Use the exact package and type names. Preserve generic values and their object
identity. Do not normalize a duration, replace a null with a default, or infer
expiration from the current time. The project has no CLI and no executable
entry point beyond ordinary Java class loading and method calls.

### Environment Configuration

The fixed build and execution environment is:

```text
JDK: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64 with glibc
Runtime dependencies: none
Network: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The root `pom.xml` is metadata for the Maven project. It must not introduce
dependencies, plugins, profiles, repositories, modules, extensions, or custom
commands for this task. Use the standard Maven source layout and Java 21
compilation settings required by the environment.

### Project Directory Structure

The created project must have this public shape:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── net/
                └── jodah/
                    └── expiringmap/
                        ├── ExpirationPolicy.java
                        └── ExpiringValue.java
```

`ExpirationPolicy.java` must declare the public enum. `ExpiringValue.java`
must declare the public generic class. There is no required resource
directory, test entry point, CLI script, configuration file, or external
service integration.

## API Usage Guide

### `net.jodah.expiringmap.ExpirationPolicy`

Declare the public enum at the exact import path:

```java
import net.jodah.expiringmap.ExpirationPolicy;
```

The enum has these constants and no other required constants:

```java
ExpirationPolicy.ACCESSED
ExpirationPolicy.CREATED
```

The constants are identity-stable enum values. They are metadata only. Reading
or storing one must not start a timer or modify any other state. A normal use
is `ExpirationPolicy.CREATED` when metadata describes time since construction.
An edge use is passing `null` as the policy to an `ExpiringValue`; the policy
constructor accepts that null and the accessor returns null.

### `ExpiringValue<V>` constructors

Import the generic class and the standard-library time unit:

```java
import net.jodah.expiringmap.ExpiringValue;
import net.jodah.expiringmap.ExpirationPolicy;
import java.util.concurrent.TimeUnit;
```

#### `public ExpiringValue(V value)`

The one-argument constructor accepts any reference value, including null. It
returns a new `ExpiringValue<V>` with `value` stored exactly, a null policy,
duration `-1L`, and a null time unit. It has no I/O, clock access, mutation of
the supplied value, or other side effect. It does not throw for a null value.

Normal example:

```java
ExpiringValue<String> item = new ExpiringValue<>("cached");
String value = item.getValue(); // "cached"
```

Edge example:

```java
ExpiringValue<Object> empty = new ExpiringValue<>(null);
// value == null, policy == null, duration == -1L, timeUnit == null
```

#### `public ExpiringValue(V value, ExpirationPolicy expirationPolicy)`

The policy constructor accepts any value and either enum policy or null. It
stores the value and policy exactly, while leaving duration at `-1L` and time
unit null. It performs no policy validation beyond Java's ordinary reference
semantics and does not schedule expiration.

Normal example:

```java
ExpiringValue<String> item =
    new ExpiringValue<>("session", ExpirationPolicy.ACCESSED);
```

Edge example:

```java
ExpiringValue<String> item = new ExpiringValue<>("session", null);
// getExpirationPolicy() returns null; no default policy is inserted
```

#### `public ExpiringValue(V value, long duration, TimeUnit timeUnit)`

The duration constructor accepts any value, any `long` including zero or a
negative number, and a non-null `java.util.concurrent.TimeUnit`. It stores the
exact duration and exact unit without conversion. If `timeUnit` is null, it
throws `NullPointerException` and does not produce an object. A null value is
otherwise valid.

Normal example:

```java
ExpiringValue<String> item =
    new ExpiringValue<>("token", 5L, TimeUnit.MINUTES);
```

Edge example:

```java
ExpiringValue<String> item =
    new ExpiringValue<>("token", -7L, TimeUnit.SECONDS);
// getDuration() remains -7L; it is not clamped or converted
```

Invalid example:

```java
new ExpiringValue<>("token", 1L, null); // throws NullPointerException
```

#### `public ExpiringValue(V value, ExpirationPolicy expirationPolicy, long duration, TimeUnit timeUnit)`

The full constructor stores all four supplied fields exactly. It accepts null
for `value` and `expirationPolicy`, accepts every `long`, and requires a
non-null `TimeUnit`. A null unit throws `NullPointerException`; no duration
conversion, range check, clock read, or background operation occurs.

Normal example:

```java
ExpiringValue<String> item = new ExpiringValue<>(
    "document", ExpirationPolicy.CREATED, 2L, TimeUnit.HOURS);
```

Edge example:

```java
new ExpiringValue<>(null, null, 0L, TimeUnit.NANOSECONDS);
// valid: null fields and a zero duration are retained
```

### `ExpiringValue<V>` accessors

#### `public V getValue()`

Returns the exact value reference supplied to the constructor. The return type
is the class type parameter `V`; null is returned when a null value was stored.
The call is deterministic and has no side effect.

```java
String value = new ExpiringValue<>("report").getValue();
Object absent = new ExpiringValue<>(null).getValue(); // null
```

#### `public ExpirationPolicy getExpirationPolicy()`

Returns the exact stored enum reference or null. It does not choose a default,
consult a map, or perform expiration.

```java
ExpirationPolicy p = new ExpiringValue<>("x", ExpirationPolicy.CREATED)
    .getExpirationPolicy();
```

#### `public long getDuration()`

Returns the exact stored `long`. Values from the basic constructors are
`-1L`; explicit zero, positive, and negative durations remain unchanged.

```java
long duration = new ExpiringValue<>("x", 0L, TimeUnit.SECONDS).getDuration();
// duration == 0L
```

#### `public TimeUnit getTimeUnit()`

Returns the exact stored `java.util.concurrent.TimeUnit` reference or null for
the constructors without a duration. The method does not convert the unit.

```java
TimeUnit unit = new ExpiringValue<>("x", 3L, TimeUnit.MILLISECONDS)
    .getTimeUnit();
```

### `ExpiringValue<V>` value-object methods

#### `public boolean equals(Object other)`

Equality is true only when `other` is the same concrete `ExpiringValue` type
and all four fields compare as specified: values use null-safe value equality,
policies use enum identity, durations use exact `long` equality, and time units
use identity. Null fields compare equal to corresponding null fields. Equality
is deterministic, does not mutate either object, and returns false for null or
an unrelated object.

```java
var left = new ExpiringValue<>("x", ExpirationPolicy.CREATED, 1L, TimeUnit.HOURS);
var right = new ExpiringValue<>("x", ExpirationPolicy.CREATED, 1L, TimeUnit.HOURS);
boolean same = left.equals(right); // true
```

An edge comparison with a different duration, unit, policy, or value is false;
two basic instances containing null fields can still be equal.

#### `public int hashCode()`

Returns a deterministic hash code consistent with `equals`. Equal objects must
have equal hash codes. The result is derived from the same four stored fields;
callers must not depend on a particular numeric value for unequal objects.
Calling it has no side effect.

```java
var a = new ExpiringValue<>("x", 1L, TimeUnit.SECONDS);
var b = new ExpiringValue<>("x", 1L, TimeUnit.SECONDS);
boolean consistent = a.equals(b) && a.hashCode() == b.hashCode();
```

#### `public String toString()`

Returns the stable field-labelled form:

```text
ExpiringValue{value=..., expirationPolicy=..., duration=..., timeUnit=...}
```

Each ellipsis is replaced by the ordinary string form of that stored field,
with `null` for null fields, and the field order is unchanged. It performs no
I/O or time calculation.

```java
String text = new ExpiringValue<>("x", 1L, TimeUnit.SECONDS).toString();
// ExpiringValue{value=x, expirationPolicy=null, duration=1, timeUnit=SECONDS}
```

For a null value, the string contains `value=null`; it must not omit the field.

## Implementation Notes

Keep both public types in the same `net.jodah.expiringmap` package so the
documented imports bind without adapters. The generic parameter belongs to
`ExpiringValue<V>` and must not be replaced by a raw or string-only design.

Store metadata in a way that preserves the supplied reference and primitive
values. The constructors without a duration use the documented sentinel and
null unit. The duration constructors validate the unit before returning and
otherwise retain the caller's exact duration and enum reference.

The contract is deliberately passive. Do not start threads, create executors,
read the system clock, perform unit conversion, mutate the supplied value, or
communicate with a map. Repeated accessor, equality, hash, and string calls
must be deterministic for unchanged field values.

Small verifiable examples include:

1. A basic value has duration `-1L`, null policy, and null unit.
2. A full value returns the same policy, duration, and `TimeUnit` supplied.
3. Two equal values compare true and have equal hash codes.
4. A null duration unit raises `NullPointerException`, while a null value is
   accepted.

Do not expose private verifier protocols, hidden test names, report paths, or
reference-source details. Do not copy an upstream implementation. The Maven
project must remain offline-compatible with an empty dependency closure, and
all candidate behavior must stay within the public API described here.
