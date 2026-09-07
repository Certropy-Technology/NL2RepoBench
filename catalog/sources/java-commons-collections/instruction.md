# Introduction and Goals of the Commons Collections Project

Apache Commons Collections is a Java utility library for working with
collections. This task implements a bounded, deterministic public slice of
`CollectionUtils`: null-safe emptiness checks, membership checks, cardinality,
multiset comparisons, and collection mutation helpers. The result must be a
normal single-module Maven project with the requested public class and
methods.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Collections that implements
the following public behavior:

1. Provide null-safe checks for empty and non-empty collections.
2. Count occurrences of a value in an iterable collection.
3. Determine whether two collections share an element.
4. Compare collections using element cardinality, so duplicate values matter.
5. Add a non-null value to a collection while reporting whether it changed.
6. Report the size of supported collection-like inputs and whether such an
   input is empty.
7. Keep the implementation under `src/main/java` in a single-module Maven
   project without external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime
Maven 3.9.11                # Offline project tooling
Linux amd64                 # Fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # Agent and verifier are offline
```

## Commons Collections Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── commons
                        └── collections4
                            └── CollectionUtils.java
```

The candidate POM is metadata only. Do not use Maven plugins, repositories,
dependencies, profiles, modules, or custom build extensions to control the
verifier.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.commons.collections4.CollectionUtils;
```

#### 2. Emptiness Checks

```java
boolean empty = CollectionUtils.isEmpty(values);
boolean present = CollectionUtils.isNotEmpty(values);
```

Signatures:

```java
static boolean isEmpty(Collection<?> coll)
static boolean isNotEmpty(Collection<?> coll)
```

Both methods are null-safe. A null collection is empty and is not non-empty.

#### 3. cardinality() - Count an Element

```java
int count = CollectionUtils.cardinality("red", values);
```

Signature:

```java
static <O> int cardinality(O obj, Iterable<? super O> collection)
```

The result is the number of elements equal to `obj`, including duplicates.

#### 4. containsAny() - Check Shared Membership

```java
boolean shared = CollectionUtils.containsAny(left, right);
```

Signature:

```java
static boolean containsAny(Collection<?> coll1, Collection<?> coll2)
```

The result is true when at least one element from the second collection occurs
in the first collection. Empty inputs produce false.

#### 5. isEqualCollection() - Compare Cardinalities

```java
boolean same = CollectionUtils.isEqualCollection(left, right);
```

Signature:

```java
static boolean isEqualCollection(Collection<?> a, Collection<?> b)
```

Order does not matter, but duplicate counts do. For example, `[a, a, b]`
equals `[b, a, a]` and does not equal `[a, b]`.

#### 6. addIgnoreNull() - Conditional Mutation

```java
boolean changed = CollectionUtils.addIgnoreNull(values, "new-value");
```

Signatures:

```java
static <T> boolean addIgnoreNull(Collection<T> collection, T object)
```

The method adds the value when it is non-null and returns whether the
collection changed. A null value is ignored and returns false. A null
collection is rejected.

#### 7. size() and sizeIsEmpty() - Inspect Supported Inputs

```java
int size = CollectionUtils.size(values);
boolean empty = CollectionUtils.sizeIsEmpty(values);
```

Signatures:

```java
static int size(Object object)
static boolean sizeIsEmpty(Object object)
```

For a collection, size is its element count. Null has size zero and is empty.

### Actual Usage Modes

#### Basic Collection Checks

```java
List<String> values = Arrays.asList("a", "b");
CollectionUtils.isNotEmpty(values); // true
CollectionUtils.cardinality("a", values); // 1
```

#### Duplicate-Aware Comparison

```java
CollectionUtils.isEqualCollection(
    Arrays.asList("a", "a", "b"), Arrays.asList("b", "a", "a")); // true
```

### Supported Function Types

The supported function types are null-safe collection predicates, occurrence
counting, membership checks, duplicate-aware equality, conditional mutation,
size inspection, deterministic ordering, and standard Java
exception behavior. Do not implement unrelated decorators, functors, maps, or
iterators.

### Error Handling

Null-safe methods must retain their null behavior. Methods whose public
contract requires non-null collections must reject null inputs with the normal
Java exception rather than returning fabricated data. Invalid indexes or
unsupported input shapes for `size` follow the public method contract.

## Detailed Implementation Nodes of Functions

### Node 1: Null-Safe Emptiness

Implement `isEmpty` and `isNotEmpty` consistently for null, empty, and
non-empty collections.

### Node 2: Cardinality

Count every equal occurrence in encounter order without collapsing duplicates.

### Node 3: Shared Membership

Determine whether two collections share any value while handling empty inputs
deterministically.

### Node 4: Duplicate-Aware Equality

Compare value frequencies rather than only comparing `containsAll` or order.

### Node 5: Conditional Mutation

Add non-null values exactly once per invocation according to ordinary
`Collection.add` behavior, and ignore null values without mutating the input.

### Node 6: Size Inspection

Return the correct count and empty result for supported collection-like values,
including null and empty inputs.

### Node 7: Offline Maven Layout

Use the exact public package, standard Maven source layout, Java 21, and no
network or candidate-controlled Maven build configuration.

### Node 8: Contract Boundaries

Implement only the documented `CollectionUtils` methods. Do not expose
unrequested overloads or rely on the upstream project's build plugins,
transitive dependencies, or test framework.
