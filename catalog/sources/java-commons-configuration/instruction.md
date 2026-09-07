# Introduction and Goals of the Commons Configuration Project

Apache Commons Configuration is a Java library for reading, representing, and
transforming application configuration data. This task focuses on one small,
deterministic public API from the frozen project: the
`org.apache.commons.configuration2.ex.ConfigurationException` checked
exception. The implementation must preserve its constructor overloads,
formatted messages, and cause chain without requiring external runtime
dependencies.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Configuration that provides
the public `ConfigurationException` behavior described below:

1. Define `org.apache.commons.configuration2.ex.ConfigurationException` as a
   checked exception extending `java.lang.Exception`.
2. Provide the no-argument constructor, message constructor, formatted-message
   constructor, message-and-cause constructor, cause constructor, and
   cause-plus-formatted-message constructor.
3. Preserve exact message text for direct messages.
4. Format the varargs message constructors with `String.format` semantics.
5. Preserve the supplied cause and its identity through `getCause()`.
6. Keep the implementation under `src/main/java` in a single-module Maven
   project. Do not add external runtime dependencies or candidate-controlled
   Maven build configuration.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime and javac compiler
Maven 3.9.11                # Offline project metadata/build tool
Linux amd64                 # Fixed execution platform
Runtime dependencies: none  # This bounded API uses java.lang.Exception only
Network access: unavailable # Agent, candidate, and verifier runs are offline
```

## Commons Configuration Project Architecture

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
                        └── configuration2
                            └── ex
                                └── ConfigurationException.java
```

The public package is `org.apache.commons.configuration2.ex`. The candidate
POM is metadata only. Do not add `<build>`, plugins, dependencies, profiles,
repositories, modules, parent configuration, or custom Maven extensions.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.commons.configuration2.ex.ConfigurationException;
```

#### 2. No-Argument Constructor

```java
ConfigurationException error = new ConfigurationException();
```

Signature:

```java
ConfigurationException()
```

The exception is created without a detail message or cause.

#### 3. Direct Message Constructor

```java
ConfigurationException error = new ConfigurationException("could not load file");
```

Signature:

```java
ConfigurationException(String message)
```

`getMessage()` returns the supplied message unchanged.

#### 4. Formatted Message Constructor

```java
ConfigurationException error = new ConfigurationException(
    "could not load %s (%d)", "settings.ini", 2);
```

Signature:

```java
ConfigurationException(String format, Object... params)
```

The message is the result of `String.format(format, params)` and the cause is
unset.

#### 5. Message-and-Cause Constructor

```java
Throwable cause = new IllegalStateException("parser stopped");
ConfigurationException error = new ConfigurationException("load failed", cause);
```

Signature:

```java
ConfigurationException(String message, Throwable cause)
```

Both the direct message and cause must be preserved.

#### 6. Cause Constructor

```java
ConfigurationException error = new ConfigurationException(cause);
```

Signature:

```java
ConfigurationException(Throwable cause)
```

The cause is preserved using standard Java exception semantics.

#### 7. Cause-Plus-Formatted-Message Constructor

```java
ConfigurationException error = new ConfigurationException(
    cause, "failed at key %s", "database.url");
```

Signature:

```java
ConfigurationException(Throwable cause, String format, Object... params)
```

The message is formatted with `String.format`; the supplied cause is retained.

### Actual Usage Modes

#### Basic Failure

```java
try {
    throw new ConfigurationException("invalid configuration");
} catch (ConfigurationException error) {
    System.out.println(error.getMessage());
}
```

#### Formatted Failure

```java
throw new ConfigurationException("missing key %s", "server.port");
```

#### Chained Failure

```java
Throwable cause = new IllegalArgumentException("not a number");
throw new ConfigurationException("invalid port", cause);
```

### Supported Function Types

The supported behavior consists of checked-exception inheritance, six public
constructors, exact direct messages, Java format-string behavior, and cause
preservation. No filesystem, locale, clock, reflection, or network behavior is
part of this task.

### Error Handling

Do not replace a supplied cause, silently discard a message, or substitute a
custom formatting implementation. Standard `String.format` failures for an
invalid format are not swallowed. The class must remain a checked exception.

## Detailed Implementation Nodes of Functions

### Node 1: Exception Type

Declare the exact public package and class and extend `Exception` directly.

### Node 2: Empty Constructor

Use the standard no-argument exception state: no detail message and no cause.

### Node 3: Direct Message

Delegate direct messages to the standard superclass constructor without
rewriting whitespace or punctuation.

### Node 4: Formatted Messages

Apply `String.format(format, params)` for both formatted overloads, preserving
placeholder ordering and numeric/string conversions.

### Node 5: Cause Preservation

Pass the exact `Throwable` object to the superclass so identity and cause
messages remain observable through `getCause()`.

### Node 6: Overload Resolution

Implement both varargs overloads with the exact parameter order shown above;
do not replace them with differently named helpers or generic catch-all APIs.

### Node 7: Maven Project Layout

Use the standard source path and a metadata-only Java 21 POM. The class must
compile without third-party artifacts.

### Node 8: Offline Build Behavior

The verifier compiles candidate sources with a separate JVM boundary and no
network. Do not invoke Maven plugins or external services from candidate code.
