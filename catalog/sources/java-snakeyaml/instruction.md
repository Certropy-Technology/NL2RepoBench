# Introduction and Goals of the SnakeYAML Project

SnakeYAML is a Java YAML library. This task covers its small, deterministic
array-to-list utility in `org.yaml.snakeyaml.util.ArrayUtils`, rather than YAML
parsing, emitting, reflection, or object construction. Create a normal
single-module Maven project from an empty workspace and implement exactly the
public API described here.

## Natural Language Instruction (Prompt)

Create a Java Maven project named SnakeYAML. Implement the public static
methods of `ArrayUtils` described below, using the exact package and type
name. The project must compile with Java 21 and place production code under
`src/main/java`. Do not copy the upstream project, add YAML parser APIs, or
perform network access at build or run time.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compiler and runtime
Maven 3.9.11                # offline metadata validation
Linux amd64 / glibc         # fixed platform
Runtime dependencies: none  # JDK collections only
Network access: unavailable # candidate and verifier execution is offline
```

The candidate `pom.xml` is metadata only. It may contain the model version,
coordinates, packaging, name, description, and compiler properties, but must
not contain dependencies, plugins, profiles, repositories, modules,
extensions, or custom build instructions.

## SnakeYAML Project Architecture

### Project Directory Structure

```Plain
workspace/
|-- pom.xml
`-- src/main/java/org/yaml/snakeyaml/util/ArrayUtils.java
```

Use a single Maven module and the exact public class and package above. No
generated sources or test implementation is required in the candidate project.

## API Usage Guide

### Core APIs

#### ArrayUtils class

Import the class as follows:

```java
import org.yaml.snakeyaml.util.ArrayUtils;
```

`ArrayUtils` is a utility class. Its constructor is not part of this task.

#### toUnmodifiableList(E[])

Signature:

```java
public static <E> java.util.List<E> toUnmodifiableList(E[] elements)
```

The method accepts a non-null array and returns a list with the same elements
in the same order. The result is backed by the supplied array: changing an
array element after the call changes the value observed through the returned
list. The returned list is not structurally or element mutable through the
`List` API; mutating methods such as `set` throw
`UnsupportedOperationException`.

Examples:

```java
String[] colors = {"red", "blue"};
List<String> values = ArrayUtils.toUnmodifiableList(colors);
values.get(1); // "blue"
colors[1] = "green";
values.get(1); // "green"
```

An empty array produces an empty unmodifiable list. Passing `null` throws
`NullPointerException`. Calling `get` with an index below zero or at least the
list size throws `IndexOutOfBoundsException`.

#### toUnmodifiableCompositeList(E[], E[])

Signature:

```java
public static <E> java.util.List<E> toUnmodifiableCompositeList(E[] array1, E[] array2)
```

The method accepts two non-null arrays and returns one unmodifiable list. Its
contents are every element of `array1` followed by every element of `array2`;
the ordering is deterministic and duplicates are retained. The result is
backed by the non-empty input arrays, so later element replacement in either
array is visible through the matching list position. It does not copy array
contents.

Examples:

```java
ArrayUtils.toUnmodifiableCompositeList(new String[] {"a", "b"}, new String[] {"c"});
// List containing "a", "b", "c"
```

If either input is empty, the result has the elements of the other array with
the same backing and immutability semantics. Passing either `null` throws
`NullPointerException`. Out-of-range `get` calls throw
`IndexOutOfBoundsException`, and `List` mutators throw
`UnsupportedOperationException`.

### Actual Usage Modes

Use these helpers when an API needs a read-only list view over one array or a
read-only concatenated view over two arrays. Calls have no global state, I/O,
locale, random, time, or network behavior. Repeated calls with unchanged
arrays have the same ordering and size.

### Supported Function Types

The supported surface is limited to the two static generic methods above,
ordinary `List` observation through `size` and `get`, and the documented
exceptions. YAML parsing, serialization, tags, anchors, comments, custom
constructors, and all other SnakeYAML classes are outside this task.

### Error Handling

Reject a null array reference with `NullPointerException`. Do not turn null
into an empty array. Preserve `IndexOutOfBoundsException` for invalid list
indexes and `UnsupportedOperationException` for attempted `List` mutation.
These exception types are part of the public contract.

## Detailed Implementation Nodes of Functions

### Node 1: Exact public surface

Provide `org.yaml.snakeyaml.util.ArrayUtils` and the two public static generic
methods with the signatures shown above. Do not require callers to construct
the utility class.

### Node 2: Single-array view

Return a list whose size equals the input array length and whose index `i`
reads the current value of `elements[i]`. The view must not make a defensive
copy.

### Node 3: Composite view

Return a list with size `array1.length + array2.length`. Indexes below
`array1.length` read from the first array; remaining indexes read from the
second array after subtracting that length.

### Node 4: Read-only list interface

The views may expose read operations but must reject mutation via the standard
`List` API with `UnsupportedOperationException`.

### Node 5: Boundaries and determinism

Preserve empty arrays, duplicate values, ordering, backing updates, invalid
index failures, and null input failures. Do not retain unrelated mutable
state, perform I/O, or use network access.

### Node 6: Offline Maven layout

Use the standard source layout, Java 21, a metadata-only candidate POM, and no
third-party dependency. The project must remain buildable in a no-network
environment.
