## Project Description

Create a small Java library project named SnakeYAML that reproduces the bounded
array-view utility used by the `org.yaml.snakeyaml` package.

The target users are Java callers that need to expose one Java array, or two
arrays joined in order, through the read-only `java.util.List` interface.
The task is intentionally narrower than the complete SnakeYAML project.

The candidate must create a clean, single-module Maven project from an empty
workspace. The public package must be exactly:

```java
org.yaml.snakeyaml.util
```

The public class required by this task is exactly:

```java
org.yaml.snakeyaml.util.ArrayUtils
```

The class must expose the two public static generic methods specified in the
API Usage Guide. A caller must be able to compile against those methods using
Java 21 and the standard JDK collection interfaces.

The single-array method presents the elements of one non-null array as a
read-only list view. The composite method presents the first input array
followed by the second input array as one read-only list view. Element changes
made through the original arrays remain observable at the corresponding list
positions when the contract below says the input is retained as a backing
array.

In scope are the exact package and class name, generic type handling, list
size and indexed observation, deterministic ordering, duplicate preservation,
empty arrays, null-array failures, and rejection of list mutation.

Also in scope is the minimal Maven project metadata needed by the offline
harness. Production code belongs under `src/main/java` and must compile with
the declared Java release.

Out of scope are YAML parsing, YAML emitting, serialization, deserialization,
anchors, aliases, tags, comments, reflection-based object construction,
schema configuration, command-line tools, network clients, file persistence,
third-party libraries, and every other SnakeYAML class.

Do not recreate the upstream repository or copy unrelated upstream files.
Do not add a command-line entry point. Do not require a caller to instantiate
`ArrayUtils`; the required operations are static methods.

## Supports

### Natural Language Instruction

Build the project in an empty workspace with the following capabilities:

1. Provide `ArrayUtils.toUnmodifiableList(E[] elements)` with the exact
   generic signature and array-backed observation semantics.
2. Provide
   `ArrayUtils.toUnmodifiableCompositeList(E[] array1, E[] array2)` with the
   exact generic signature, first-array-then-second-array ordering, and the
   specified backing behavior.
3. Return objects that implement `java.util.List<E>` for normal read
   operations such as `size()` and `get(int)` while rejecting structural or
   element mutation through the list interface.
4. Preserve generic element types, repeated values, empty inputs, and the
   documented Java exception behavior without adding global state or I/O.
5. Supply a single Maven project layout that can be validated and compiled
   without downloading dependencies.

The only confidently bindable public API for this task is the `ArrayUtils`
class and the two methods documented below. Other SnakeYAML APIs are not part
of the requested surface and should not be added as substitutes.

### Runtime and package manager

- Operating system: Debian Bookworm on Linux amd64 with glibc.
- Java runtime and compiler: Temurin JDK `21.0.12+8`.
- Java release: compile production code for Java 21.
- Package manager/build tool: Apache Maven `3.9.11`.
- Runtime dependencies: none beyond the Java standard library.
- Candidate dependency list: empty.
- Native code: not required; keep the project independent of cgo, JNI, and
  other native extensions.

The harness performs offline project validation. It may run `mvn --offline
validate` and compile the public class and its contract with `javac --release
21`. The candidate must therefore provide valid Maven metadata even though
the production implementation has no external dependency.

The candidate POM may contain normal project coordinates, packaging, name,
description, and compiler properties. It must not require a repository,
plugin download, profile, module, extension, or custom network-backed build
step. Do not encode a dependency on the full SnakeYAML distribution.

Every stage is offline. The agent, candidate build, candidate tests, verifier,
Oracle, and controls must not access GitHub, Maven Central, DNS, a proxy, or
any other external service at runtime. The implementation itself must not
open files, create sockets, inspect the environment, or invoke subprocesses.

### Project Directory Structure

Create this project tree, using `workspace/` as the project root:

```text
workspace/
|-- pom.xml
`-- src/
    `-- main/
        `-- java/
            `-- org/
                `-- yaml/
                    `-- snakeyaml/
                        `-- util/
                            `-- ArrayUtils.java
```

`pom.xml` is the Maven project descriptor. It must describe one project and
must not declare third-party dependencies for this task.

`src/main/java/org/yaml/snakeyaml/util/ArrayUtils.java` is the only required
production source file. Its package declaration must match its directory.

No CLI, executable script, resource directory, generated source directory,
database, configuration file, or candidate-owned test directory is required.
The harness owns the contract compilation and test setup.

The public entry point is the Java import path below, not a `main` method:

```java
import org.yaml.snakeyaml.util.ArrayUtils;
```

## API Usage Guide

### `ArrayUtils` class

Import the class with:

```java
import org.yaml.snakeyaml.util.ArrayUtils;
```

Use it as a utility class. The task does not require a public constructor or
any instance state. Callers should not need to construct an `ArrayUtils`
object.

The class may use private implementation details, but only the two public
static methods below are part of the contract. Do not expose additional
SnakeYAML APIs in order to satisfy this task.

### `toUnmodifiableList(E[] elements)`

Full signature:

```java
public static <E> java.util.List<E> toUnmodifiableList(E[] elements)
```

Input domain:

- `elements` is a reference to an array of elements of type `E`.
- A non-null array is accepted, including an array of length zero.
- A null array reference is invalid and must fail with
  `NullPointerException`.
- The method does not accept a scalar value in place of an array.

Return contract:

- Return a `java.util.List<E>`.
- The returned list size is exactly `elements.length`.
- For every valid index `i`, `list.get(i)` observes the current value of
  `elements[i]`.
- Preserve the input order exactly, including duplicate and null elements
  stored inside a non-null array.
- The list is not structurally mutable through the `List` API.
- Element-replacement operations such as `set` must be rejected with
  `UnsupportedOperationException` rather than changing the source array.
- The returned list has no global side effect and performs no I/O or network
  access.

Backing and state behavior:

- For a non-empty input, retain the array-view behavior: replacing an array
  element after the call changes the value observed by a later `get` at the
  same position.
- Do not make a defensive element copy that would hide a later replacement.
- The list size remains tied to the original array length; callers cannot
  resize the source array in Java.
- The method does not sort, deduplicate, normalize, or otherwise transform
  elements.
- Repeated reads with an unchanged array are deterministic.

Ordinary example:

```java
String[] names = {"Ada", "Lin"};
java.util.List<String> view = ArrayUtils.toUnmodifiableList(names);
int count = view.size();       // 2
String second = view.get(1);   // "Lin"
```

Backing-update example:

```java
String[] names = {"Ada", "Lin"};
java.util.List<String> view = ArrayUtils.toUnmodifiableList(names);
names[1] = "Grace";
String current = view.get(1);  // "Grace"
```

Empty and error examples:

```java
String[] empty = {};
java.util.List<String> values = ArrayUtils.toUnmodifiableList(empty);
int count = values.size();    // 0
```

```java
ArrayUtils.toUnmodifiableList(null); // throws NullPointerException
```

An index below zero or at least `list.size()` is invalid and must result in
an `IndexOutOfBoundsException` (a more specific standard Java subtype is
acceptable). Calling a mutating `List` operation such as `set`, `add`, or
`remove` must result in `UnsupportedOperationException` when that operation
is reached through the returned list.

### `toUnmodifiableCompositeList(E[] array1, E[] array2)`

Full signature:

```java
public static <E> java.util.List<E> toUnmodifiableCompositeList(
    E[] array1,
    E[] array2
)
```

Input domain:

- Both `array1` and `array2` are array references with the same element type
  `E` (or a type relationship accepted by Java generic array inference).
- Both references must be non-null.
- Either or both arrays may have length zero.
- A null first or second reference is invalid and must fail with
  `NullPointerException`.

Return contract:

- Return one `java.util.List<E>` containing all elements of `array1`, followed
  by all elements of `array2`.
- The returned size is `array1.length + array2.length`.
- For `0 <= i < array1.length`, `get(i)` observes `array1[i]`.
- For `array1.length <= i < array1.length + array2.length`, `get(i)` observes
  `array2[i - array1.length]`.
- Preserve order and duplicate values. Do not sort or deduplicate either
  input.
- Reject list mutation with `UnsupportedOperationException`.
- Invalid indexes must fail with `IndexOutOfBoundsException` or a standard
  subtype.

Backing and state behavior:

- When both arrays are non-empty, later replacement in either source array is
  visible through the corresponding range of the returned list.
- If `array1` is empty, the result contains the elements of `array2` in their
  original order and retains the documented read-only behavior.
- If `array2` is empty, the result contains the elements of `array1` in their
  original order and retains the documented read-only behavior.
- If both arrays are empty, return an empty list with size zero.
- The method must not perform I/O, network access, sorting, deduplication, or
  global state updates.

Ordinary example:

```java
String[] first = {"red", "green"};
String[] second = {"blue"};
java.util.List<String> colors =
    ArrayUtils.toUnmodifiableCompositeList(first, second);
// size() is 3 and get(0), get(1), get(2) are red, green, blue.
```

Backing-update example:

```java
Integer[] first = {1};
Integer[] second = {2, 3};
java.util.List<Integer> values =
    ArrayUtils.toUnmodifiableCompositeList(first, second);
second[0] = 20;
int current = values.get(1);  // 20
```

Empty and error examples:

```java
String[] first = {};
String[] second = {"only"};
java.util.List<String> values =
    ArrayUtils.toUnmodifiableCompositeList(first, second);
// size() is 1 and get(0) is "only".
```

```java
ArrayUtils.toUnmodifiableCompositeList(new String[0], null);
// throws NullPointerException
```

An attempt to read `get(-1)` or `get(values.size())` is out of range and must
not return an element. A `List` mutator such as `set(0, value)`, `add(value)`,
or `remove(0)` must not mutate either source array and must report
`UnsupportedOperationException`.

### Not confidently bindable

No additional public class, function, CLI, serialization format, or YAML API
is confidently bindable for this bounded task. Do not invent or implement
such an API. The full upstream SnakeYAML surface is intentionally excluded.

## Implementation Notes

Keep the implementation compatible with ordinary Java 21 collection usage.
Use the exact package declaration and public method signatures; changing a
generic method to a raw `List`, changing a method to an instance method, or
renaming either array parameter in the callable shape is not acceptable.

The list may be implemented with standard JDK collection support, but its
observable behavior must remain read-only. Returning a mutable list, a list
that copies values when the specification requires a view, or a list that
silently ignores mutation is incorrect.

Null validation applies to the array references, not to individual elements.
An input array containing null elements is still a valid non-null array, and
those elements remain list values in their original positions.

Index validation must be consistent for negative and too-large indexes. Do
not turn an invalid index into a null result or wrap it around to another
position.

Composite indexing must keep the boundary between the two arrays precise.
The first element of the second array is immediately after the last element
of the first array, including when one array is empty.

Preserve deterministic behavior: unchanged arrays produce the same size,
ordering, and values on repeated calls. The methods must not depend on time,
randomness, locale, filesystem contents, environment variables, process
state, or network responses.

The project should remain minimal. Do not add YAML parser classes, dependency
management workarounds, generated code, a CLI, or unrelated modules. The
Maven descriptor and source layout are part of the build contract, while the
actual behavior is defined by the public API sections above.

Small verifiable examples:

1. For `new String[] {"a", "b"}`, the single-array result has size `2`, and
   indexes `0` and `1` observe `"a"` and `"b"` in that order.
2. For `new Integer[] {1}` and `new Integer[] {2, 3}`, the composite result
   has size `3` and observes `1`, `2`, then `3`.
3. Replacing an element in either original array after creating a non-empty
   view changes the value returned for that corresponding index.
4. Empty arrays produce a zero-length result where applicable; null array
   references fail instead of being treated as empty arrays.

These examples describe externally observable behavior only. Do not copy an
upstream implementation or hidden test code, and do not add private verifier
details to the project.
