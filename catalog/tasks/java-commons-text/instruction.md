## Project Description

Create a small, offline Java Maven project that recreates the bounded public
contract of Apache Commons Text's Hamming-distance value calculator. The
project is intended for callers that need a deterministic count of positional
UTF-16 character mismatches between two equal-length text sequences.

The deliverable is a normal Maven project rooted at `workspace/`. It has one
production class, one public package, and no third-party runtime dependency.
The implementation must be usable from another Java class through the exact
package and method signatures described in the API Usage Guide.

The supported behavior is deliberately narrow. Implement the public
`org.apache.commons.text.similarity.HammingDistance` class, its public no-arg
constructor, and its public `apply` method. Do not add unrelated Commons Text
classes, alternate package names, a command-line interface, persistence,
logging, network access, or an extra dependency. The requested result is an
`Integer` mismatch count, not a code-point-aware similarity score or a
normalized distance.

### Natural Language Instruction

Starting from an empty workspace, create the Maven project shown below and
implement the documented HammingDistance API. Use Java 21 source-compatible
code and the exact package name. The candidate project must remain buildable
offline: its POM is metadata-only and must not require downloading a library,
plugin, parent, repository, profile, extension, or module.

The implementation must satisfy these capabilities:

1. Expose `org.apache.commons.text.similarity.HammingDistance` as a public
   class with a public no-argument constructor.
2. Expose `public Integer apply(CharSequence left, CharSequence right)` with
   the exact parameter and return types.
3. Compare corresponding UTF-16 `char` values in order and return the number
   of positions that differ.
4. Reject null arguments and unequal lengths with
   `IllegalArgumentException`, while accepting equal empty sequences and any
   other equal-length `CharSequence` implementation.

Do not copy an upstream repository or reproduce implementation source in the
instruction. Keep production code under
`src/main/java/org/apache/commons/text/similarity/`. A candidate `pom.xml` is
required even though the public API has no external dependencies.

## Supports

### Runtime and build environment

Use the following fixed environment and project identity:

| Item | Required value |
| --- | --- |
| Language | Java |
| Java runtime | Temurin JDK 21.0.12+8 |
| Package manager | Maven 3.9.11 |
| Platform | Linux amd64 with glibc |
| Maven project | One module rooted at `workspace/` |
| Runtime dependencies | None beyond the Java platform |
| Network policy | No network during agent, candidate, verifier, Oracle, or control execution |

The implementation may use `java.lang` and other JDK-provided types needed by
the declared signatures. It must not add Commons Text, Apache Commons, test,
logging, or other third-party dependencies to the candidate project. The
metadata POM may declare ordinary coordinates such as group, artifact, and
version, but it must not introduce a parent, dependency, repository, plugin,
profile, extension, module, or custom build instruction.

### Project Directory Structure

The required public project has this shape. `workspace/` is the project root,
not an extra directory nested inside the candidate workspace.

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── text/
                            └── similarity/
                                └── HammingDistance.java
```

`pom.xml` is the Maven project descriptor. The only public production source
file required by this task is
`src/main/java/org/apache/commons/text/similarity/HammingDistance.java`.
The directory and filename are case-sensitive. Do not place the class in the
default package, under a different `org.apache` package, or in a generated
source tree. No CLI entry point, resource directory, service descriptor, or
application configuration file is part of this task.

### Build and installation boundary

The project should be recognizable as a standard single-module Maven project
and should validate with the available offline toolchain. A minimal POM is
sufficient. Maven metadata must not cause a run-time download. The class is
consumed as a library; it does not need a `main` method and must not read
standard input or write files.

## API Usage Guide

The public API surface is intentionally limited to one class and two public
members. The exact import path and signatures below are the contract. Package
private helpers are allowed only when they do not change this public surface;
no additional public class or public method is required.

### `org.apache.commons.text.similarity.HammingDistance`

Import the class with:

```java
import org.apache.commons.text.similarity.HammingDistance;
```

This is a stateless value calculator. Constructing it does not retain input,
perform I/O, inspect the environment, use randomness, or mutate global state.
Repeated calls on the same instance are independent and deterministic.

#### Constructor

Signature:

```java
public HammingDistance()
```

The constructor accepts no parameters and returns a new
`HammingDistance` instance. It has no checked or unchecked failure condition
for ordinary construction and has no observable side effect. The normal use
is:

```java
HammingDistance distance = new HammingDistance();
```

An edge use is also valid because the instance has no configuration:

```java
Integer distance = new HammingDistance().apply("", "");
// distance is 0
```

#### `apply(CharSequence, CharSequence)`

Signature:

```java
public Integer apply(final CharSequence left, final CharSequence right)
```

The `left` and `right` parameters are required, non-null `CharSequence`
values. Their `length()` values must be equal before comparison begins. The
method accepts `String`, `StringBuilder`, `StringBuffer`, or another
well-behaved `CharSequence` implementation; callers are not restricted to
two `String` objects.

The return type is the boxed type `Integer`. Its value is the number of
indexes `i` in the range `0` inclusive through `left.length()` exclusive for
which `left.charAt(i)` and `right.charAt(i)` are different. Equal positions do
not contribute to the count. The result is always between zero and the common
UTF-16 length, inclusive.

Comparison is positional and deterministic. The method observes each input
through `length()` and `charAt(int)` and does not modify either object. It
does not trim whitespace, normalize case, apply locale rules, compare
grapheme clusters, or compare Unicode code points. Supplementary characters
are therefore considered through their two UTF-16 code units, as required by
the `CharSequence.charAt` contract.

For a normal one-mismatch call:

```java
HammingDistance distance = new HammingDistance();
Integer result = distance.apply("karolin", "karnlin");
// result is 1
```

For an equal-length `CharSequence` other than `String`:

```java
Integer result = new HammingDistance().apply(
    new StringBuilder("abc"), new StringBuilder("axc"));
// result is 1; neither builder is changed
```

For equal values and all differing values:

```java
new HammingDistance().apply("same", "same"); // 0
new HammingDistance().apply("abc", "xyz");   // 3
```

For the empty boundary:

```java
new HammingDistance().apply("", ""); // 0
```

If either argument is `null`, the method throws
`IllegalArgumentException`. Null is not treated as an empty sequence and the
method must not return a sentinel value. If the lengths differ, the method
also throws `IllegalArgumentException`; it must not truncate to the common
prefix, pad either value, or silently return a partial count. For example:

```java
new HammingDistance().apply("ab", "abc"); // IllegalArgumentException
new HammingDistance().apply(null, "abc"); // IllegalArgumentException
```

The contract does not require a particular exception message. No checked
exception is declared by the signature. Exceptions raised by a hostile,
custom `CharSequence` implementation while its `length()` or `charAt(int)` is
called are not converted into a different API contract; ordinary inputs must
follow the validation and return behavior above.

### Unsupported public surface

There is no task-defined static convenience method, CLI command, file format,
serialization contract, configuration object, distance-normalization API,
or network integration. Do not invent public methods for these concerns. A
class or entry point not described above is not confidently bindable to this
bounded task contract and should be omitted from the public implementation.

## Implementation Notes

### Contract and validation constraints

Validate the two references and their lengths before attempting to count
positions. Both null and unequal-length cases must use
`IllegalArgumentException`. Equal empty sequences are valid. The returned
`Integer` must represent the mismatch count without exposing a primitive-only
replacement signature.

The two arguments are read-only from the caller's perspective. In particular,
an implementation must not call mutating methods on a mutable
`CharSequence`, retain a reference for later calls, or cache a result in
global state. The class should remain safe to reuse sequentially with
different pairs of inputs.

### Determinism and character semantics

The result depends only on the current sequence contents and their order. Do
not use locale, system time, randomness, filesystem state, environment
variables, thread scheduling, or network services. Treat the sequence as
UTF-16 code units: a supplementary Unicode character is not a special
single-element case for this API.

Small verifiable examples include:

```java
new HammingDistance().apply("1011101", "1011111"); // 1
new HammingDistance().apply("", "");                 // 0
new HammingDistance().apply("abc", "abc");           // 0
new HammingDistance().apply("abc", "abd");           // 1
```

Boundary checks should additionally exercise a null left value, a null right
value, and unequal lengths, confirming `IllegalArgumentException` in each
case. An equal-length `StringBuilder` pair should produce the same positional
count as equivalent strings and remain unchanged after the call.

### Maven and repository constraints

Keep `pom.xml` minimal and offline-compatible. Do not copy the upstream
repository, add private verifier material, include test assertions in the
candidate, or add a dependency merely to provide `CharSequence` behavior.
The verifier and build environment supply their own checks; the candidate
only needs the public source layout and API documented here.
