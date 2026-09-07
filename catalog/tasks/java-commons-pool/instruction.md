# Introduction and Goals of the Commons Pool Project

Apache Commons Pool provides reusable-object pool infrastructure. This task
focuses on the deterministic configuration value object used by the evictor,
and the public enum that names pooled-object states. Recreate this bounded API
as a normal single-module Maven project without external runtime dependencies.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Pool that implements the
public behavior below:

1. Provide `org.apache.commons.pool3.PooledObjectState` with the exact public
   enum constants and declaration order listed below.
2. Provide `org.apache.commons.pool3.impl.EvictionConfig` with its public
   constructor, static thread check, getters, and deterministic text form.
3. Treat only strictly positive durations as configured durations; null, zero,
   and negative durations become `Duration.ofMillis(Long.MAX_VALUE)`.
4. Preserve `minIdle`, including negative values, and keep both classes under
   `src/main/java` in a standard single-module Maven project.
5. Do not add runtime dependencies, Maven plugins, profiles, repositories,
   modules, custom extensions, or verifier/test commands to the candidate POM.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compilation and execution
Maven 3.9.11                # offline metadata validation only
Linux amd64 / glibc         # fixed platform
Runtime dependencies: none  # java.time is part of the JDK
Network access: unavailable # agent, candidate, verifier, Oracle, controls
```

The candidate `pom.xml` is metadata only. Use the normal Maven source layout;
do not use Maven configuration to change how the verifier operates.

## Commons Pool Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/pool3/
    ├── PooledObjectState.java
    └── impl/EvictionConfig.java
```

The exact package names are part of the contract. No database, socket,
filesystem, native library, scheduler, or third-party library is needed.

## API Usage Guide

### Core APIs

#### 1. PooledObjectState

```java
import org.apache.commons.pool3.PooledObjectState;

PooledObjectState state = PooledObjectState.IDLE;
String text = state.name();
```

Declare this public enum with exactly these constants, in this order:

```text
IDLE, ALLOCATED, EVICTION, EVICTION_RETURN_TO_HEAD, VALIDATION,
VALIDATION_PREALLOCATED, VALIDATION_RETURN_TO_HEAD, INVALID, ABANDONED,
RETURNING
```

Java's standard `name()`, `ordinal()`, `valueOf(String)`, and `values()`
behavior must therefore work without custom ordering or aliases.

#### 2. EvictionConfig constructor

```java
import java.time.Duration;
import org.apache.commons.pool3.impl.EvictionConfig;

EvictionConfig config = new EvictionConfig(
    Duration.ofSeconds(30), Duration.ofSeconds(5), 2);
```

Signature:

```java
public EvictionConfig(Duration idleEvictDuration,
                      Duration idleSoftEvictDuration,
                      int minIdle)
```

The object is immutable. A duration is retained only when it is non-null,
non-zero, and non-negative; otherwise use `Duration.ofMillis(Long.MAX_VALUE)`.
The integer is stored exactly as supplied.

#### 3. Duration getters

```java
Duration hard = config.getIdleEvictDuration();
Duration soft = config.getIdleSoftEvictDuration();
int minimum = config.getMinIdle();
```

Signatures:

```java
public Duration getIdleEvictDuration()
public Duration getIdleSoftEvictDuration()
public int getMinIdle()
```

Getters return the normalized values and preserved integer. Repeated calls are
deterministic and have no side effects.

#### 4. Eviction-thread check

```java
boolean ordinary = EvictionConfig.isEvictionThread();
```

Signature:

```java
public static boolean isEvictionThread()
```

Return `true` exactly when the calling thread's name is
`"commons-pool-evictor"`; otherwise return `false`. Do not inspect thread
type, identity, stack frames, or scheduler state.

#### 5. Text form

```java
String description = config.toString();
```

For normalized durations `hard`, `soft`, and integer `minimum`, return:

```text
EvictionConfig [idleEvictDuration=<hard>, idleSoftEvictDuration=<soft>, minIdle=<minimum>]
```

Use `Duration.toString()` formatting for each duration and decimal formatting
for the integer. The text form is deterministic and must not mutate state.

### Actual Usage Modes

#### Positive configuration

```java
EvictionConfig config = new EvictionConfig(
    Duration.ofMillis(10), Duration.ofSeconds(1), 3);
config.getIdleEvictDuration().toMillis(); // 10
config.getIdleSoftEvictDuration().toMillis(); // 1000
config.getMinIdle(); // 3
```

#### Disabled-duration normalization

```java
EvictionConfig config = new EvictionConfig(Duration.ZERO, null, -1);
config.getIdleEvictDuration().toMillis(); // Long.MAX_VALUE
config.getIdleSoftEvictDuration().toMillis(); // Long.MAX_VALUE
config.getMinIdle(); // -1
```

#### Thread-name check

```java
Thread thread = new Thread(() -> EvictionConfig.isEvictionThread());
thread.setName("commons-pool-evictor");
```

### Supported Function Types

The supported behavior is enum declaration/order, immutable duration
normalization, integer preservation, three getters, exact eviction-thread
name matching, and deterministic `toString()`. Pool allocation, borrowing,
returning, eviction scheduling, JMX, proxying, concurrency, and lifecycle
factories are outside this contract.

### Error Handling

The constructor accepts null durations and normalizes them as described. Do
not throw for null durations, zero durations, negative durations, or negative
`minIdle`. Preserve normal Java enum behavior for unknown `valueOf` names and
normal Java `Duration` behavior for values supplied by callers. Do not add
silent aliases or locale-dependent formatting.

## Detailed Implementation Nodes of Functions

### Node 1: Enum Identity and Ordering

Declare the ten public constants in the exact order specified. Their names and
ordinals are observable through standard enum APIs.

### Node 2: Positive Duration Retention

Retain each independently supplied duration only if it is strictly positive.
The two duration fields are independent and must not share mutable state.

### Node 3: Disabled Duration Normalization

Map null, zero, and negative durations to `Duration.ofMillis(Long.MAX_VALUE)`.
This fallback is used for either constructor argument independently.

### Node 4: Minimum Idle Preservation

Store and return the constructor's `int` without clamping or conversion.

### Node 5: Eviction Thread Detection

Compare only `Thread.currentThread().getName()` with the exact literal
`commons-pool-evictor`.

### Node 6: Deterministic Text Form

Format the class name, field labels, normalized `Duration` values, and integer
in the exact documented order and punctuation.

### Node 7: Immutability and Repeatability

After construction, getter results and text output remain stable. The class
must not expose setters or mutate the supplied `Duration` values.

### Node 8: Offline Maven Layout

Use Java 21, standard Maven directories, a metadata-only POM, and no external
runtime dependencies. All candidate and verifier execution is offline.
