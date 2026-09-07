## Project Description

Joda-Convert is a small Java library for marking conversion entry points with
annotations. This task covers the public annotation API only. The result is a
minimal Maven project that lets other Java code identify text-to-object and
object-to-text methods through Java reflection.

The target users are Java developers who need stable marker annotations for a
conversion layer. A caller may inspect annotation metadata at runtime without
depending on a conversion manager or on a third-party library.

The implementation boundary is deliberately narrow. Implement the two public
annotation types in the `org.joda.convert` package:

- `org.joda.convert.FromString`
- `org.joda.convert.ToString`

`FromString` marks a constructor or method that can be used by a conversion
layer to create a value from text. The annotation does not call the constructor
or method and does not inspect its parameter list.

`ToString` marks a method that can be used by a conversion layer to obtain text
from an object. The annotation does not call the method and does not alter the
object or the returned text.

The public contract is annotation declaration metadata: package name, type
name, target set, retention policy, and the absence of annotation elements.
The exact metadata must be observable through `java.lang.annotation` and normal
reflection on Java 21.

Do not implement a conversion manager, registry, reflection scanner, parser,
formatter, command-line application, shell integration, or service provider.
Do not add public annotation types that are not listed in this specification.

### Natural Language Instruction

Create an installable Java Maven project under the empty `workspace/` directory.
Place the two annotation source files under
`src/main/java/org/joda/convert/`, preserving their complete package names.

Implement `FromString` as a public annotation with runtime retention and
exactly the `METHOD` and `CONSTRUCTOR` targets.

Implement `ToString` as a public annotation with runtime retention and exactly
the `METHOD` target.

Neither annotation may declare annotation elements, defaults, parameters, or
methods. The annotation declarations must therefore be usable as `@FromString`
and `@ToString` with no arguments.

Keep the project dependency-free. The Java standard library is sufficient, and
no external dependency may be needed to compile or inspect these annotations.

Provide a minimal `pom.xml` at the workspace root so Maven recognizes the
project. The POM is build metadata, not a second API surface. It must not add
repositories, modules, plugins, profiles, extensions, or runtime dependencies.

There is no CLI or executable entry point for this task. Do not invent a main
class or document a command beyond the declared Maven validation command.

The implementation must work in the fixed offline environment described in the
Supports section. Candidate source is compiled and inspected independently from
the trusted test harness.

## Supports

### Runtime and Build Environment

Use Temurin JDK `21.0.12+8` on Linux amd64 with glibc. Use Apache Maven
`3.9.11` as the package manager and build tool.

The project should be valid for the Java 21 language and class-file level. The
annotation declarations should compile with `javac --release 21`.

The expected project metadata is:

```text
groupId: org.joda
artifactId: joda-convert
version: 3.0.2
source root: src/main/java
package root: org.joda.convert
runtime dependencies: none
```

The version and coordinates describe the task's Maven metadata. They do not
authorize adding the full upstream project or implementing APIs outside the
bounded annotation slice.

### Installation and Validation

From the project root, the public build command is:

```text
mvn --offline validate
```

The project must also compile when its Java sources are passed to `javac` with
`--release 21`. Do not require a network request, an installed global Maven
plugin, or a non-standard local tool.

There is no task-specific CLI. There are no flags, stdin records, stdout data
formats, environment variables, configuration files, or filesystem databases
to implement.

### Dependencies and Network Boundary

The implementation uses only Java language and JDK annotation APIs. Do not add
third-party Maven dependencies, transitive dependencies, test frameworks, or
runtime services.

Agent, candidate, verifier, Oracle, and control execution all run with network
access disabled. They must not access GitHub, Maven Central, a Maven mirror,
PyPI, npm, a Go proxy, DNS, or another external service at runtime.

Maven must use its already available offline environment. Do not use a build
script to download artifacts, resolve floating versions, run a remote command,
or contact an update checker.

### Project Directory Structure

Create this project structure. Paths and package declarations must agree:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── joda/
                    └── convert/
                        ├── FromString.java
                        └── ToString.java
```

`pom.xml` is the only required project-level metadata file. Do not require a
custom resource directory because the two annotations have no resources.

Do not add `module-info.java`, a conversion manager, a CLI source tree, a
reflection utility, or an unrelated package. Extra public APIs make the task
ambiguous and are outside the requested contract.

## API Usage Guide

The public API consists of two annotation types. They are imported from the
exact package paths below. Both types have an empty annotation body and no
annotation elements, so their usage never takes a value or named argument.

### `org.joda.convert.FromString`

#### Import path and declaration

Use this fully qualified type:

```java
import org.joda.convert.FromString;
```

Its declaration contract is:

```java
@java.lang.annotation.Target({
    java.lang.annotation.ElementType.METHOD,
    java.lang.annotation.ElementType.CONSTRUCTOR
})
@java.lang.annotation.Retention(
    java.lang.annotation.RetentionPolicy.RUNTIME
)
public @interface FromString { }
```

The public type is an annotation interface, not a class, enum, or ordinary
interface. Its fully qualified binary name is `org.joda.convert.FromString`.

#### Accepted declaration elements

The allowed input domain is a Java method declaration or a Java constructor
declaration. `@FromString` may appear on either declaration kind.

The target set must contain exactly `ElementType.METHOD` and
`ElementType.CONSTRUCTOR`. Do not include `TYPE`, `FIELD`, `PARAMETER`,
`PACKAGE`, `MODULE`, `ANNOTATION_TYPE`, `LOCAL_VARIABLE`, or a type-use target.

The annotation does not require the method to be static, to accept one
`String`, or to return a particular type. Those are conventions for a caller's
conversion layer, not validation performed by this marker annotation.

#### Runtime behavior and metadata

The retention policy is exactly `RetentionPolicy.RUNTIME`. A caller can inspect
the annotation after compilation through `AnnotatedElement` methods such as
`Method.isAnnotationPresent(FromString.class)` or
`Constructor.isAnnotationPresent(FromString.class)`.

The annotation has no elements. `FromString.class.getDeclaredMethods()` must
therefore have an empty result, and the annotation cannot accept named values.

The annotation declaration has no state, I/O, global mutation, ordering, or
network side effect. Applying it only contributes class-file metadata.

#### Normal example

This constructor usage is valid and can be observed through reflection:

```java
final class Port {
    private final int value;

    @FromString
    Port(String text) {
        this.value = Integer.parseInt(text);
    }
}
```

The annotation marks the constructor; it does not perform `parseInt` and does
not create a `Port` instance by itself.

#### Edge and invalid examples

This static factory usage is also valid because a method is an allowed target:

```java
final class UserId {
    @FromString
    static UserId parse(String text) {
        return new UserId(text);
    }

    private UserId(String text) { }
}
```

Applying `@FromString` to a class, field, parameter, or package is outside the
target set and must be rejected by the Java compiler. Do not broaden the target
set merely to make such source compile.

### `org.joda.convert.ToString`

#### Import path and declaration

Use this fully qualified type:

```java
import org.joda.convert.ToString;
```

Its declaration contract is:

```java
@java.lang.annotation.Target(java.lang.annotation.ElementType.METHOD)
@java.lang.annotation.Retention(
    java.lang.annotation.RetentionPolicy.RUNTIME
)
public @interface ToString { }
```

The public type is an annotation interface with binary name
`org.joda.convert.ToString`. It is distinct from `java.lang.Override` and from
any ordinary `toString()` implementation.

#### Accepted declaration elements

The allowed input domain is exactly a Java method declaration. The target set
must contain only `ElementType.METHOD`.

The annotation does not enforce that the method is an instance method, has no
parameters, or returns `String`. Those method-shape conventions belong to the
consumer of the metadata. The annotation itself only declares a marker.

Do not add constructor, type, field, parameter, package, module, or type-use
targets. A constructor annotated with `@ToString` must fail compilation because
constructors are not methods for this target contract.

#### Runtime behavior and metadata

The retention policy is exactly `RetentionPolicy.RUNTIME`. Runtime reflection
must be able to observe `@ToString` on an annotated `Method`.

The annotation has no elements. `ToString.class.getDeclaredMethods()` must be
empty, and `@ToString` must not require or accept an argument.

The annotation performs no invocation, conversion, formatting, mutation, I/O,
or external communication. Repeated reflective reads return the same metadata
contract and do not change application state.

#### Normal example

This method usage is valid:

```java
final class Label {
    @ToString
    public String text() {
        return "ready";
    }
}
```

A conversion layer may discover the marker and choose to invoke `text()`, but
that invocation is outside this annotation implementation.

#### Edge and invalid examples

An overloaded class may mark one method while leaving another unmarked:

```java
final class Token {
    @ToString
    public String asText() { return "token"; }

    public String debugText(String prefix) { return prefix + "token"; }
}
```

The unmarked method must not acquire `ToString` implicitly. Applying
`@ToString` to a field or constructor is invalid because only `METHOD` is
permitted.

### Reflection and annotation-type contract

Both annotations must remain independently discoverable by reflection. A
method carrying `@FromString` must not thereby appear to carry `@ToString`, and
an unannotated member must not report either marker.

The standard reflection APIs expose the metadata through `Class`,
`Method`, `Constructor`, and `java.lang.annotation.Annotation`. Preserve the
annotation names and package exactly so callers can load the class literals.

The order of the `@Target` and `@Retention` meta-annotations in source is not
observable API behavior, but their values are. Do not add `@Inherited`,
`@Repeatable`, `@Documented`, or another meta-annotation unless the source
contract explicitly requires it; this task does not.

## Implementation Notes

### Cross-file and cross-module constraints

Keep `FromString.java` and `ToString.java` in the same package directory and
give each file one matching public top-level annotation declaration. A public
type whose file name or package differs from the contract will not be loadable
through the documented import path.

Use `java.lang.annotation.Target`, `ElementType`, `Retention`, and
`RetentionPolicy` from the JDK. Explicit imports or fully qualified names are
both acceptable, provided the resulting metadata is identical.

The POM and source files must agree on the project coordinates and source root.
The POM must remain minimal and offline-valid. No source code should depend on
Maven at runtime, and no annotation implementation should read POM metadata.

### Determinism and observable state

Compilation of the same two declarations must produce the same public type
names and annotation metadata. Do not derive targets or retention from system
properties, environment variables, locale, time, random values, or files.

Annotation lookup must be side-effect free. The declarations must not contain
static initialization, constructors, mutable fields, annotation elements,
logging, filesystem operations, or network calls.

The exact target set is part of the deterministic contract. `FromString` has two
targets; `ToString` has one. Runtime retention is part of the deterministic
contract for both types.

### Small verifiable examples

1. Compile a class with a `String` constructor marked `@FromString`; reflection
   reports `FromString` on that constructor.
2. Compile a class with a static method marked `@FromString`; reflection
   reports the marker on the method.
3. Compile a class with a no-argument method returning `String` marked
   `@ToString`; reflection reports `ToString` on that method.
4. Inspect `getDeclaredMethods()` on both annotation classes; each result is
   empty because neither annotation declares elements.

Also verify the metadata boundaries with compile-time probes: a field or class
cannot use either marker, a constructor cannot use `ToString`, and a method or
constructor can use `FromString`. These probes test declaration legality only;
they should not require a conversion manager.

### Error propagation and boundaries

The annotations themselves do not throw checked or unchecked exceptions during
normal declaration or reflective lookup. Invalid target placement is rejected
by Java compilation rather than by a custom runtime validator.

Do not catch or transform compiler errors in the annotation source. Do not add
runtime checks that inspect method signatures or throw custom exceptions for a
marker mismatch.

An empty project, a class with no annotated members, and a class with unrelated
annotations are valid inputs to reflection. They should simply report no
matching marker for members that were not annotated.

Unicode text in a consumer's `String` value is irrelevant to these annotations;
the markers neither parse nor normalize text. Similarly, overloaded methods,
private methods, static methods, and constructors are metadata consumers'
responsibility unless constrained by the target set itself.

### Scope and implementation discipline

Do not copy a conversion algorithm or upstream project implementation. The
required behavior is fully described by the two annotation declarations and
their metadata contract.

Do not expose private verifier details, hidden test identifiers, report paths,
artifact references, or grader protocols in the project. Implement only the
public package and files shown in the directory tree.

Before finishing, inspect the generated declarations with Java reflection and
confirm that both annotation classes load from `org.joda.convert`. Run Maven
offline and compile with the fixed Java release. Keep all execution offline and
leave no generated build output as part of the source contract.
