## Project Description

Create a small, single-module Java Maven project that recreates the bounded
public exception contract selected from Apache Commons Configuration.

The project is for callers that need to represent a configuration-loading or
configuration-parsing failure while retaining a human-readable message and an
underlying cause.  The public type is a checked exception in the package
`org.apache.commons.configuration2.ex`.

The implementation target is intentionally narrow.  It contains one public
class, `ConfigurationException`, and its six public constructor overloads.
The class must extend `java.lang.Exception` directly.  Standard inherited
methods such as `getMessage()`, `getCause()`, `toString()`, and
`printStackTrace()` must therefore observe the state established by the
constructors.

### Natural Language Instruction

Build the project from an empty `workspace/` directory and implement the
following capabilities:

1. Provide the exact public type
   `org.apache.commons.configuration2.ex.ConfigurationException`.
2. Provide the no-argument, direct-message, formatted-message,
   message-and-cause, cause-only, and cause-plus-formatted-message
   constructors described in the API guide.
3. Preserve a direct message exactly, including whitespace and punctuation.
4. Apply Java `String.format` semantics to both formatted-message overloads,
   preserving argument order and normal Java formatting failures.
5. Preserve the exact `Throwable` object supplied as a cause, so callers can
   verify identity with `getCause()`.
6. Keep the implementation under `src/main/java`, make it compile with Java
   21, and avoid runtime dependencies outside the Java standard library.

Do not add unrelated Commons Configuration modules, parsers, file readers,
network clients, command-line entry points, service providers, or additional
public APIs.  Do not copy an upstream implementation verbatim.  The candidate
`pom.xml` is project metadata only; it must not introduce candidate-controlled
plugins, repositories, modules, profiles, build extensions, or dependencies.

The public contract does not require a CLI.  A consumer uses the class by
importing it and constructing an exception, then catching it as a checked
`Exception` or as a `ConfigurationException`.

## Supports

### Runtime and Build Environment

Use the following fixed environment:

```text
Language: Java
JDK: Temurin 21.0.12+8
Compiler release: 21
Package manager: Maven 3.9.11
Platform: Linux amd64 with glibc
Runtime dependencies: none
Network during agent/candidate/verifier execution: unavailable
```

The task uses only `java.lang.Exception`, `java.lang.Throwable`, and
`java.lang.String` behavior supplied by the JDK.  There are no Maven runtime
packages to install.  Maven commands must be usable offline, and candidate
code must not contact GitHub, Maven Central, DNS, or any other external
service.  Do not download artifacts during compilation or execution.

### Project Directory Structure

Create this public project layout.  `workspace/` is the project root:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── configuration2/
                            └── ex/
                                └── ConfigurationException.java
```

The source file must declare package
`org.apache.commons.configuration2.ex`.  The POM must identify a normal
single-module Maven project and may contain ordinary project coordinates and
Java 21 metadata, but it must not be used to hide implementation code or to
add an external runtime dependency.  No test, resource, CLI, shell script, or
additional module is required by this bounded contract.

### Scope Boundary

The selected API inventory binds only these six constructor signatures on
`ConfigurationException`.  The upstream project contains many other classes,
but they are outside this task and are not confidently bindable as part of the
candidate contract.  Do not implement or document additional upstream APIs in
order to broaden the task.

## API Usage Guide

### Import Path

Import the one public type with its complete package name:

```java
import org.apache.commons.configuration2.ex.ConfigurationException;
```

All examples below assume this import.  Each constructor returns a new
`ConfigurationException` object.  Construction has no filesystem, process,
environment, network, clock, global-state, or other external side effect.
The inherited exception state is observable through standard `Throwable`
methods.

### `ConfigurationException()`

Full signature:

```java
public ConfigurationException()
```

Input domain: no inputs.  Return shape: one new
`org.apache.commons.configuration2.ex.ConfigurationException` instance.

The instance has the standard no-argument `Exception` state: `getMessage()`
returns `null` and `getCause()` returns `null`.  No checked or unchecked
exception is expected from valid construction.  There is no ordering
concern, because the constructor accepts no sequence of values.

Normal example:

```java
ConfigurationException error = new ConfigurationException();
if (error.getMessage() != null) {
    throw new AssertionError("unexpected message");
}
```

Edge example: catching this object as `Exception` must work because the class
is checked and extends `java.lang.Exception` directly:

```java
try {
    throw new ConfigurationException();
} catch (Exception error) {
    // The catch is valid without a runtime-specific adapter.
}
```

### `ConfigurationException(String message)`

Full signature:

```java
public ConfigurationException(String message)
```

Input domain: any `String`, including the empty string and a string containing
Unicode, newlines, or leading/trailing whitespace.  A `null` reference is
accepted by the standard exception contract and results in a null detail
message.  Return shape: one new exception instance.

The supplied message must be retained exactly; do not trim, normalize,
translate, or otherwise rewrite it.  The cause is unset unless established by
standard superclass behavior for this overload, so `getCause()` is `null` for
normal use.  Construction has no external side effect and does not reorder
anything.

Normal example:

```java
ConfigurationException error =
    new ConfigurationException("settings file could not be opened");
if (!"settings file could not be opened".equals(error.getMessage())) {
    throw new AssertionError("message was changed");
}
```

Edge example:

```java
String message = "  bad key\n\u03bb  ";
ConfigurationException error = new ConfigurationException(message);
if (!message.equals(error.getMessage())) {
    throw new AssertionError("whitespace or Unicode was changed");
}
```

### `ConfigurationException(String format, Object... params)`

Full signature:

```java
public ConfigurationException(String format, Object... params)
```

Input domain: a Java format string plus zero or more formatting arguments.
Arguments are consumed in their original left-to-right order by the ordinary
`String.format(format, params)` contract.  The return shape is one new
exception instance whose detail message is the formatted `String`; its cause
is not supplied by this overload.

Formatting must use Java's standard `String.format` semantics, including
conversion rules, placeholder ordering, and the JVM's normal default-locale
behavior.  There is no file or process side effect.  A malformed format or an
argument that cannot satisfy a conversion must propagate the corresponding
unchecked formatting exception, such as `IllegalFormatException`; do not
silently substitute a literal message.  A null format follows standard
`String.format` behavior and may raise `NullPointerException`.

Normal example:

```java
ConfigurationException error = new ConfigurationException(
    "Could not load %s after %d attempts", "settings.ini", 2);
// error.getMessage() is "Could not load settings.ini after 2 attempts".
```

Edge example:

```java
ConfigurationException error = new ConfigurationException(
    "key=%s value=%d", "port", 8080);
// The first argument fills %s and the second fills %d.
```

### `ConfigurationException(String message, Throwable cause)`

Full signature:

```java
public ConfigurationException(String message, Throwable cause)
```

Input domain: any direct message reference and any `Throwable` reference,
including a null cause.  Return shape: one new exception instance.  The direct
message is retained exactly, and the exact supplied cause object is observable
through `getCause()`; no copy or replacement cause is allowed.

Construction does not throw a checked exception and has no external side
effect.  The cause chain preserves the order `ConfigurationException` then
the supplied `Throwable`.  Do not format the direct message or concatenate
the cause into it.

Normal example:

```java
IllegalArgumentException cause = new IllegalArgumentException("bad port");
ConfigurationException error =
    new ConfigurationException("port is invalid", cause);
if (error.getCause() != cause) {
    throw new AssertionError("cause identity was not preserved");
}
```

Edge example:

```java
ConfigurationException error =
    new ConfigurationException("no underlying failure", null);
// A null cause remains observable as error.getCause() == null.
```

### `ConfigurationException(Throwable cause)`

Full signature:

```java
public ConfigurationException(Throwable cause)
```

Input domain: any `Throwable`, including `null`.  Return shape: one new
exception instance.  The supplied cause is passed through standard Java
exception semantics.  The default detail message follows the JDK
`Exception(Throwable)` behavior rather than a task-specific rewritten string;
in particular, a non-null cause normally contributes its `toString()` text.

There are no checked exceptions or external side effects for valid input.  A
null cause is allowed and leaves the cause unset.  The single cause is not
reordered or wrapped in another exception.

Normal example:

```java
RuntimeException cause = new RuntimeException("parser stopped");
ConfigurationException error = new ConfigurationException(cause);
if (error.getCause() != cause) {
    throw new AssertionError("cause identity was not preserved");
}
```

Edge example:

```java
ConfigurationException error = new ConfigurationException((Throwable) null);
if (error.getCause() != null) {
    throw new AssertionError("null cause was changed");
}
```

The explicit cast in the edge example selects the cause overload when the
argument is null; without a cast, Java overload resolution may be ambiguous.

### `ConfigurationException(Throwable cause, String format, Object... params)`

Full signature:

```java
public ConfigurationException(Throwable cause, String format, Object... params)
```

Input domain: a cause reference, a Java format string, and zero or more
formatting arguments.  Arguments are consumed left to right by
`String.format(format, params)`.  Return shape: one new exception with the
formatted detail message and the exact supplied cause.

Use standard Java formatting behavior.  Invalid format syntax, incompatible
arguments, or a null format must propagate the normal unchecked exception
from the JDK rather than being swallowed.  A valid null cause remains null.
Construction has no external side effect; the cause is not converted into a
message and the formatting arguments are not reordered.

Normal example:

```java
Throwable cause = new IllegalStateException("parser stopped");
ConfigurationException error = new ConfigurationException(
    cause, "failed while reading key %s", "database.url");
// The message is formatted and error.getCause() == cause.
```

Edge example:

```java
ConfigurationException error = new ConfigurationException(
    null, "attempt %d of %d", 1, 3);
// The message is "attempt 1 of 3" and the cause remains null.
```

### Inherited Observable Behavior

No override of `getMessage()` or `getCause()` is required by this contract.
The class should rely on the standard `Throwable` state so that callers can
use `getMessage()`, `getCause()`, `toString()`, and stack-trace methods in the
usual way.  These inherited methods return or display the state created by
the selected constructor; they do not perform I/O as part of object creation.

## Implementation Notes

1. Declare the exact package and public class name.  The class must extend
   `java.lang.Exception`, not `RuntimeException` and not a custom base class.
2. Keep all implementation code in
   `src/main/java/org/apache/commons/configuration2/ex/ConfigurationException.java`.
3. Implement all six signatures exactly, including the order of the
   `Throwable`, `String`, and varargs parameters in the final overload.
4. Use superclass exception construction so direct messages and cause
   identity remain observable through inherited methods.
5. For formatted overloads, use the standard JDK formatting contract.  Do not
   implement a second formatter, sort arguments, or normalize format text.
6. Preserve the distinction between a direct-message overload and a
   formatted-message overload.  A direct string is not a format string unless
   the formatted overload is selected by its arguments.
7. Preserve Java overload behavior.  In particular, callers may need an
   explicit `(Throwable) null` or `(String) null` cast when selecting among
   overloads with null arguments.
8. Do not add fields, caches, registries, global mutable state, logging,
   filesystem writes, network access, subprocess execution, reflection, or
   locale-changing code.
9. The class must be deterministic for the same constructor inputs, except
   for ordinary JDK formatting behavior that depends on the JVM default
   locale.  Do not promise locale-independent output beyond `String.format`.
10. Keep the Maven project single-module and offline.  The POM must not cause
    a build plugin or dependency download during candidate execution.
11. Compile with `javac --release 21` or the equivalent offline Maven command.
    No third-party JAR is needed for this contract.
12. Do not add a CLI or invent configuration readers.  The package name and
    class name are the only public entry points selected for this task.

### Small Verification Scenarios

The following public scenarios should be possible without network access:

```java
ConfigurationException empty = new ConfigurationException();
ConfigurationException direct = new ConfigurationException("bad input");
ConfigurationException formatted = new ConfigurationException(
    "bad key %s", "server.port");
```

`empty.getMessage()` is null, `direct.getMessage()` is exactly `"bad input"`,
and `formatted.getMessage()` is exactly `"bad key server.port"`.

```java
Throwable cause = new IllegalArgumentException("not numeric");
ConfigurationException chained = new ConfigurationException(
    "invalid value", cause);
ConfigurationException chainedFormatted = new ConfigurationException(
    cause, "invalid key %s", "port");
```

Both chained objects retain the same `cause` object by identity.  The first
message is `"invalid value"`, and the second is `"invalid key port"`.

### Boundary and Error Scenarios

An empty direct message is still a valid message and must not become null or
be replaced with a default phrase.  Unicode and newline characters are data,
not reasons to trim or escape the message.  A malformed `%` conversion in a
formatted constructor must expose the JDK's unchecked formatting failure.

The candidate must not claim support for file-based configuration, XML,
properties, environment variables, network URLs, interpolation, reload
policies, or any other Apache Commons Configuration feature.  Those APIs are
outside the selected inventory and are not confidently bindable for this
task.
