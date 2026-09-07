## Project Description

### Natural Language Instruction

Recreate the bounded, deterministic filtering slice of the Java Reflections
library as a small Maven project. The package is used by code that needs to
accept or reject fully qualified class or resource names before a scanner
consumes them. This task is about the local predicate builder, not about
discovering classes.

The candidate must provide the public class
`org.reflections.util.FilterBuilder` and the public exception class
`org.reflections.ReflectionsException`. `FilterBuilder` implements
`java.util.function.Predicate<String>` and maintains an ordered, fluent chain
of include and exclude predicates. Its results must be deterministic for a
given sequence of calls and a given input string.

In scope:

- Constructing an empty filter builder.
- Adding regular-expression include and exclude predicates.
- Mapping literal package prefixes to descendant-name patterns.
- Parsing comma-separated `+` and `-` package specifications.
- Evaluating the ordered chain with `test(String)`.
- Returning the same builder from fluent mutators.
- Exposing the three documented `ReflectionsException` constructors.
- Compiling the two classes with the Java standard library only.

The bounded contract does not require classpath scanning, class loading,
annotation inspection, URL or filesystem traversal, jar handling, metadata
stores, serializers, query builders, or any other Reflections subsystem. Do
not add a command-line application, network service, persistence layer,
native code, or runtime dependency. The verifier interacts with the candidate
through its own Java-side contract and does not require the candidate to
implement a scanner.

The source package layout and public names are part of the contract. Keep the
filter type in `org.reflections.util` and the exception type in
`org.reflections`; changing either package makes the implementation
unusable by callers.

## Supports

The runtime is Linux amd64 with glibc, Temurin JDK `21.0.12+8`, and Maven
`3.9.11`. Use the Java standard library and compile for Java release 21.
The project has no runtime or test dependency that the candidate must add.
The supplied `pom.xml` is metadata only; do not introduce dependencies,
plugins, profiles, repositories, modules, extensions, or custom build steps.

Network access is unavailable to the agent, candidate, verifier, Oracle, and
controls. The implementation must work offline and must not download data at
runtime. Maven metadata validation may be invoked offline, but the contract
itself only needs JDK classes such as `Pattern`, `Predicate`, `List`, and
`RuntimeException`.

### Project Directory Structure

Use this project directory layout, rooted at `workspace/`:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── reflections/
                    ├── ReflectionsException.java
                    └── util/
                        └── FilterBuilder.java
```

The entry points are Java calls, not a CLI. The fully qualified entry points
are `org.reflections.util.FilterBuilder` and
`org.reflections.ReflectionsException`. There is no required `main` method.
The harness prepares the workspace, supplies or validates the Maven metadata,
compiles the candidate-owned sources, and invokes the public classes from a
separate verifier process. Do not assume that verifier classes are available
on the candidate compile classpath.

Keep source files under `src/main/java`. The verifier owns test collection,
JUnit reporting, process limits, and grading. Candidate code must not write
trusted reports, change the verifier, or rely on files outside the workspace.

## API Usage Guide

### `org.reflections.util.FilterBuilder`

`FilterBuilder` is a public class implementing
`java.util.function.Predicate<String>`. Each mutating method appends one
predicate to the receiver's ordered chain. The methods below return the same
receiver unless explicitly described as static. Calls do not mutate global
state and do not perform I/O.

Typical imports are:

```java
import org.reflections.util.FilterBuilder;
import org.reflections.ReflectionsException;
```

### `FilterBuilder()`

Signature: `public FilterBuilder()`.

Create an empty builder. An empty chain accepts every input passed to
`test(String)`, including the empty string. Construction has no arguments,
no external effects, and no failure mode beyond ordinary JVM allocation
failure.

Ordinary example:

```java
FilterBuilder allNames = new FilterBuilder();
boolean accepted = allNames.test("org.example.Service"); // true
```

Edge example:

```java
FilterBuilder empty = new FilterBuilder();
boolean accepted = empty.test(""); // true
```

### `includePattern(String)`

Import path: `org.reflections.util.FilterBuilder`.

Signature: `public FilterBuilder includePattern(String regex)`.

Append an include predicate compiled from the supplied Java regular
expression and return the same builder instance. The expression is evaluated
with Java `Pattern` matching over the complete input string, not a substring
search. Include predicates can move the current result from rejected to
accepted when they match. The regular expression is compiled when the method
is called, so an invalid expression must surface Java's normal pattern
compilation exception. A null argument may fail with the normal Java runtime
null behavior.

Ordering is significant: this predicate is evaluated after all predicates
already appended and before later predicates. The operation is deterministic
and has no I/O or global side effect.

Ordinary example:

```java
FilterBuilder names = new FilterBuilder()
    .includePattern("org\\.example\\..*");
boolean accepted = names.test("org.example.Service"); // true
```

Edge example:

```java
FilterBuilder exact = new FilterBuilder()
    .includePattern("org\\.example\\..*");
boolean accepted = exact.test("org.example"); // false; no descendant suffix
```

### `excludePattern(String)`

Signature: `public FilterBuilder excludePattern(String regex)`.

Append an exclude predicate compiled from the supplied Java regular
expression and return the same builder. The predicate rejects complete-string
matches and otherwise leaves the current result accepted. The expression is
compiled using Java `Pattern`; invalid expressions and null arguments retain
normal Java runtime failure behavior. Evaluation remains in insertion order.

An exclusion can override an accepted result when it matches. Once a matching
exclusion changes an accepted result to rejected, evaluation stops at that
exclusion. A nonmatching exclusion is skipped while the current result is
already rejected.

Ordinary example:

```java
FilterBuilder publicNames = new FilterBuilder()
    .includePattern("org\\.example\\..*")
    .excludePattern("org\\.example\\.internal\\..*");
boolean accepted = publicNames.test("org.example.internal.Hidden"); // false
```

Edge example:

```java
FilterBuilder noMatch = new FilterBuilder()
    .excludePattern("org\\.secret\\..*");
boolean accepted = noMatch.test("org.example.Service"); // true
```

### `includePackage(String)`

Signature: `public FilterBuilder includePackage(String value)`.

Append an include predicate for descendants of a literal package prefix and
return the same builder. The supplied package text is treated as literal
package text: dots and dollar signs are escaped, a trailing dot is added when
absent, and the resulting pattern matches descendants below that dot. The
bare package name itself is not a descendant match. A value ending in a dot
is not given a second dot.

This is a mapping helper, so its ordering and state behavior are the same as
`includePattern`. The value is compiled as a generated Java regular
expression. Null or otherwise unusable input may raise the normal Java
runtime exception.

Ordinary example:

```java
FilterBuilder project = new FilterBuilder()
    .includePackage("org.example");
boolean accepted = project.test("org.example.Service"); // true
```

Edge example:

```java
FilterBuilder packageOnly = new FilterBuilder()
    .includePackage("org.example");
boolean accepted = packageOnly.test("org.example"); // false
```

### `excludePackage(String)`

Signature: `public FilterBuilder excludePackage(String value)`.

Append the exclusion equivalent of `includePackage`. The package prefix is
literal, is converted to a descendant pattern with an escaped dot and a
trailing `.*`, and the same builder is returned. It rejects matching
descendants while preserving the ordered-chain rules of `excludePattern`.

Ordinary example:

```java
FilterBuilder visible = new FilterBuilder()
    .includePackage("org.example")
    .excludePackage("org.example.internal");
boolean accepted = visible.test("org.example.internal.Hidden"); // false
```

Edge example:

```java
FilterBuilder literal = new FilterBuilder()
    .includePackage("a$b");
boolean accepted = literal.test("a$b.Type"); // true; `$` is literal
```

### Deprecated `include(String)` and `exclude(String)`

Signatures: `@Deprecated public FilterBuilder include(String regex)` and
`@Deprecated public FilterBuilder exclude(String regex)`.

These legacy fluent methods append the same regular-expression include or
exclude predicates as their pattern-named counterparts and return the same
builder. New code should use `includePattern` and `excludePattern`, but the
legacy methods must retain the same complete-string matching, ordering,
invalid-pattern behavior, and side-effect constraints.

Ordinary example:

```java
FilterBuilder legacy = new FilterBuilder()
    .include("org\\.example\\..*")
    .exclude("org\\.example\\.internal\\..*");
boolean accepted = legacy.test("org.example.Service"); // true
```

Edge example:

```java
FilterBuilder legacy = new FilterBuilder().include("x+");
boolean accepted = legacy.test("x+"); // false; the regex is not a literal
```

### `parsePackages(String)`

Signature: `public static FilterBuilder parsePackages(String includeExcludeString)`.

Parse a comma-separated package-filter string and return a new builder. Split
on commas, trim each item, inspect its first character, and append a package
include for `+` or a package exclude for `-`. The remainder of each item uses
the same literal prefix mapping as the package helper methods. Items are
processed left to right, so the resulting chain is deterministic and order
dependent.

An item with a prefix other than `+` or `-` throws
`org.reflections.ReflectionsException`. Empty input items, an empty overall
input, null input, or malformed values may produce the normal Java runtime
failure from splitting, indexing, or pattern construction; they must not be
silently converted into an unrelated valid filter.

Ordinary example:

```java
FilterBuilder parsed = FilterBuilder.parsePackages("+java, -java.lang");
boolean list = parsed.test("java.util.List"); // true
boolean string = parsed.test("java.lang.String"); // false
```

Edge example:

```java
try {
    FilterBuilder.parsePackages("java.util");
    throw new AssertionError("invalid prefix was accepted");
} catch (org.reflections.ReflectionsException expected) {
    // The item must begin with '+' or '-'.
}
```

### `add(Predicate<String>)`

Signature: `public FilterBuilder add(java.util.function.Predicate<String> filter)`.

The source class exposes this fluent method for appending a caller-provided
predicate and returning the same builder. It is a generic extension point,
not a required scanner or serialization feature. Preserve insertion order and
do not add global state. The bounded contract is primarily exercised through
the regex and package methods above; arbitrary predicates may have caller
defined side effects and are not confidently bindable beyond this append-and-
return shape.

### `test(String)`

Signature: `public boolean test(String value)` from
`java.util.function.Predicate<String>`.

Evaluate the chain in insertion order and return the final acceptance state.
An empty chain starts accepted. A chain whose first predicate is an exclusion
also starts accepted; a chain whose first predicate is an inclusion starts
rejected. If the current state is accepted, an include is skipped because it
cannot change that state. If the current state is rejected, an exclude is
skipped for the same reason. A matching exclusion that changes accepted to
rejected ends evaluation. Later include operations can recover from a
rejected state when the preceding exclusion did not terminate evaluation.

The result is a boolean and the call does not mutate the builder. Matching is
complete-string matching for regex predicates. Null input may follow normal
Java runtime behavior from the underlying matcher.

Ordinary example:

```java
FilterBuilder filter = new FilterBuilder()
    .includePackage("org.reflections")
    .excludePackage("org.reflections.internal");
boolean publicType = filter.test("org.reflections.Api"); // true
boolean internalType = filter.test("org.reflections.internal.Impl"); // false
```

Edge example:

```java
FilterBuilder exclusionFirst = new FilterBuilder()
    .excludePackage("org.secret");
boolean unrelated = exclusionFirst.test("org.example.Api"); // true
```

### `org.reflections.ReflectionsException`

Import path: `org.reflections.ReflectionsException`.

This public class extends `java.lang.RuntimeException` and provides these
constructors:

```java
public ReflectionsException(String message)
public ReflectionsException(String message, Throwable cause)
public ReflectionsException(Throwable cause)
```

The constructors preserve the normal RuntimeException message and cause
semantics. The parser uses this exception for an unsupported package-item
prefix. The class does not perform I/O or carry global state.

Ordinary example:

```java
RuntimeException error = new ReflectionsException("bad filter");
```

Edge example:

```java
Throwable cause = new IllegalArgumentException("bad prefix");
ReflectionsException error = new ReflectionsException("invalid", cause);
// error.getCause() is the supplied cause.
```

### Object methods and representation

`FilterBuilder` also exposes the normal public `equals(Object)`,
`hashCode()`, and `toString()` overrides. Equality and hashing reflect the
ordered predicate chain, and the string form represents that chain. These
methods must be deterministic and must not perform I/O. They are secondary
to the filtering contract; do not add serialization or scanner state.

## Implementation Notes

Use exact package declarations and keep the two required source files in the
directory layout above. A Maven project with an empty dependency closure is
enough. Compile with the standard JDK and avoid third-party libraries,
reflection-based shortcuts, filesystem access, environment inspection, time,
randomness, threads, and network access.

Preserve the ordered nature of the builder. Do not sort, deduplicate, or
replace predicates merely because they have equal textual patterns. Compile
regular expressions using Java's standard regex behavior, and ensure package
mapping escapes literal dots and dollar signs before adding the descendant
suffix. The bare package prefix must remain distinct from a descendant name.

Keep `parsePackages` consistent with the direct package helpers. Trimming is
performed per comma-separated item; the first non-trimmed character selects
the operation. Unsupported operation markers are errors, not includes.

The implementation should be isolated and repeatable. For the same builder
call sequence and string, repeated `test` calls return the same result. One
builder's chain must not affect another builder's chain. Do not write files,
open URLs, inspect a classpath, or depend on scanner classes from the upstream
repository.

Small verifiable examples:

1. `new FilterBuilder().test("")` returns `true` because the chain is empty.
2. `new FilterBuilder().includePackage("a.b").test("a.b.Type")` returns
   `true`, while testing `"a.b"` returns `false`.
3. An include for `org.example..*` followed by an exclude for
   `org.example.internal..*` rejects a matching internal name.
4. `parsePackages("+java, -java.lang")` accepts `java.util.List` and rejects
   `java.lang.String`.

These examples describe observable behavior only. Do not copy upstream source
or tests, do not expose verifier or grading details, and do not implement
unscored Reflections subsystems as a substitute for the required API.
