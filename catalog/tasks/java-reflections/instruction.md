# Introduction and Goals of the Reflections Project

Reflections is a Java runtime metadata library. This task isolates its local,
deterministic `FilterBuilder` utility. Recreate the bounded filtering API as a
single-module Maven project. Classpath scanning, metadata indexing, serializers,
and every external Reflections dependency are outside this task.

## Natural Language Instruction (Prompt)

Create a Java Maven project that provides
`org.reflections.util.FilterBuilder` and
`org.reflections.ReflectionsException`. Implement the public filtering methods
listed below. The builder is a stateful `Predicate<String>`: each include or
exclude operation appends a predicate to its chain, and `test` evaluates that
chain deterministically. Keep source code under `src/main/java` and use only
the Java standard library.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11 (offline metadata validation)
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. Do not add dependencies, plugins,
profiles, repositories, modules, extensions, or custom test commands. The
trusted verifier owns compilation, collection, reports, and grading.

## Reflections Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/
    └── org/reflections/
        ├── ReflectionsException.java
        └── util/FilterBuilder.java
```

The exact public types are `org.reflections.ReflectionsException` and
`org.reflections.util.FilterBuilder`. The bounded task needs no classpath
scanner, URL handling, filesystem traversal, reflection lookup, or external
Maven artifact.

## API Usage Guide

### Core APIs

`FilterBuilder` implements `java.util.function.Predicate<String>` and exposes
these public methods:

```java
public FilterBuilder()
public FilterBuilder includePackage(String value)
public FilterBuilder excludePackage(String value)
public FilterBuilder includePattern(String regex)
public FilterBuilder excludePattern(String regex)
@Deprecated public FilterBuilder include(String regex)
@Deprecated public FilterBuilder exclude(String regex)
public static FilterBuilder parsePackages(String includeExcludeString)
public boolean test(String value)
```

`includePattern` appends a predicate that accepts only complete-string matches
of its Java regular expression. `excludePattern` appends a predicate that
rejects complete-string matches. Both return the same builder instance.
`include` and `exclude` have exactly the same behavior as their pattern-named
counterparts.

`includePackage("a.b")` is equivalent to including the complete-match regex
for names beginning with `a.b.`. `excludePackage` has the corresponding
exclusion behavior. The supplied package text is treated as literal package
text: dots and dollar signs are escaped before the trailing `.*` is added.
Neither package helper matches the bare package name without its trailing dot.

```java
FilterBuilder filter = new FilterBuilder()
    .includePackage("org.example")
    .excludePackage("org.example.internal");
filter.test("org.example.Service");          // true
filter.test("org.example.internal.Hidden");  // false
filter.test("org.example");                  // false
```

`parsePackages` accepts a comma-separated list of package prefixes. Each
trimmed item must begin with `+` for include or `-` for exclude, followed by
the package prefix. It applies entries left to right using the same package
mapping as the helper methods.

```java
FilterBuilder filter = FilterBuilder.parsePackages("+java, -java.lang");
filter.test("java.util.List");   // true
filter.test("java.lang.String"); // false
```

`test` is deterministic. An empty chain accepts every input. A chain whose
first predicate is an exclusion also begins accepted; otherwise it begins
rejected. While evaluating in insertion order, an include is skipped when the
current result is already accepted, and an exclude is skipped when it is
already rejected. The first matching exclusion that changes an accepted result
to rejected ends evaluation. This makes exclusion override a previously
accepted matching include, while a later include can recover from a rejected
nonmatching exclusion.

`ReflectionsException` extends `RuntimeException` and provides these public
constructors:

```java
public ReflectionsException(String message)
public ReflectionsException(String message, Throwable cause)
public ReflectionsException(Throwable cause)
```

### Actual Usage Modes

Use a builder to retain or reject fully-qualified names before an external
scanner consumes them. This task only covers local predicate construction and
evaluation. It does not discover classes, load classes, open jars, inspect
annotations, or scan packages.

### Supported Function Types

The supported functions are regex predicate creation, literal package-prefix
mapping, ordered include/exclude chaining, and comma-separated package filter
parsing. Generic `add(Predicate<String>)`, equality/hash representation,
serialization, and every scanner/configuration API are outside this bounded
contract.

### Error Handling

Null inputs may fail with normal Java runtime exceptions. Invalid regular
expressions must surface the normal `Pattern` runtime failure. A
`parsePackages` item not beginning with `+` or `-` must throw
`ReflectionsException`. Empty or malformed parsed entries may fail with a
normal runtime exception rather than being silently accepted. No method may
perform I/O, access the network, or depend on classpath scanning.

## Detailed Implementation Nodes of Functions

### Node 1: Regex predicate behavior

Use Java regular-expression whole-string matching for include and exclude
predicates. Preserve Java's invalid-regex failure behavior.

### Node 2: Package-prefix mapping

Ensure package helpers add a trailing dot when absent, escape literal dots and
dollar signs, then match all names below that package prefix. The bare package
name is not a descendant name.

### Node 3: Ordered chain state

Maintain predicate insertion order. Empty and exclusion-first chains begin in
the accepted state; inclusion-first chains begin rejected. Apply the documented
skip and exclusion behavior without reordering predicates.

### Node 4: Parsed package entries

Split on commas, trim each entry, interpret `+` and `-`, and use the same
prefix transformation as direct package helpers. Reject unsupported prefixes
with `ReflectionsException`.

### Node 5: Fluent mutation

All include/exclude methods mutate only their receiver's ordered chain and
return that same `FilterBuilder`. No global state is involved.

### Node 6: Determinism and isolation

For the same sequence of builder calls and input string, `test` always returns
the same result. The bounded API has no filesystem, reflection, classpath,
thread, time, or network side effects.

### Node 7: Source and package layout

Use the exact `org.reflections` and `org.reflections.util` packages and compile
with `javac --release 21` using the standard Maven directory layout.

### Node 8: Offline build behavior

Keep the Maven dependency closure empty and download nothing at run time. The
trusted verifier invokes candidate code through a separate JSON/JVM process;
it does not import candidate classes into the verifier JVM.
