# Introduction and Goals of the Commons Text Project

Apache Commons Text is a Java library for deterministic text processing and
similarity utilities. This task focuses on the self-contained
`HammingDistance` value calculator in `org.apache.commons.text.similarity`.
Create a normal single-module Maven project from an empty workspace and expose
the documented public API without external runtime dependencies.

## Natural Language Instruction (Prompt)

Create a Java Maven project named Commons Text. Implement the public
`HammingDistance` class described below. The project must compile with Java 21,
use the exact package name, and keep production code under `src/main/java`.
Do not copy the upstream project, add unrelated Commons Text classes, or use
network access at build or run time.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compiler and runtime
Maven 3.9.11                # offline metadata validation
Linux amd64 / glibc         # fixed platform
Runtime dependencies: none  # java.lang and java.lang internals only
Network access: unavailable  # candidate and verifier execution is offline
```

The candidate `pom.xml` is metadata only. It may contain the model version,
coordinates, and packaging, but must not contain dependencies, plugins,
profiles, repositories, modules, extensions, or custom build instructions.

## Commons Text Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/text/similarity/HammingDistance.java
```

Use a single Maven module and the exact public class and package above. No
generated sources or test implementation is required in the candidate project.

## API Usage Guide

### Core APIs

#### HammingDistance class

Import the class as follows:

```java
import org.apache.commons.text.similarity.HammingDistance;
```

Construct an instance with:

```java
HammingDistance distance = new HammingDistance();
```

Signature:

```java
public HammingDistance()
```

The constructor has no arguments, has no observable state, and does not
perform I/O or mutate global state.

#### apply(CharSequence, CharSequence)

Signature:

```java
public Integer apply(CharSequence left, CharSequence right)
```

Both arguments must be non-null `CharSequence` values of exactly the same
length. The method compares corresponding positions using
`CharSequence.charAt(int)` and returns an `Integer` equal to the number of
positions whose UTF-16 `char` values differ. Ordering is positional and
deterministic; duplicate characters count independently. The input sequences
are read only and never modified.

Examples:

```java
new HammingDistance().apply("1011101", "1011111"); // 1
new HammingDistance().apply("karolin", "kerstin"); // 3
new HammingDistance().apply("", "");                 // 0
new HammingDistance().apply("abc", new StringBuilder("axc")); // 1
```

If either argument is `null`, throw `IllegalArgumentException`. If the two
sequences have different lengths, throw `IllegalArgumentException`; do not
truncate, pad, or compare only the common prefix. A sequence containing a
Unicode supplementary character is compared by its UTF-16 code units, as
required by `CharSequence.charAt`, rather than by code points.

### Actual Usage Modes

Use the instance method for equal-length identifiers, fixed-width records,
binary-as-text samples, or any other pair of `CharSequence` values. A mutable
implementation such as `StringBuilder` is accepted through the interface but
must not be changed. Calling the method repeatedly on the same instance with
the same inputs returns the same result.

### Supported Function Types

The supported behavior is limited to constructing `HammingDistance` and
computing the positional mismatch count through `apply(CharSequence,
CharSequence)`. No static helpers, collection APIs, file operations, random
behavior, locale behavior, or network behavior are part of this task.

### Error Handling

Reject null arguments and unequal lengths with `IllegalArgumentException`.
The exception type is part of the contract; do not return a sentinel or let a
null input be treated as an empty sequence. Equal empty sequences are valid
and return zero. Inputs of equal length, including all-equal and all-different
values, must return an `Integer` rather than a primitive-only alternate API.

## Detailed Implementation Nodes of Functions

### Node 1: Exact public surface

Provide the public class in
`org.apache.commons.text.similarity.HammingDistance` with the public no-arg
constructor and the exact `Integer apply(CharSequence, CharSequence)` method.

### Node 2: Equal-length validation

Validate both references and then compare their lengths before reading any
character. Unequal lengths must fail with `IllegalArgumentException`.

### Node 3: Positional comparison

Visit each index from zero through `length - 1`, compare the two UTF-16 code
units at that index, and increment the mismatch count only when they differ.

### Node 4: Determinism and state

Do not mutate either argument, retain input between calls, use locale or
randomness, or perform I/O. Results depend only on the two current sequences.

### Node 5: Boundary behavior

Cover empty strings, one mismatch, all mismatches, equal strings, mutable
`CharSequence` inputs, null inputs, unequal lengths, and supplementary
characters represented by their UTF-16 units.

### Node 6: Offline Maven layout

Use the standard source layout, Java 21, a metadata-only candidate POM, and no
third-party dependency. The project must remain buildable in a no-network
environment.
