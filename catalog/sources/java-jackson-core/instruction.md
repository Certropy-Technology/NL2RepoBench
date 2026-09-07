# Introduction and Goals of the Jackson Core Project

Jackson Core is a Java library containing low-level JSON infrastructure. This task
implements a bounded, deterministic slice of `tools.jackson.core.JsonPointer`.
The slice parses RFC 6901-style pointer strings, exposes the first matching
segment, and constructs pointers by appending a property or array index.

## Natural Language Instruction (Prompt)

Create a single-module Java Maven project implementing the public class
`tools.jackson.core.JsonPointer` and the documented methods below. Keep the
implementation under `src/main/java/tools/jackson/core/JsonPointer.java`.
The implementation must be immutable and deterministic. Do not implement JSON
parsing, tree traversal, token streams, serialization, or unrelated Jackson APIs.

## Environment Configuration

### Core Dependency Library Versions

Use Temurin JDK 21.0.12+8 and Maven 3.9.11 on Linux amd64 with glibc. Maven is
used only for project validation. The runtime has no third-party dependencies,
and agent, candidate, verifier, Oracle, and controls execute without network.
The candidate `pom.xml` is metadata only: it must not declare repositories,
dependencies, modules, profiles, plugins, or build extensions.

## Jackson Core Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/tools/jackson/core/JsonPointer.java
```

The class is an immutable pointer. A compiled non-empty pointer is a sequence of
decoded segments. A pointer's textual form retains the supplied escape spelling,
while matching uses decoded segment values.

## API Usage Guide

### Core APIs

Import `tools.jackson.core.JsonPointer`.

`public static JsonPointer compile(String expr)` accepts `null` or the empty
string as the empty pointer. Any non-empty expression must begin with `/`, or
the method throws `IllegalArgumentException`. Each slash starts a segment;
`~0` decodes to `~` and `~1` decodes to `/`. Other tilde sequences preserve the
tilde and following character as ordinary text. The returned pointer is
immutable.

`public static JsonPointer empty()` returns the empty pointer. For an empty
pointer, `matches()` is true, `tail()` and `head()` return `null`, and its
string form and length are both empty/zero.

`public int length()` returns the length of `toString()`.
`public boolean matches()` reports whether this pointer is the final matching
state. `public String getMatchingProperty()` returns the decoded first segment,
or `null` for the empty pointer. `public int getMatchingIndex()` returns the
first segment as a non-negative integer only for canonical decimal indexes
(`0` or a non-zero digit followed by digits, within `Integer.MAX_VALUE`);
otherwise it returns `-1`.

`public boolean mayMatchProperty()` is true for every non-empty pointer.
`public boolean mayMatchElement()` is true only when `getMatchingIndex()` is
non-negative. `public JsonPointer tail()` returns the pointer after removing
the first segment, or `null` when this pointer has one segment. `public
JsonPointer head()` returns the pointer after removing the final segment, or the
empty pointer when this pointer has one segment; it returns `null` for empty.

`public boolean matchesProperty(String name)` tests the first decoded segment
against `name`; it is false for an empty pointer. `public JsonPointer
matchProperty(String name)` returns `tail()` when the test succeeds, otherwise
`null`. `public boolean matchesElement(int index)` and `public JsonPointer
matchElement(int index)` perform the analogous non-negative index test.

`public JsonPointer appendProperty(String property)` appends one segment. A
null property returns this pointer unchanged; otherwise slash becomes `~1` and
tilde becomes `~0`, including for an empty property. `public JsonPointer
appendIndex(int index)` appends a canonical decimal array index and throws
`IllegalArgumentException` for a negative index. `toString()`, `equals`, and
`hashCode` use the original textual pointer representation.

### Actual Usage Modes

```java
JsonPointer p = JsonPointer.compile("/a~1b/0");
p.matchesProperty("a/b");       // true
p.getMatchingIndex();            // -1
p.tail().matchesElement(0);      // true
JsonPointer q = p.appendProperty("x~y"); // "/a~1b/0/x~0y"
```

### Supported Function Types

The supported types are static factories, RFC 6901 segment decoding and
escaping, immutable pointer navigation, decoded property matching, canonical
array-index matching, and deterministic value methods. Inputs are finite Java
strings and integer values. No filesystem, clock, randomness, network, or
global state is used.

### Error Handling

`compile` rejects a non-empty string without a leading slash with
`IllegalArgumentException`. `appendIndex` rejects negative values with
`IllegalArgumentException`. Other methods follow the null behavior stated
above; a null property name simply does not match, and a null append property
is a no-op.

## Detailed Implementation Nodes of Functions

### Node 1: Factory and Escapes

Implement `compile` and `empty` with exact null, empty, slash, `~0`, `~1`,
malformed escape, and invalid-prefix behavior.

### Node 2: Segment State

Expose decoded first-segment property, canonical integer detection, match flags,
text length, and immutable textual representation.

### Node 3: Navigation

Implement `tail` and `head` with empty, one-segment, and multi-segment
boundaries. Navigation must not mutate the original pointer.

### Node 4: Matching

Match decoded property names and canonical non-negative indexes. Successful
match methods return the remaining pointer; failed matches return false/null.

### Node 5: Appending

Append escaped properties and non-negative decimal indexes. Preserve existing
segments and reject negative indexes.

### Node 6: Maven and Contract Boundaries

Use the exact package and class name, standard Maven layout, Java 21 syntax, and
no dependency or build plugin. Implement only this documented public slice.
