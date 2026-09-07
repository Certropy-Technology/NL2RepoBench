## Project Description

Apache Commons Logging is a small Java logging abstraction used by libraries
that should not depend on a particular logging backend.

This task asks you to recreate the bounded, deterministic no-op logger used by
the project: `org.apache.commons.logging.impl.NoOpLog`.

The result is a single-module Java project that can be compiled offline with
Maven metadata and the Java standard library.

The logger accepts normal logging calls but intentionally discards every
message and throwable.

Every supported logging level is disabled.

The public type must remain usable through the `org.apache.commons.logging.Log`
interface.

The public behavior is local and deterministic.

It must not open files, write output, contact a service, load a logging
backend, or mutate process-wide logging configuration.

The target users are Java library authors who need a compatible logger object
without a runtime logging dependency.

The input boundary is Java objects supplied to constructors, level methods,
and level-query methods.

The output boundary is the Java type relationship, boolean query results, and
normal return from void logging methods.

Do not add a command-line interface, a network logger, a file logger, a
formatter, a logger factory, or additional public modules.

## Supports

### Natural Language Instruction

Create the project from an empty `workspace/` directory.

Implement the public `NoOpLog` contract under `src/main/java`.

Preserve the exact package names and public Java signatures in this document.

Provide the companion `org.apache.commons.logging.Log` interface required by
the implementation.

Make `NoOpLog` implement both `Log` and `java.io.Serializable`.

Provide both public constructors.

Provide all six level-query methods and all twelve logging overloads.

Make every level-query method return `false`.

Make every logging method return normally without observable output or state
changes.

Treat null messages, null throwables, and a null constructor name as valid
inputs.

Keep the project single-module and standard-library-only at runtime.

Do not copy an unrelated Commons Logging class or expose APIs not listed here.

### Runtime and Dependency Configuration

Use Temurin JDK `21.0.12+8`.

Use Maven `3.9.11` for project metadata validation.

The target platform is Linux amd64 with glibc.

The project must compile with Java release 21.

Runtime dependencies are empty.

The Java standard library is sufficient for `Serializable` and the logger
contract.

Execution is offline.

The agent, candidate, verifier, Oracle, and controls must not access GitHub,
Maven Central, DNS, or any other external service during execution.

The root `pom.xml` is metadata for a single jar project.

It must not introduce dependencies, plugins, profiles, repositories, modules,
extensions, or custom build behavior.

### Project Directory Structure

Create this public project structure:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── logging/
                            ├── Log.java
                            └── impl/
                                └── NoOpLog.java
```

`pom.xml` must identify a single Maven artifact and use jar packaging.

`Log.java` must declare the public interface in package
`org.apache.commons.logging`.

`NoOpLog.java` must declare the public class in package
`org.apache.commons.logging.impl`.

There is no required application main class.

There is no required resource directory.

There is no required test package in the created project.

### Supported Usage Modes

Instantiate `new NoOpLog()` when no component name is needed.

Instantiate `new NoOpLog("storage")` when a caller has a component name.

Assign either instance to a `Log` reference.

Check an `is*Enabled()` method before constructing expensive log messages.

Call a one-argument or two-argument level method when a message or cause is
available.

All of these modes must remain local, offline, and deterministic.

## API Usage Guide

### Public Type: `org.apache.commons.logging.Log`

Import the interface with:

```java
import org.apache.commons.logging.Log;
```

The interface is the public logging contract implemented by `NoOpLog`.

Its methods accept any `Object` message, including `null`.

Its two-argument methods accept any `Throwable`, including `null`.

The methods return `void` and have no declared checked exceptions.

Implementations must not require a backend merely to satisfy this interface.

### `Log.debug(Object message)`

Signature: `public void debug(Object message)`.

The input may be any object reference or `null`.

The return type is `void`.

The method must not write the message to stdout, stderr, a file, or a service.

The method must not mutate the logger or global state.

The call returns normally for `debug("cache hit")`.

The edge call `debug(null)` must also return normally.

No checked or unchecked exception is part of the contract for these inputs.

### `Log.debug(Object message, Throwable t)`

Signature: `public void debug(Object message, Throwable t)`.

The message may be any object reference or `null`.

The throwable may be any `Throwable` reference or `null`.

The return type is `void`.

Neither argument is inspected for output or formatting.

The call `debug("retry", new IllegalStateException())` returns normally.

The edge call `debug(null, null)` returns normally.

No checked or unchecked exception is part of the contract for these inputs.

### `Log.error(Object message)`

Signature: `public void error(Object message)`.

The method accepts any object reference, including `null`, and returns `void`.

It discards the value without output or external side effects.

The normal example is `error("request rejected")`.

The edge example is `error(null)`.

Both calls return normally and preserve all subsequent logger behavior.

### `Log.error(Object message, Throwable t)`

Signature: `public void error(Object message, Throwable t)`.

The message and throwable are independently nullable object references.

The method returns `void` and does not print or persist either value.

The normal example is `error("parse failed", cause)`.

The edge example is `error(null, null)`.

No checked exception is declared or required for either example.

### `Log.fatal(Object message)`

Signature: `public void fatal(Object message)`.

The method accepts any object reference or `null`.

It returns `void` without throwing for the documented input domain.

It must discard the message rather than terminate or alter the process.

The normal example is `fatal("configuration unavailable")`.

The edge example is `fatal(null)`.

No output, file operation, or network operation is permitted.

### `Log.fatal(Object message, Throwable t)`

Signature: `public void fatal(Object message, Throwable t)`.

Both arguments may be arbitrary references, including two null references.

The method returns `void` and does not rethrow the supplied throwable.

The normal example is `fatal("startup failed", cause)`.

The edge example is `fatal(null, null)`.

The method has no declared checked exceptions.

### `Log.info(Object message)`

Signature: `public void info(Object message)`.

The message domain is any object reference, including `null`.

The method returns `void` and discards the input.

The normal example is `info("opened local cache")`.

The edge example is `info(null)`.

Repeated calls have no cumulative effect and preserve deterministic behavior.

### `Log.info(Object message, Throwable t)`

Signature: `public void info(Object message, Throwable t)`.

The method accepts nullable message and throwable references.

It returns `void` without formatting, output, or persistence.

The normal example is `info("fallback selected", cause)`.

The edge example is `info(null, null)`.

The method must not throw for either documented example.

### `Log.trace(Object message)`

Signature: `public void trace(Object message)`.

The method accepts any object reference or `null` and returns `void`.

It must discard the value and perform no observable operation.

The normal example is `trace("entered parser")`.

The edge example is `trace(null)`.

Calls may be made before or after any level query.

### `Log.trace(Object message, Throwable t)`

Signature: `public void trace(Object message, Throwable t)`.

The message and throwable may both be null.

The method returns normally with return type `void`.

The normal example is `trace("token read", cause)`.

The edge example is `trace(null, null)`.

The throwable must not be printed, stored, or rethrown.

### `Log.warn(Object message)`

Signature: `public void warn(Object message)`.

The method accepts any object reference or `null`.

It returns `void`, discards the message, and has no external side effect.

The normal example is `warn("using default")`.

The edge example is `warn(null)`.

No checked or unchecked exception is expected for these inputs.

### `Log.warn(Object message, Throwable t)`

Signature: `public void warn(Object message, Throwable t)`.

The method accepts independently nullable message and throwable references.

It returns `void` without emitting or retaining either argument.

The normal example is `warn("deprecated option", cause)`.

The edge example is `warn(null, null)`.

The method must not rethrow the supplied throwable.

### `Log.isDebugEnabled()`

Signature: `public boolean isDebugEnabled()`.

The method takes no arguments and returns a primitive `boolean`.

For `NoOpLog`, the result is always `false`.

The result is the same before and after any debug call.

The normal example is `if (log.isDebugEnabled()) { ... }`.

There are no documented exceptions or side effects.

### `Log.isErrorEnabled()`

Signature: `public boolean isErrorEnabled()`.

The method takes no arguments and returns `false` for every `NoOpLog` instance.

The result does not depend on constructor name, message history, or thread.

The normal example is `boolean enabled = log.isErrorEnabled()`.

The edge case is calling it after `error(null, null)`; it remains `false`.

### `Log.isFatalEnabled()`

Signature: `public boolean isFatalEnabled()`.

The method takes no arguments and returns primitive `false`.

It has no I/O, synchronization, or mutable-state requirement.

The normal example is `if (log.isFatalEnabled()) { report(); }`.

The edge case is querying a newly constructed logger; the result is still
`false`.

### `Log.isInfoEnabled()`

Signature: `public boolean isInfoEnabled()`.

The method takes no arguments and always returns `false`.

The result is deterministic across instances and call order.

The normal example is `boolean enabled = log.isInfoEnabled()`.

The edge case is querying after `info("ignored")`; it remains `false`.

### `Log.isTraceEnabled()`

Signature: `public boolean isTraceEnabled()`.

The method takes no arguments and always returns `false`.

It must not inspect or invoke any previously supplied message object.

The normal example is `if (log.isTraceEnabled()) { traceState(); }`.

The edge case is querying after `trace(null, null)`; it remains `false`.

### `Log.isWarnEnabled()`

Signature: `public boolean isWarnEnabled()`.

The method takes no arguments and always returns `false`.

It has no checked exceptions and no observable side effects.

The normal example is `boolean enabled = log.isWarnEnabled()`.

The edge case is querying a logger created with a null name; it remains
`false`.

### `NoOpLog()`

Import the class with `import org.apache.commons.logging.impl.NoOpLog;`.

Signature: `public NoOpLog()`.

The constructor creates a logger with all six levels disabled.

Construction must not perform I/O, discover a backend, or mutate global state.

The normal example is `Log log = new NoOpLog()`.

The resulting object can be used with every method listed above.

No checked exception is declared or expected.

### `NoOpLog(String name)`

Signature: `public NoOpLog(String name)`.

The string is accepted for compatibility and has no observable effect.

The input may be a component name such as `"worker"` or `null`.

The normal example is `NoOpLog log = new NoOpLog("worker")`.

The edge example is `new NoOpLog(null)`.

Both instances have identical disabled and no-op behavior.

No checked exception is declared or expected.

### `NoOpLog` Type Relationship

Declare `NoOpLog` as a public class implementing `Log` and
`java.io.Serializable`.

The serializable marker is a type contract; no custom serialization API is
required.

The class does not need to expose a logger name getter or mutable state.

The normal example is `Serializable value = new NoOpLog()`.

The edge example is assigning `new NoOpLog(null)` to a `Log` reference.

No additional public constructor, method, field, or CLI entry point is
confidently bindable from this task contract; do not invent one.

## Implementation Notes

Keep `Log.java` and `NoOpLog.java` in the exact packages shown in the directory
tree.

Use Java 21 syntax only where it does not alter the public contract.

Keep the Maven project single-module and compilable with no network access.

Do not add third-party dependencies to `pom.xml`.

Do not require Maven plugins or repositories for the implementation.

The implementation may use an empty body for a no-op logging method.

The implementation may return the boolean literal `false` for every level
query.

Do not print diagnostics as a substitute for logging behavior.

Do not convert a no-op call into an exception, process exit, or callback.

Do not call `toString()` on a message or throwable as an observable effect.

Do not retain message or throwable references after a method returns.

Constructor names must not change query results or logging behavior.

Call order must not affect later results.

Two separate `NoOpLog` instances must behave identically.

The six levels are independent names only; all are disabled.

The twelve logging overloads are independent entry points with the same
discarding behavior.

The interface and implementation must compile together from the stated source
roots.

The public package layout must match Java's package-to-directory convention.

The project must remain safe when callers pass arbitrary object subclasses.

The project must remain safe when callers pass throwable subclasses whose
messages or causes have side effects if inspected.

Small verification example 1: construct `new NoOpLog("component")`, call
`debug("ignored")`, and confirm that all six queries remain `false`.

```java
NoOpLog log = new NoOpLog("component");
log.debug("ignored");
assert !log.isDebugEnabled();
assert !log.isInfoEnabled();
```

Small verification example 2: construct `new NoOpLog(null)`, call every
two-argument method with `(null, null)`, and confirm that all calls return.

```java
NoOpLog log = new NoOpLog(null);
log.debug(null, null);
log.error(null, null);
log.fatal(null, null);
log.info(null, null);
log.trace(null, null);
log.warn(null, null);
```

Small verification example 3: assign a `NoOpLog` to `Log`, call `warn("x")`,
and confirm that the assignment and call compile through the interface.

```java
Log log = new NoOpLog();
log.warn("x");
```

Small verification example 4: create two instances with different names and
compare every enabled query; each result must be `false` for both instances.

```java
NoOpLog first = new NoOpLog("one");
NoOpLog second = new NoOpLog("two");
assert !first.isWarnEnabled();
assert !second.isWarnEnabled();
```

These examples describe observable behavior without prescribing a particular
internal algorithm or copying reference source.

There is no CLI command to document for this bounded library slice.

There is no network configuration to implement beyond preserving the stated
offline boundary.

Keep comments focused on constraints that are not obvious from the signatures.

Do not add private test names, grader protocols, artifact identifiers, or
reference-source download instructions to the project.
