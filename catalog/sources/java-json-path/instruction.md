## Project Description

Recreate a small, deterministic Java library named `java-json-path`.

The project is a bounded slice of the JsonPath API. Its job is to accept a
path expression, validate the expression, retain its normalized text, and
classify whether it can identify at most one location. The implementation is
used by Java callers that need path compilation without reading a JSON
document.

The target is an installable Maven project, not a copy of the complete
upstream JsonPath library. Keep the public package name exactly
`com.jayway.jsonpath`. A caller must be able to compile a path, inspect its
normalized spelling, and ask whether it is definite using ordinary Java
method calls.

### Natural Language Instruction

Create the project in an empty `workspace/` directory and implement the
bounded public contract described in this document.

1. Provide `com.jayway.jsonpath.JsonPath` as the public compiled-path value.
2. Provide the static `JsonPath.compile(String, Predicate...)` factory with
   validation, normalization, and deterministic state.
3. Provide `JsonPath.getPath()` so callers can read the normalized path text.
4. Provide `JsonPath.isDefinite()` and
   `JsonPath.isPathDefinite(String)` using the same classification rules.
5. Provide the public `com.jayway.jsonpath.Predicate` type so the documented
   varargs signature can be compiled. This bounded task accepts predicate
   references but does not evaluate or dereference them.
6. Provide `com.jayway.jsonpath.InvalidPathException` as the unchecked error
   for invalid path input.

The package, class names, method visibility, static modifiers, parameter
types, return types, and exception behavior above are part of the contract.
Do not substitute a different package, a builder-only API, a JSON parser, or
an unrelated command-line interface.

This task must remain a pure library slice. Do not add JSON document reading,
provider selection, object mapping, mutation, serialization, cache storage,
filesystem access, URL access, stream access, or network clients. Do not
make the result depend on the current time, locale, process environment,
randomness, thread identity, or external resources.

## Supports

### Environment Configuration

Use the following runtime and build boundary:

```text
Language: Java
Runtime: Temurin JDK 21.0.12+8
Package manager: Maven 3.9.11
Platform: Linux amd64 with glibc
Build mode: Maven project, single module
Runtime dependencies: none
Candidate build: Maven metadata and the JDK only
Network during agent/candidate/verifier/Oracle/controls execution: unavailable
```

The implementation must build with Java release 21. The project must not
download artifacts or contact GitHub, Maven Central, DNS, or another external
service while it is being tested. Keep the `pom.xml` minimal and avoid
undeclared dependencies, repositories, plugins, profiles, modules, and custom
Maven extensions. The candidate `pom.xml` is installation metadata; it is not
an invitation to add a third-party JsonPath dependency.

### Project Directory Structure

Create this structure under the empty workspace. Names are case-sensitive.

```text
workspace/
|- pom.xml
`- src/
   `- main/
      `- java/
         `- com/
            `- jayway/
               `- jsonpath/
                  |- JsonPath.java
                  |- InvalidPathException.java
                  `- Predicate.java
```

`pom.xml` must identify a single Maven artifact and compile the Java sources
with release 21. The source root must be `src/main/java`. There is no CLI
entry point in this task, so do not invent a `main` class or shell script.
There are no required resources, service loaders, test fixtures, or runtime
configuration files.

The directory tree and the import paths below must agree. In particular,
`JsonPath.java` must declare `package com.jayway.jsonpath;`, and the two
supporting source files must declare the same package.

### Public Surface Boundary

The confidently bindable public surface is intentionally small:

| Type | Confidently bindable contract |
| --- | --- |
| `com.jayway.jsonpath.JsonPath` | `compile`, `getPath`, `isDefinite`, and `isPathDefinite` |
| `com.jayway.jsonpath.Predicate` | Public type used by the compile varargs parameter; no callable member is confidently bound here |
| `com.jayway.jsonpath.InvalidPathException` | Public unchecked error type for invalid path input; constructor signatures are not confidently bound here |

Do not add undocumented public methods to make the task appear larger. APIs
from the full upstream distribution, including JSON providers, read methods,
mapping methods, filters, predicates with execution context, configuration,
and mutation are not part of this contract.

## API Usage Guide

### `com.jayway.jsonpath.JsonPath`

Import the compiled path type with:

```java
import com.jayway.jsonpath.JsonPath;
import com.jayway.jsonpath.InvalidPathException;
import com.jayway.jsonpath.Predicate;
```

`JsonPath` represents one successfully compiled path expression. A compiled
instance stores the normalized path text and its definiteness classification.
Those values are established by compilation and must not change after the
factory returns.

#### `JsonPath.compile`

Signature:

```java
public static JsonPath compile(String jsonPath, Predicate... filters)
```

`jsonPath` is the required path expression. Reject `null`, the empty string,
and a string that becomes empty after trimming. A valid expression may use
the `$` root marker or the `@` current-context marker. A bare property path
is interpreted relative to `$` and receives the `$.` prefix in normalized
text.

The bounded syntax includes property steps written with dots, quoted
properties in brackets, a single non-negative numeric array index, wildcard
steps, descendant scans, comma-separated indexes, slices, filter-shaped
expressions, and function-shaped suffixes. These forms are classified by
their path shape; this task does not evaluate them against JSON data.

`filters` is a possibly empty varargs array. It exists to preserve the public
compile signature. The bounded implementation must not invoke, inspect, or
dereference a supplied predicate object. A `null` element is therefore not a
reason to read external state; it is simply not evaluated by this slice.

The return value is a non-null `JsonPath` whose `getPath()` and
`isDefinite()` results are deterministic for the same input. Compilation has
no filesystem, environment, network, or global-state side effects.

Throw `com.jayway.jsonpath.InvalidPathException` for null or blank input, a
trailing dot or descendant marker, an unclosed or malformed bracket
expression, or another path spelling that cannot be validated by the bounded
grammar. This is an unchecked exception. Do not return `null` or silently
accept malformed delimiters.

Normal example:

```java
JsonPath path = JsonPath.compile("$.store.book[0].title");
String text = path.getPath();
boolean oneLocation = path.isDefinite();
```

For that example, `text` is `"$.store.book[0].title"` and
`oneLocation` is `true`.

Edge example:

```java
try {
    JsonPath.compile("$.store.book[");
    throw new AssertionError("malformed input must fail");
} catch (InvalidPathException expected) {
    // The unchecked contract is satisfied.
}
```

#### `JsonPath.getPath`

Signature:

```java
public String getPath()
```

This accessor returns the normalized path text as a non-null `String`. It
does not read JSON, consult a provider, mutate the object, or perform I/O.
Repeated calls return equal text and do not alter the definiteness result.

Surrounding whitespace is removed during compilation. A bare property
expression is normalized under `$`; an expression already beginning with
`$` or `@` retains that context. Do not normalize by locale or by a
filesystem-specific path separator: JsonPath syntax uses its own textual
delimiters.

Normal example:

```java
JsonPath path = JsonPath.compile("  store.book  ");
assert "$.store.book".equals(path.getPath());
```

Edge example:

```java
JsonPath path = JsonPath.compile("@.book");
assert "@.book".equals(path.getPath());
assert path.getPath().equals(path.getPath());
```

#### `JsonPath.isDefinite`

Signature:

```java
public boolean isDefinite()
```

Return `true` only when the compiled path consists of a root or context,
property steps, and single non-negative numeric array indexes. Such a path
can select at most one location under this bounded classification.

Return `false` for a descendant scan (`..`), wildcard (`*`), multiple index
selection, a slice, a filter-shaped step, or a function-shaped suffix. The
method returns a primitive boolean, is deterministic, and has no side
effects. It does not evaluate a predicate or inspect a JSON document.

Normal example:

```java
assert JsonPath.compile("$.store.book[0].title").isDefinite();
```

Edge example:

```java
assert !JsonPath.compile("$.store.book[*].title").isDefinite();
assert !JsonPath.compile("$.store.book[0,1]").isDefinite();
```

#### `JsonPath.isPathDefinite`

Signature:

```java
public static boolean isPathDefinite(String path)
```

This static convenience query validates and classifies one path without
requiring the caller to retain a `JsonPath` object. It accepts the same
string domain as `compile`, applies the same normalization-independent
classification, and returns the same boolean that
`JsonPath.compile(path).isDefinite()` would return.

For null, blank, trailing-dot, or malformed input, throw the same unchecked
`InvalidPathException` as `compile`. Do not create a second grammar with
different acceptance or exception rules. The method has no I/O or global
state side effects.

Normal example:

```java
assert JsonPath.isPathDefinite("store.book[0]");
```

Edge example:

```java
assert !JsonPath.isPathDefinite("$.store.book[0:2]");
try {
    JsonPath.isPathDefinite(" ");
    throw new AssertionError("blank input must fail");
} catch (InvalidPathException expected) {
    // expected
}
```

### `com.jayway.jsonpath.Predicate`

Import path:

```java
import com.jayway.jsonpath.Predicate;
```

`Predicate` is the public type named by the `JsonPath.compile` varargs
signature. The bounded task only requires that callers can pass zero or more
values of this type to `compile`. Predicate evaluation, callback invocation,
context objects, and predicate serialization are explicitly out of scope.

No callable member or constructor signature is confidently bindable from the
task-local source material available to this author. Do not invent methods on
this type. A normal compile call therefore uses no filters:

```java
JsonPath path = JsonPath.compile("$.book[0]");
```

The edge contract is that a supplied reference is not dereferenced by this
bounded slice. The implementation must still validate the path itself:

```java
Predicate optional = null;
JsonPath path = JsonPath.compile("$.book[0]", optional);
assert path.isDefinite();
```

### `com.jayway.jsonpath.InvalidPathException`

Import path:

```java
import com.jayway.jsonpath.InvalidPathException;
```

This public unchecked exception identifies invalid input to `compile` or
`isPathDefinite`. The exact constructor surface is not confidently bindable
from the available task-local source material, so callers should catch the
type rather than depend on an undocumented constructor or message format.

The exception is required for null, blank, trailing-dot, unclosed-bracket,
and malformed-path cases. Its message, if present, is not a stable output
contract. It must not expose private test details, filesystem paths, or
network responses.

Normal handling:

```java
try {
    JsonPath.compile("$.book.");
} catch (InvalidPathException expected) {
    // Report invalid user input.
}
```

Edge handling:

```java
for (String invalid : new String[] { null, "", "   ", "$.book[" }) {
    try {
        JsonPath.isPathDefinite(invalid);
        throw new AssertionError("invalid input was accepted");
    } catch (InvalidPathException expected) {
        // Each case has the same unchecked exception contract.
    }
}
```

## Implementation Notes

Keep all three public types in the one package shown in the directory tree.
The source and Maven coordinates must agree so a clean offline Maven build
can compile the package without a downloaded JsonPath dependency.

Use one validation and classification contract for both static and instance
entry points. `isPathDefinite(path)` must not drift from
`compile(path).isDefinite()` on roots, properties, indexes, scans, wildcards,
slices, multiple indexes, filters, functions, or invalid delimiters.

The normalized string and boolean classification should be stable after
construction. Calling `getPath()` repeatedly must not reparse mutable global
state. Calling `isDefinite()` repeatedly must return the same primitive
value. No API in this task should create files, read environment variables,
open sockets, load services, or depend on time or randomness.

Small verifiable cases include:

```java
JsonPath a = JsonPath.compile("$.store.book[0].title");
assert a.isDefinite();
assert "$.store.book[0].title".equals(a.getPath());

JsonPath b = JsonPath.compile("store.book");
assert "$.store.book".equals(b.getPath());

assert !JsonPath.compile("$.store.book[*]").isDefinite();
assert !JsonPath.compile("$.store..title").isDefinite();
```

Additional boundary cases should cover `@` context, whitespace around a
valid expression, a single index versus a slice, and malformed bracket
closure. Keep examples small and public-contract based; do not copy private
leaf tests, verifier protocols, source files, or expected grader artifacts.

Preserve ordering and spelling rules stated above. A path is text, not an OS
filesystem path, so platform separators and locale-sensitive case conversion
must not affect results. Property order is the order in the input expression;
the API must not sort or deduplicate path steps as a side effect of compiling.

The task has no CLI. Do not add a `main` method, shell entry point, network
service, JSON provider, or document evaluation layer. Do not expose extra
upstream APIs merely because their names are familiar. APIs not listed in
this instruction, including any additional `Predicate` members and
`InvalidPathException` constructors, are not confidently bindable and must
be omitted from the public contract.

Before considering the project complete, verify a clean Java 21 Maven build
with offline settings, check that imports use `com.jayway.jsonpath`, and
exercise both successful and exception paths. Keep the implementation
deterministic and suitable for an isolated no-network verifier.
