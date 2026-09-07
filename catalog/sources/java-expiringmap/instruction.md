# Introduction and Goals of the ExpiringMap Project

ExpiringMap is a Java library for maps whose entries can expire. This task
isolates the deterministic `ExpiringValue<V>` value object. Recreate this
bounded API in a normal single-module Maven project without implementing the
map, timers, listeners, or background expiry machinery.

## Natural Language Instruction (Prompt)

Create a Java Maven project that provides `net.jodah.expiringmap.ExpiringValue`
and `net.jodah.expiringmap.ExpirationPolicy`. Implement the constructors and
methods listed below using only the Java standard library. Keep production
source under `src/main/java` and preserve generic value semantics.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies,
plugins, profiles, repositories, modules, extensions, or custom commands. The
trusted verifier compiles and calls the candidate in a separate JVM.

## ExpiringMap Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/net/jodah/expiringmap/
    ├── ExpiringValue.java
    └── ExpirationPolicy.java
```

The bounded contract has no map storage, clock, executor, thread, filesystem,
network, or external Maven behavior.

## API Usage Guide

### Core APIs

Declare the enum `net.jodah.expiringmap.ExpirationPolicy` with the constants
`ACCESSED` and `CREATED`.

Implement `net.jodah.expiringmap.ExpiringValue<V>` with these exact public
constructors and methods:

```java
public ExpiringValue(V value)
public ExpiringValue(V value, ExpirationPolicy expirationPolicy)
public ExpiringValue(V value, long duration, TimeUnit timeUnit)
public ExpiringValue(V value, ExpirationPolicy expirationPolicy, long duration, TimeUnit timeUnit)
public V getValue()
public ExpirationPolicy getExpirationPolicy()
public long getDuration()
public TimeUnit getTimeUnit()
public boolean equals(Object other)
public int hashCode()
public String toString()
```

The one-argument constructor stores the value and leaves policy and time unit
unset; its duration is `-1`. The policy constructor stores the supplied policy
with the same unset duration. The duration constructors store the exact
duration and unit, and reject a null unit with `NullPointerException`.
Values, policies, and units are not copied or changed. A null value is valid.

Accessors return the stored value, policy, duration, and unit exactly. Equality
requires the same concrete `ExpiringValue` type and equal value, identical
enum policy, equal duration, and identical `TimeUnit`; null fields compare as
equal. Equal objects must have equal hash codes. The string form is the stable
form `ExpiringValue{value=..., expirationPolicy=..., duration=..., timeUnit=...}`
using the normal string form of each stored field and `null` for null fields.

### Actual Usage Modes

Use the value object when a caller needs to pass a value together with an
optional expiration policy, duration, and `TimeUnit` to map insertion logic.
The task itself performs no expiration and does not consult the current time.

### Supported Function Types

The supported functions are value construction, field access, null-unit
validation, equality, hashing, and deterministic string conversion. Map
operations, expiration scheduling, listeners, thread factories, concurrency,
and time-based behavior are outside the contract.

### Error Handling

The duration constructors must throw `NullPointerException` for a null
`TimeUnit`. Other constructor inputs, including a null value and null policy,
are accepted. Do not silently replace nulls or normalize duration values.

## Detailed Implementation Nodes of Functions

### Node 1: Basic construction

Store the value, a null policy, duration `-1`, and null time unit for the basic
constructor. The policy constructor changes only the policy field.

### Node 2: Explicit duration construction

Store the supplied duration and `TimeUnit` without conversion. Both overloads
must reject null `TimeUnit` before producing an object.

### Node 3: Accessors

Return each stored field without expiration checks, mutation, I/O, or clock
access. Generic values retain their original object identity.

### Node 4: Equality and hashing

Compare all four stored fields with null-safe value equality, enum identity for
the policy, exact duration equality, and unit identity. Derive a consistent
hash code from the value as required by the public value-object behavior.

### Node 5: String representation

Produce the field-labelled `ExpiringValue{...}` representation in the stated
field order. It must be deterministic for the same field values.

### Node 6: Boundary behavior

Cover null values and policies, zero and negative durations, all supported
`TimeUnit` values, equal and unequal objects, and null duration units.

### Node 7: Source and package layout

Use the exact `net.jodah.expiringmap` package and public type names. The
project must compile with `javac --release 21` and standard Maven layout.

### Node 8: Offline behavior

Keep the Maven dependency closure empty. Candidate, verifier, Oracle, and
controls must complete without network access; the verifier owns collection,
JUnit reporting, and reward calculation.
