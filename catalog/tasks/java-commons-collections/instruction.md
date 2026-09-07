## Project Description

### Natural Language Instruction

Create a small Java Maven project that provides the documented, bounded slice of
Apache Commons Collections represented by `CollectionUtils`. The project is a
library task, not a command-line application. It must compile from an empty
workspace with the standard Maven layout and expose the public class and
methods described below.

The target user is a Java developer who needs null-safe collection predicates,
element counting, membership checks, duplicate-aware collection comparison,
conditional insertion, and size inspection. The implementation must use the
package name shown in the API guide and must keep the public behavior
deterministic for the same inputs.

The required capabilities are:

1. Treat a null `Collection` as empty for the two documented emptiness
   predicates.
2. Count equal values in an `Iterable`, including repeated occurrences.
3. Determine whether two collections have at least one common element.
4. Compare collections as multisets, so element multiplicity matters while
   encounter order does not.
5. Add a non-null value through ordinary `Collection.add` behavior and report
   whether the collection changed.
6. Inspect the size of supported collection-like Java objects, including
   collections, maps, object arrays, primitive arrays, and general iterables.

Only the public `CollectionUtils` surface documented here is required. Do not
implement unrelated Commons Collections decorators, maps, queues, iterators,
functors, command-line tools, shell scripts, or extra packages. No CLI or
standalone executable entry point is confidently bindable for this task.

### Project Directory Structure

Create the following project rooted at `workspace/`:

```text
workspace/
|- pom.xml
`- src/
   `- main/
      `- java/
         `- org/
            `- apache/
               `- commons/
                  `- collections4/
                     `- CollectionUtils.java
```

`pom.xml` must describe one ordinary Maven project. It must not add runtime
dependencies, modules, custom repositories, network-dependent build steps, or
candidate-controlled verifier code. `CollectionUtils.java` must declare the
public class in exactly `org.apache.commons.collections4`.

The class is a utility class and should not require construction by callers.
The documented APIs are static; callers should not need an application main
method. Keep implementation files under `src/main/java` and do not move the
class into the default package or an alternate Commons package.

## Supports

### Environment Configuration

Use the following fixed build and runtime boundary:

- Language: Java.
- Java runtime and compiler: Temurin JDK 21.0.12+8.
- Build tool: Apache Maven 3.9.11.
- Platform: Linux amd64 with glibc.
- Runtime dependencies: none beyond the Java standard library.
- Network policy: no network during agent, candidate, verifier, Oracle, or
  controls execution.
- Maven commands must work offline; do not fetch GitHub, Maven Central, DNS,
  or any external service at runtime.
- The project is a single module and has no required external artifact.

The expected project checks are equivalent to `mvn --offline validate` followed
by compilation of the public class. Keep the POM minimal so offline Maven can
read it without requiring plugins or repositories that are not already
available. Do not encode behavior in Maven profiles or custom extensions.

### Public Module Import

Callers import the only required public class as follows:

```java
import org.apache.commons.collections4.CollectionUtils;
```

The class declaration is:

```java
public final class CollectionUtils
```

Its constructor is not part of the callable API. Utility methods are static and
must not depend on mutable global state, system properties, the filesystem,
network access, locale, or wall-clock time.

### isEmpty

Signature:

```java
public static boolean isEmpty(Collection<?> coll)
```

Input domain:

- `coll` may be null, an empty collection, or a non-empty collection.
- The method accepts any implementation of `java.util.Collection`.
- It does not accept a map, array, or arbitrary `Iterable` as a substitute for
  the declared collection type.

Return and side effects:

- Returns `true` when `coll` is null or `coll.isEmpty()` is true.
- Returns `false` for a non-empty collection.
- Returns the primitive type `boolean` and does not mutate the collection.
- It is deterministic for the collection state at the call.

Errors and examples:

- A null input is valid and returns `true`; no exception is thrown.
- A collection whose `isEmpty()` implementation throws may propagate that
  unchecked exception, as ordinary collection method behavior is not masked.
- Normal example: `CollectionUtils.isEmpty(List.of())` returns `true`.
- Edge example: `CollectionUtils.isEmpty(null)` returns `true`.

### isNotEmpty

Signature:

```java
public static boolean isNotEmpty(Collection<?> coll)
```

Input and result contract:

- Accepts the same `Collection<?>` domain as `isEmpty`, including null.
- Returns `true` exactly when the collection is non-null and non-empty.
- Returns `false` for null and for an empty collection.
- Does not mutate the collection or establish persistent state.

Normal example: `CollectionUtils.isNotEmpty(List.of("red"))` returns `true`.

Edge example: `CollectionUtils.isNotEmpty(null)` returns `false`.

The result must remain logically complementary to `isEmpty` for every valid
collection state: `isNotEmpty(coll) == !isEmpty(coll)`.

### cardinality

Signature:

```java
public static <O> int cardinality(O obj, Iterable<? super O> collection)
```

Input domain and matching:

- `obj` may be null or any value comparable by `Objects.equals` semantics.
- `collection` must be a non-null `Iterable<? super O>`.
- Iterate every element exactly once and count each element equal to `obj`.
- Repeated values count repeatedly; do not collapse the input into a set.

Return, ordering, and side effects:

- Returns a non-negative primitive `int` count.
- Encounter order does not change the numeric result, although traversal is in
  the iterable's normal iterator order.
- The method does not mutate the iterable or its elements.
- The result is deterministic when the iterable and equality behavior are
  stable.

Errors and examples:

- A null `collection` is invalid and must be rejected with the normal unchecked
  null-argument exception, such as `NullPointerException`.
- A null `obj` is valid and counts null elements.
- Exceptions thrown by the iterable's iterator or by element equality may
  propagate unchanged.
- Normal example: `cardinality("a", List.of("a", "b", "a"))` returns `2`.
- Edge example: `cardinality(null, Arrays.asList(null, "a", null))` returns `2`.

### containsAny

Signature:

```java
public static boolean containsAny(Collection<?> coll1, Collection<?> coll2)
```

Input and behavior:

- Both arguments must be non-null `Collection<?>` instances.
- Return `true` if at least one element of either collection is equal to an
  element of the other collection.
- Return `false` when either collection is empty or when there is no shared
  value.
- Duplicate occurrences do not affect the boolean result.

Ordering and side effects:

- The result is independent of argument order and encounter order.
- The implementation may inspect the smaller collection first, but this is an
  internal optimization and must not alter observable behavior.
- Neither collection may be modified.

Errors and examples:

- A null `coll1` or `coll2` is invalid and must result in an unchecked
  null-argument exception, such as `NullPointerException`.
- Exceptions from collection iteration or `contains` may propagate.
- Normal example: `containsAny(List.of("a", "b"), List.of("x", "b"))` returns
  `true`.
- Edge example: `containsAny(List.of(), List.of("b"))` returns `false`.

### isEqualCollection

Signature:

```java
public static boolean isEqualCollection(Collection<?> a, Collection<?> b)
```

Input and multiset semantics:

- Both arguments must be non-null collections.
- Two collections are equal when every value has the same number of
  occurrences in both collections.
- Encounter order is ignored.
- Duplicate counts are significant: two `a` values do not equal one `a` value.
- Null elements are values and must be counted consistently.

Return and side effects:

- Returns a primitive `boolean`.
- Returns `false` immediately when collection sizes differ.
- Returns `true` for equal frequency maps and `false` otherwise.
- Does not mutate either collection and has no filesystem, network, or global
  state side effect.

Errors and examples:

- A null `a` or `b` is invalid and must result in an unchecked null-argument
  exception, such as `NullPointerException`.
- Exceptions from iteration, hashing, or equality may propagate according to
  the input collection and element implementations.
- Normal example: `isEqualCollection(List.of("a", "a", "b"),
  List.of("b", "a", "a"))` returns `true`.
- Edge example: `isEqualCollection(List.of("a", "a"), List.of("a"))`
  returns `false`.

### addIgnoreNull

Signature:

```java
public static <T> boolean addIgnoreNull(Collection<T> collection, T object)
```

Input, mutation, and result:

- `collection` must be a non-null mutable or otherwise add-capable
  `Collection<T>`.
- `object` may be null or a non-null value accepted by the collection.
- If `object` is null, return `false` and do not call `add` or mutate the
  collection.
- If `object` is non-null, delegate to the collection's ordinary `add`
  behavior and return the boolean it reports.
- A collection may reject an otherwise non-null value according to its own
  contract; do not fabricate a successful result.

Errors and examples:

- A null `collection` is invalid even when `object` is null and must result in
  an unchecked null-argument exception, such as `NullPointerException`.
- An unmodifiable collection can throw `UnsupportedOperationException` for a
  non-null object; that unchecked exception may propagate.
- Normal example: adding `"c"` to `ArrayList.of("a", "b")` returns `true` and
  leaves `a,b,c` in encounter order.
- Edge example: adding null returns `false` and leaves the collection exactly
  unchanged.

### size

Signature:

```java
public static int size(Object object)
```

Supported input shapes:

- Null has size zero.
- A `Map<?, ?>` returns `Map.size()`.
- A `Collection<?>` returns `Collection.size()`.
- An object array returns its array length.
- A primitive array such as `int[]` returns its reflective array length.
- An `Iterable<?>` that is not handled by an earlier supported shape is
  traversed and counted.

Return and side effects:

- Returns the number of entries as a primitive non-negative `int`.
- Map and collection order do not affect the count.
- Counting a general iterable consumes its iterator and may therefore have the
  observable side effect of advancing a one-shot iterable; do not assume it is
  repeatable.
- The method does not mutate maps, collections, arrays, or their elements.

Errors and examples:

- An object of an unsupported type must be rejected with
  `IllegalArgumentException`; do not return a guessed count.
- Iterator, collection, map, or reflective-array failures may propagate as
  unchecked exceptions.
- Normal example: `size(Map.of("a", 1, "b", 2))` returns `2`.
- Edge example: `size(new int[] {1, 2, 3})` returns `3`, while `size(null)`
  returns `0`.

### sizeIsEmpty

Signature:

```java
public static boolean sizeIsEmpty(Object object)
```

Input and result:

- Accepts the same supported object shapes and unsupported-input boundary as
  `size`.
- Returns `true` exactly when `size(object)` is zero.
- Null is valid and returns `true`.
- An unsupported non-null object must produce the same
  `IllegalArgumentException` boundary as `size`, rather than being treated as
  empty.

Normal example: `sizeIsEmpty(Collections.emptyList())` returns `true`.

Edge example: `sizeIsEmpty(new String[] {"x"})` returns `false`.

## API Usage Guide

### Typical Composition

The methods can be used together without hidden state:

```java
List<String> values = new ArrayList<>(List.of("red", "red", "blue"));
boolean present = CollectionUtils.isNotEmpty(values);
int reds = CollectionUtils.cardinality("red", values);
boolean hasBlue = CollectionUtils.containsAny(values, List.of("blue"));
boolean added = CollectionUtils.addIgnoreNull(values, "green");
int total = CollectionUtils.size(values);
```

The example should produce `present == true`, `reds == 2`, `hasBlue == true`,
`added == true`, and `total == 4` with an `ArrayList`.

### Boundary Examples

```java
CollectionUtils.isEmpty(null);                 // true
CollectionUtils.isNotEmpty(Collections.emptyList()); // false
CollectionUtils.cardinality("x", List.of());  // 0
CollectionUtils.isEqualCollection(
    List.of("x", "x"), List.of("x"));        // false
CollectionUtils.addIgnoreNull(values, null);   // false; no mutation
CollectionUtils.size(new long[] {1L, 2L});      // 2
CollectionUtils.sizeIsEmpty(null);              // true
```

Do not rely on the textual representation of collections, hash-map iteration
order, object identity, or a particular concrete collection implementation.
Use the declared Java interfaces and preserve the specified return and
exception contracts.

### Not Confidently Bindable

No CLI command, executable main class, configuration file format, persistence
format, or additional public Commons Collections class is confidently bindable
from the task-local solution. Do not add one to satisfy an assumed upstream
API. Private helper methods, verifier harness classes, and build-only files are
not public task APIs.

## Implementation Notes

### Cross-Module Constraints

- Keep `CollectionUtils` in the exact package and file path shown above.
- Keep the project single-module and standard Maven; Java source belongs under
  `src/main/java`.
- Use only JDK classes such as `java.util.Collection`, `Iterable`, `Map`, and
  reflection support for primitive arrays.
- Do not add a runtime dependency, network fetch, plugin repository, shell
  integration, or alternate package alias.
- Preserve generic signatures so callers can compile against the documented
  methods without casts not required by the API.

### Determinism and State

The methods are pure with respect to process-global state. Apart from the
explicit mutation performed by `addIgnoreNull` for a non-null value, callers'
objects must not be changed. Collection comparison must use values and their
frequencies, not iteration order. Size inspection must not sort, serialize, or
otherwise normalize inputs. No method may read files, write files, access the
network, consult environment variables, or depend on the current time.

For mutable collections, document behavior in terms of the state observed
during the call. Concurrent mutation is outside the supported contract; do
not introduce synchronization that changes ordinary Java collection semantics.

### Verifiable Examples

1. `isEmpty(null)` is `true`, and `isNotEmpty(null)` is `false`.
2. `cardinality("a", List.of("a", "b", "a"))` is `2`.
3. `isEqualCollection(List.of("a", "b", "a"),
   List.of("b", "a", "a"))` is `true`, while comparing it with
   `List.of("a", "b")` is `false`.
4. `addIgnoreNull(new ArrayList<>(List.of("a")), null)` returns `false` and
   leaves the list unchanged; adding `"b"` delegates to `add` and returns its
   result.
5. `size(Map.of("k", 1))` is `1`, `size(new byte[0])` is `0`, and
   `sizeIsEmpty(new byte[0])` is `true`.
6. `size("not a supported collection-like value")` raises
   `IllegalArgumentException` rather than returning the string length.

These examples are behavioral guidance, not an algorithm prescription. Keep
the implementation readable and compatible with ordinary JDK collection
contracts while honoring every declared input, output, mutation, and error
boundary.
