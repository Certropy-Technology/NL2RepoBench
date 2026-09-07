## Project Description

Build a small Java Maven project that recreates the bounded annotation metadata
surface of Jackson Annotations needed by this task. The project is a library,
not a JSON parser or a data-binding implementation. Its observable behavior is
the declaration metadata that Java reflection exposes for two annotation types
and one nested enum.

The target users are Java code that declares creator metadata and tooling that
reads that metadata through the standard reflection API. A consumer must be
able to compile source using the package `com.fasterxml.jackson.annotation`,
inspect retention and target metadata, read the creator mode, and use the four
creator-mode enum constants.

The bounded public surface is:

* `com.fasterxml.jackson.annotation.JacksonAnnotation`;
* `com.fasterxml.jackson.annotation.JsonCreator`;
* `com.fasterxml.jackson.annotation.JsonCreator.Mode`; and
* the `mode()` member, enum constants, and standard enum lookup operations
  described in the API Usage Guide.

Do not implement JSON parsing, JSON generation, object mapping, creator
selection, parameter-name discovery, annotation scanning frameworks, mix-ins,
serialization, deserialization, or any other Jackson module. A declaration of
an annotation is the required behavior; the annotation does not invoke a
constructor or perform an operation when it is read.

### Natural Language Instruction

Create a single-module Java project rooted at `workspace/`. Put production
source below `src/main/java/com/fasterxml/jackson/annotation/` and provide a
minimal `pom.xml` that identifies the project as a Maven artifact without
adding runtime dependencies. Implement the following capabilities:

1. Declare `JacksonAnnotation` as a public marker annotation in the exact
   package and with the exact runtime retention and annotation-type target
   described below.
2. Declare `JsonCreator` as a public annotation in the exact package, mark it
   with `JacksonAnnotation`, and expose its single `mode()` member with the
   exact default and return type described below.
3. Declare the nested public enum `JsonCreator.Mode` with exactly the constants
   `DEFAULT`, `DELEGATING`, `PROPERTIES`, and `DISABLED`, in that order.
4. Preserve normal Java annotation and enum reflection behavior, including
   annotation defaults, target validation by the compiler, enum ordering, and
   `valueOf` exception behavior.

Use the package names and declarations exactly as specified. Do not rename the
types, add aliases, add custom constructors, or replace the enum with strings.
The two annotation declarations must not depend on external libraries. Keep
all observable behavior deterministic and free of I/O, environment reads,
time, random numbers, processes, and network access.

## Supports

### Runtime and Build Boundary

The target runtime is Temurin JDK 21.0.12+8 on Linux amd64 with glibc. Use
Maven 3.9.11 for project metadata and offline validation. The project must
compile with Java release 21 and must not require a runtime artifact other than
the JDK.

The candidate project is expected to build in a no-network environment. The
agent, candidate build, tests, reflection probes, and any supporting scripts
must not contact GitHub, Maven Central, DNS, or another external service.
Do not download dependencies during a build or at runtime. The dependency
closure for the two source files is empty: `java.lang` and
`java.lang.annotation` are JDK packages, not Maven dependencies.

### Maven Project Contract

Create a single Maven project with a normal `pom.xml`. It may declare the
project coordinates and Java 21 compiler settings needed to compile the source.
It must not add application plugins, repositories, profiles, modules,
extensions, or third-party runtime dependencies. Do not copy the upstream
Jackson parent POM or introduce a dependency on a published Jackson artifact.

The source tree must compile with a command equivalent to:

```text
mvn --offline validate
mvn --offline -DskipTests package
```

The project has no command-line interface, executable main class, service, or
configuration file. Users consume the annotations from Java source imports.

### Project Directory Structure

Use `workspace/` as the project root and keep the public structure aligned
with the package names in the API Usage Guide:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/
                └── fasterxml/
                    └── jackson/
                        └── annotation/
                            ├── JacksonAnnotation.java
                            └── JsonCreator.java
```

`JacksonAnnotation.java` contains the marker annotation. `JsonCreator.java`
contains the creator annotation and its nested `Mode` enum. There is no
required resource directory, executable script, CLI entry point, database, or
network configuration. Additional tests may exist locally, but they are not a
public library entry point and must not change the production package layout.

### Supported Function Types

This task supports Java annotation declarations and standard reflection:

* runtime-visible `@Retention` metadata;
* `@Target` metadata for legal annotation locations;
* the `@JacksonAnnotation` marker on `JsonCreator`;
* the `mode()` annotation member and its default value;
* explicit creator-mode values; and
* deterministic enum constants, `values()`, and `valueOf(String)` behavior.

There is no supported file format, serialization format, mutable database,
threaded operation, callback, subprocess, shell integration, or network API.

## API Usage Guide

All types below use the exact package `com.fasterxml.jackson.annotation`.
Signatures are Java signatures, not pseudocode. The implementation must keep
the public surface no broader than the declarations documented here.

### `com.fasterxml.jackson.annotation.JacksonAnnotation`

#### Public annotation declaration

```java
package com.fasterxml.jackson.annotation;

public @interface JacksonAnnotation {
}
```

This is a public marker annotation with no members. It has no constructor, no
mutable state, no parameters, and no return value. Applying it to an annotation
type marks that annotation as part of the Jackson annotation family; it does
not cause the marked annotation to be discovered or executed.

The declaration must have these Java meta-annotations:

* `@Retention(RetentionPolicy.RUNTIME)`, so reflection can read the marker;
* `@Target(ElementType.ANNOTATION_TYPE)`, so it can annotate annotation types
  and cannot be applied directly to an ordinary class, method, field, or
  constructor; and
* no annotation members beyond the empty marker declaration.

Normal example:

```java
@JacksonAnnotation
public @interface CustomCreatorMetadata {
}
```

Reflection can then observe the marker on `CustomCreatorMetadata`. The
annotation itself does not return an object from user code and does not perform
I/O.

Edge example:

```java
// This must be rejected by Java compilation because the target is not a type
// declaration for an annotation.
// @JacksonAnnotation
// final class NotAnAnnotation { }
```

Do not broaden the target merely to make this example compile. The target set
is part of the public contract.

### `com.fasterxml.jackson.annotation.JsonCreator`

#### Public annotation declaration

```java
package com.fasterxml.jackson.annotation;

@JacksonAnnotation
public @interface JsonCreator {
    public Mode mode() default Mode.DEFAULT;
}
```

`JsonCreator` is a public annotation type. It must have runtime retention and
exactly these targets: `ElementType.ANNOTATION_TYPE`, `ElementType.METHOD`,
and `ElementType.CONSTRUCTOR`. It must itself be annotated with
`@JacksonAnnotation`. It has one public annotation member, `mode()`, and no
other members or mutable state.

The annotation is metadata only. It does not call the annotated constructor or
factory method, inspect JSON, select a creator, bind properties, or change the
annotated class. A consumer can read the metadata later through Java
reflection.

Normal constructor example:

```java
import com.fasterxml.jackson.annotation.JsonCreator;

final class UserId {
    private final String value;

    @JsonCreator(mode = JsonCreator.Mode.DELEGATING)
    UserId(String value) {
        this.value = value;
    }
}
```

The declaration above stores `DELEGATING` as annotation metadata. It does not
make the constructor callable from outside its normal Java access rules.

Normal factory-method example:

```java
final class Point {
    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    public static Point create(int x, int y) {
        return new Point(x, y);
    }
}
```

The annotation remains a declaration on the method. The implementation does
not need to implement `Point`, factory invocation, or property binding.

Edge example:

```java
// This target is invalid because fields are not in JsonCreator's target set.
// @JsonCreator
// private String value;
```

The compiler must reject an invalid target instead of the implementation
silently accepting it. Do not add `FIELD`, `PARAMETER`, or `TYPE` to the target
set.

### `JsonCreator.mode()`

#### Public annotation member

The exact public member signature is:

```java
public abstract com.fasterxml.jackson.annotation.JsonCreator.Mode mode();
```

The source declaration uses the equivalent nested-type shorthand:

```java
public Mode mode() default Mode.DEFAULT;
```

The input domain is an enum constant of `JsonCreator.Mode`, supplied in an
annotation use. The member accepts no string, integer, null, or arbitrary
object. Its return type is exactly `JsonCreator.Mode`.

When an annotation use omits `mode`, reflection must report the default
`JsonCreator.Mode.DEFAULT`:

```java
@JsonCreator
public UserId(String value) { }

JsonCreator creator = UserId.class
    .getDeclaredConstructor(String.class)
    .getAnnotation(JsonCreator.class);
JsonCreator.Mode mode = creator.mode();
// mode is JsonCreator.Mode.DEFAULT
```

When a use supplies a constant, reflection must return that exact constant:

```java
@JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
public Point(int x, int y) { }

// Point's reflected annotation reports Mode.PROPERTIES.
```

The member has no side effects. Repeated reads of the same annotation instance
return the same logical enum value. It must not consult environment state,
perform conversion, or fall back from an invalid value.

### `com.fasterxml.jackson.annotation.JsonCreator.Mode`

#### Public nested enum declaration

```java
public enum JsonCreator.Mode {
    DEFAULT,
    DELEGATING,
    PROPERTIES,
    DISABLED
}
```

The nested enum is public and is a member of `JsonCreator`. Its constants must
be declared in exactly this order and must not have fields, aliases, or custom
behavior added by the task. The four constants mean:

* `DEFAULT`: leave creator-mode choice to the consumer's normal heuristics;
* `DELEGATING`: describe a single delegated creator input;
* `PROPERTIES`: describe creator arguments matched from named properties; and
* `DISABLED`: represent explicit disabling of a creator declaration.

These meanings are metadata documentation only. This task does not implement
the consumer that applies the mode.

Normal example:

```java
JsonCreator.Mode selected = JsonCreator.Mode.PROPERTIES;
assert selected.name().equals("PROPERTIES");
```

Edge example:

```java
// No fifth mode may be accepted or synthesized.
JsonCreator.Mode[] modes = JsonCreator.Mode.values();
assert modes.length == 4;
```

### `JsonCreator.Mode.values()`

#### Public generated enum method

The Java compiler supplies this public static method:

```java
public static JsonCreator.Mode[] values();
```

It takes no parameters and returns a new array containing the four constants in
declaration order: `DEFAULT`, `DELEGATING`, `PROPERTIES`, `DISABLED`. The array
has length four. The ordering is deterministic and must not depend on locale,
time, process state, or input data.

Normal example:

```java
JsonCreator.Mode[] modes = JsonCreator.Mode.values();
String first = modes[0].name();
String last = modes[3].name();
// first is "DEFAULT" and last is "DISABLED"
```

Edge example:

```java
JsonCreator.Mode[] first = JsonCreator.Mode.values();
first[0] = JsonCreator.Mode.DISABLED;
JsonCreator.Mode[] second = JsonCreator.Mode.values();
// second[0] is still DEFAULT; callers receive an independent enum array.
```

Do not return a mutable shared array or reorder the constants.

### `JsonCreator.Mode.valueOf(String)`

#### Public generated enum method

The Java compiler supplies this public static method:

```java
public static JsonCreator.Mode valueOf(String name);
```

The accepted input is one exact enum name: `DEFAULT`, `DELEGATING`,
`PROPERTIES`, or `DISABLED`. The return type is `JsonCreator.Mode`, and the
result is the matching singleton enum constant. Matching is case-sensitive and
does not trim whitespace or accept aliases.

Normal example:

```java
JsonCreator.Mode mode = JsonCreator.Mode.valueOf("DELEGATING");
assert mode == JsonCreator.Mode.DELEGATING;
```

Invalid-name example:

```java
try {
    JsonCreator.Mode.valueOf("delegating");
    throw new AssertionError("an unknown exact name must fail");
} catch (IllegalArgumentException expected) {
    // Normal Java enum behavior.
}
```

For an unknown non-null name, Java enum behavior throws unchecked
`IllegalArgumentException`. For `null`, normal Java enum behavior throws
unchecked `NullPointerException`. Do not return `DEFAULT`, create a new enum
value, normalize case, or convert a null input.

### Standard reflection boundary

The standard JDK reflection API is the observation mechanism, not an additional
library API to implement. In particular, callers may use
`Class.getAnnotation(JsonCreator.class)`,
`Constructor.getAnnotation(JsonCreator.class)`, and
`Method.getAnnotation(JsonCreator.class)` to read a runtime-retained use.
`JsonCreator.class.getAnnotation(JacksonAnnotation.class)` must observe the
marker. The implementation must preserve the ordinary annotation contracts for
`annotationType()`, `equals(Object)`, `hashCode()`, and `toString()` on
reflection-created annotation instances; do not write replacement wrappers.

## Implementation Notes

### Source and package constraints

Keep exactly the two production source files shown in the directory tree. Use
the package declaration `com.fasterxml.jackson.annotation` in both files.
`JsonCreator.Mode` must be nested inside `JsonCreator`, not moved to a separate
top-level enum. `JacksonAnnotation` must remain a marker with zero members.

Use only the JDK annotation types `ElementType`, `Retention`,
`RetentionPolicy`, and `Target` for declaration metadata. Do not add a Maven
dependency, import a published Jackson JAR, or copy unrelated Jackson classes.

### Metadata and determinism

The following facts are observable and must remain exact:

1. `JacksonAnnotation` has runtime retention and annotation-type-only target.
2. `JsonCreator` has runtime retention and targets annotation types, methods,
   and constructors only.
3. `JsonCreator` is marked with `JacksonAnnotation`.
4. `JsonCreator.mode()` returns `JsonCreator.Mode` and defaults to `DEFAULT`.
5. The enum order is `DEFAULT`, `DELEGATING`, `PROPERTIES`, `DISABLED`.
6. Java's generated enum lookup methods keep their standard signatures and
   exception behavior.

All of these results must be deterministic across repeated JVM processes. No
method or declaration may read a file, access the network, launch a process,
inspect an environment variable, use a clock, or use randomness.

### Small verifiable examples

The implementation should make these independent checks possible:

```java
assert JsonCreator.Mode.values().length == 4;
assert JsonCreator.Mode.values()[1] == JsonCreator.Mode.DELEGATING;
```

```java
assert JsonCreator.Mode.valueOf("DISABLED") == JsonCreator.Mode.DISABLED;
```

```java
assert JsonCreator.class.getAnnotation(JacksonAnnotation.class) != null;
```

```java
assert JsonCreator.class.getDeclaredMethod("mode").getDefaultValue()
    == JsonCreator.Mode.DEFAULT;
```

The examples are behavior checks, not a request to add an application entry
point or assertion framework to the project.

### Error and boundary handling

Let Java enforce annotation target errors during compilation. Let the Java
compiler generate ordinary enum methods and preserve their standard unchecked
exceptions. Do not catch and rewrite `IllegalArgumentException` or
`NullPointerException`, and do not silently accept malformed annotation uses.

An annotation declaration with an omitted member must use the declared default;
an explicit member must retain the selected enum constant. Empty source files,
extra enum constants, changed capitalization, changed target sets, source-only
retention, and a top-level replacement for the nested enum are all outside the
contract.

### Cross-module scope

No other module is required to consume these declarations. Do not implement
`JsonProperty`, `JsonValue`, creator invocation, property binding, or a Jackson
databind integration merely because the Javadoc describes how a larger Jackson
system may use `JsonCreator`. The task ends at the reflection-visible metadata
boundary documented here.

Before finalizing, confirm the package paths, exact public declarations, Java
21 compilation, offline Maven behavior, enum order, annotation retention, and
target sets. Keep the project small, source-discoverable, and free of runtime
network assumptions.
