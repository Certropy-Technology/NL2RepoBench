## Project Description

Create a small, standard Maven project named Commons Pool that recreates the
bounded public Java API described in this document. The project is not a full
pool implementation. It contains the deterministic state enum used by the
pool package and the immutable eviction configuration value object used by
the implementation package.

The public package names are part of the contract. Use Java source files under
`src/main/java`, with no alternate package, compatibility alias, or default
package. The implementation must compile with the supplied Java 21 toolchain.

The two bindable types are:

* `org.apache.commons.pool3.PooledObjectState`, a public enum of pooled-object
  lifecycle states.
* `org.apache.commons.pool3.impl.EvictionConfig`, a public configuration value
  object containing two normalized idle durations and an integer minimum.

The behavior is intentionally narrow and deterministic. Implement the exact
names, declaration order, constructor behavior, accessors, thread-name check,
and text representation below. Do not implement pool allocation, object
factories, eviction scheduling, JMX, metrics, logging, networking, persistence,
or unrelated Apache Commons Pool modules.

## Supports

### Natural Language Instruction

Build the following project in the workspace. Create a metadata-only Maven
`pom.xml` and the two Java types described in the API Usage Guide. The POM
must identify a normal single-module project and must not introduce runtime
dependencies, plugin repositories, Maven profiles, extra modules, or custom
Maven extensions. The Java standard library is sufficient.

Use the exact package and type names. Keep the enum constants in the exact
listed order. Store each constructor duration independently. A duration is
configured only when it is non-null and strictly greater than
`Duration.ZERO`; null, zero, and negative values must each normalize to
`Duration.ofMillis(Long.MAX_VALUE)`. Preserve `minIdle` exactly, including
negative values and the integer boundary values.

The `isEvictionThread()` result depends only on the current thread name. It is
true for the exact name `commons-pool-evictor` and false for every other name.
The value object's `toString()` output has the exact labels, order, spaces,
brackets, commas, and `Duration.toString()` values documented below.

### Environment Configuration

Use the fixed execution environment:

```text
JDK: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64 with glibc
Runtime dependencies: none
Network: unavailable during candidate, verifier, Oracle, and control runs
```

Use ordinary Maven source layout. The candidate POM is metadata only; do not
use POM configuration to alter the verifier, fetch dependencies, or run
external commands. `java.time.Duration` comes from the JDK and must not be
declared as a dependency.

### Project Directory Structure

The project must use this shape, rooted at `workspace/`:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── pool3/
                            ├── PooledObjectState.java
                            └── impl/
                                └── EvictionConfig.java
```

The file names must match their public type names. Do not put generated
classes, tests, private harness code, reference files, or artifacts in the
candidate workspace. A conventional test source tree is allowed only if it
does not replace or alter the required main source layout.

## API Usage Guide

### `org.apache.commons.pool3.PooledObjectState`

Import the enum with:

```java
import org.apache.commons.pool3.PooledObjectState;
```

Declare exactly this public enum and exactly this declaration order:

```java
public enum PooledObjectState {
    IDLE,
    ALLOCATED,
    EVICTION,
    EVICTION_RETURN_TO_HEAD,
    VALIDATION,
    VALIDATION_PREALLOCATED,
    VALIDATION_RETURN_TO_HEAD,
    INVALID,
    ABANDONED,
    RETURNING
}
```

The ten entries are the complete supported state vocabulary. Do not add
aliases, fields, constructors, methods, or extra constants that change the
public shape or ordinal positions.

### Enum entry identity and ordering

`PooledObjectState.IDLE` is a public enum entry with ordinal `0` and
`PooledObjectState.RETURNING` is a public enum entry with ordinal `9`. The
other ordinals follow the declaration order above. A normal example is:

```java
PooledObjectState state = PooledObjectState.EVICTION;
String name = state.name();       // "EVICTION"
int position = state.ordinal();   // 2
```

An edge example is:

```java
PooledObjectState[] states = PooledObjectState.values();
// states.length == 10; states[0] == IDLE; states[9] == RETURNING
PooledObjectState same = PooledObjectState.valueOf("RETURNING");
```

The inherited Java enum methods `name()`, `ordinal()`, `values()`, and
`valueOf(String)` must retain normal Java semantics. `valueOf` is case
sensitive and throws the standard unchecked `IllegalArgumentException` for
an unknown name; null is handled by the standard enum implementation. Do not
silently trim, lowercase, or translate names.

### `org.apache.commons.pool3.impl.EvictionConfig`

Import the value object with:

```java
import java.time.Duration;
import org.apache.commons.pool3.impl.EvictionConfig;
```

The public type is a normal immutable class. Its bindable public constructor
is:

```java
public EvictionConfig(
    Duration idleEvictDuration,
    Duration idleSoftEvictDuration,
    int minIdle)
```

The first argument is the hard idle eviction duration. The second argument is
the soft idle eviction duration. The third argument is stored as an `int`.
The constructor has no I/O, synchronization, scheduling, or global state
side effect.

### `EvictionConfig(Duration, Duration, int)` constructor

For each duration independently, retain the supplied `Duration` when and
only when it is strictly positive. A normal example is:

```java
EvictionConfig config = new EvictionConfig(
    Duration.ofSeconds(30),
    Duration.ofSeconds(5),
    2);
```

In this example the hard value is `Duration.ofSeconds(30)`, the soft value is
`Duration.ofSeconds(5)`, and the minimum is `2`.

The constructor accepts null durations. Null, `Duration.ZERO`, and every
negative duration are disabled inputs and normalize to
`Duration.ofMillis(Long.MAX_VALUE)`. The two arguments are independent:
normalizing one does not normalize or modify the other.

An edge example is:

```java
EvictionConfig config = new EvictionConfig(
    Duration.ZERO,
    null,
    -1);
// both duration getters return Duration.ofMillis(Long.MAX_VALUE)
// getMinIdle() returns -1
```

There is no checked exception for null, zero, negative duration, or negative
`minIdle`. A `Duration` object is immutable, so retaining a valid value has
no caller-visible mutation. Ordinary Java argument evaluation still applies;
the constructor does not catch or translate unrelated runtime failures from
the caller's expression.

### `EvictionConfig.getIdleEvictDuration()`

The full public signature is:

```java
public Duration getIdleEvictDuration()
```

It returns the normalized hard idle eviction duration. The return type is
`java.time.Duration`, never null. A normal example is:

```java
EvictionConfig config = new EvictionConfig(
    Duration.ofMillis(10), Duration.ofSeconds(1), 3);
Duration hard = config.getIdleEvictDuration();
// hard.equals(Duration.ofMillis(10))
```

An edge example is:

```java
Duration hard = new EvictionConfig(null, Duration.ofSeconds(1), 0)
    .getIdleEvictDuration();
// hard.equals(Duration.ofMillis(Long.MAX_VALUE))
```

The method has no parameters, no I/O, and no mutation. Repeated calls return
equal deterministic values. It throws no checked exception and should not
throw for the constructor's supported null, zero, or negative inputs.

### `EvictionConfig.getIdleSoftEvictDuration()`

The full public signature is:

```java
public Duration getIdleSoftEvictDuration()
```

It returns the normalized soft idle eviction duration. The return type is
`java.time.Duration`, never null. A normal example is:

```java
EvictionConfig config = new EvictionConfig(
    Duration.ofMillis(10), Duration.ofSeconds(1), 3);
Duration soft = config.getIdleSoftEvictDuration();
// soft.equals(Duration.ofSeconds(1))
```

An edge example is:

```java
Duration soft = new EvictionConfig(Duration.ofSeconds(1),
                                   Duration.ofMillis(-1), 0)
    .getIdleSoftEvictDuration();
// soft.equals(Duration.ofMillis(Long.MAX_VALUE))
```

The method has no parameters, no I/O, and no mutation. It normalizes only the
second constructor argument and does not mirror or overwrite the hard value.
It throws no checked exception for any supported constructor input.

### `EvictionConfig.getMinIdle()`

The full public signature is:

```java
public int getMinIdle()
```

It returns exactly the `int minIdle` supplied to the constructor. A normal
example is:

```java
int minimum = new EvictionConfig(
    Duration.ofSeconds(1), Duration.ofSeconds(2), 3)
    .getMinIdle();
// minimum == 3
```

An edge example is:

```java
int minimum = new EvictionConfig(
    Duration.ZERO, null, Integer.MIN_VALUE)
    .getMinIdle();
// minimum == Integer.MIN_VALUE
```

Do not clamp, reject, convert, or otherwise normalize negative values. The
method has no side effect, returns deterministically, and throws no checked
exception.

### `EvictionConfig.isEvictionThread()`

The full public static signature is:

```java
public static boolean isEvictionThread()
```

It returns `true` exactly when
`Thread.currentThread().getName().equals("commons-pool-evictor")`. It must
inspect only the current thread's name. Do not inspect thread class, thread
identity, stack frames, daemon status, scheduler state, or caller.

A normal example is:

```java
String oldName = Thread.currentThread().getName();
Thread.currentThread().setName("commons-pool-evictor");
boolean result = EvictionConfig.isEvictionThread(); // true
Thread.currentThread().setName(oldName);
```

An edge example is:

```java
Thread.currentThread().setName("commons-pool-evictor-worker");
boolean result = EvictionConfig.isEvictionThread(); // false
```

The method does not create threads or alter the current thread. It has no
checked exception contract. A null thread name is not expected from normal
Java `Thread` usage and must not be converted into a match; only the exact
literal name is accepted.

### `EvictionConfig.toString()`

The public override has the standard signature:

```java
public String toString()
```

For normalized values `hard`, `soft`, and `minimum`, return exactly:

```text
EvictionConfig [idleEvictDuration=<hard>, idleSoftEvictDuration=<soft>, minIdle=<minimum>]
```

Use each `Duration`'s normal `toString()` representation and decimal Java
integer formatting. A normal example is:

```java
String text = new EvictionConfig(
    Duration.ofMillis(10), Duration.ofSeconds(1), 3).toString();
// "EvictionConfig [idleEvictDuration=PT0.01S, "
// + "idleSoftEvictDuration=PT1S, minIdle=3]"
```

An edge example is:

```java
String text = new EvictionConfig(
    Duration.ZERO, null, -1).toString();
// "EvictionConfig [idleEvictDuration=PT2562047788015215H30M7.999999999S, "
// + "idleSoftEvictDuration=PT2562047788015215H30M7.999999999S, minIdle=-1]"
```

The output is deterministic for one configuration, uses the documented field
order, and has no I/O or mutation. It throws no checked exception for any
validly constructed object. Do not use locale-dependent number formatting,
identity hashes, timestamps, or alternate labels.

### Supported and unsupported surface

The supported surface is limited to the enum, its normal Java identity and
ordering behavior, the `EvictionConfig` constructor, the three getters, the
static thread-name predicate, and the exact `toString()` override. No public
pool classes, factory interfaces, eviction policies, timers, statistics,
JMX registrations, serialization formats, CLI commands, or service entry
points are confidently bindable from the task-local contract, so they are
outside this task and must not be invented.

## Implementation Notes

Keep the two types in their separate packages and keep the public names
discoverable from ordinary Java imports. The value object should be immutable:
initialize its values during construction, expose no setters, preserve the
integer exactly, and never mutate a supplied `Duration`. The enum declaration
must remain stable because `ordinal()` and `values()` expose declaration
order.

Normalize the hard and soft duration arguments independently. The comparison
is strict: a duration equal to zero is disabled, while any positive duration
is retained. The fallback is the same `Duration.ofMillis(Long.MAX_VALUE)` for
either disabled argument. Avoid relying on wall-clock time or mutable global
state.

The thread predicate must be a literal name comparison. A thread with a
different suffix, different case, or an otherwise similar role is not an
eviction thread. The predicate must not depend on whether a thread was
created by a scheduler or whether its name was assigned by the library.

The text form must be assembled from the object's normalized values. Preserve
the exact class name, labels, comma placement, one space after each comma,
and closing bracket. Let `Duration.toString()` provide duration formatting;
do not convert durations through locale-sensitive formatting.

Small verifiable examples to keep in mind:

1. `new EvictionConfig(Duration.ofMillis(10), Duration.ofSeconds(1), 3)`
   returns 10 milliseconds, 1 second, and 3 from its three accessors.
2. `new EvictionConfig(Duration.ZERO, null, -1)` returns the maximum-millis
   fallback for both duration accessors and preserves `-1`.
3. `PooledObjectState.values()` has ten entries, beginning with `IDLE` and
   ending with `RETURNING`.
4. Renaming the current thread to exactly `commons-pool-evictor` changes the
   predicate to true; adding one character makes it false.

Compile against Java 21 using the standard Maven layout. Keep the POM free of
runtime dependencies and do not add source copied from an upstream project,
private test assertions, verifier entry points, grader-specific output, or
reference-source retrieval instructions. Implement only the behavior that is
confidently bindable above; no additional API is required for acceptance.
