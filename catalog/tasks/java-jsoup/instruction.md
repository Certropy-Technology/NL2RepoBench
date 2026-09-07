# Introduction and Goals of the jsoup Project

jsoup is a Java library for working with HTML. This task isolates the small, deterministic public value-object behavior of `org.jsoup.nodes.Attribute`. Recreate this bounded API in a normal single-module Maven project. HTML parsing, serialization, selectors, HTTP, and entity escaping are outside this task.

## Natural Language Instruction (Prompt)

Create a Java Maven project that provides `org.jsoup.nodes.Attribute`. Implement the constructor and methods listed below using only the Java standard library. Put source under `src/main/java` and preserve the exact package and signatures.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies, plugins, profiles, repositories, modules, extensions, or custom test commands. The verifier compiles candidate code separately and owns the grading reports.

## jsoup Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/jsoup/nodes/Attribute.java
```

## API Usage Guide

### Core APIs

Implement this public type and these exact signatures:

```java
package org.jsoup.nodes;

public class Attribute implements java.util.Map.Entry<String, String>, Cloneable {
    public Attribute(String key, String value)
    public String getKey()
    public void setKey(String key)
    public String getValue()
    public boolean hasDeclaredValue()
    public String setValue(String value)
    public String prefix()
    public String localName()
}
```

The constructor and `setKey` reject null, empty, and whitespace-only keys with a runtime argument failure. Non-empty keys are trimmed, while their remaining case is preserved. A value may be null. `getValue()` maps a null value to `""`; `hasDeclaredValue()` is false only for a null stored value. `setValue` returns the previous value, mapping a previous null to `""`, then stores the supplied value.

`prefix()` returns the substring before the first colon, or `""` when no colon occurs. `localName()` returns the substring after the first colon, or the full key when no colon occurs. A leading or trailing colon is meaningful: `":name"` has prefix `""` and local name `"name"`; `"og:"` has prefix `"og"` and local name `""`.

Examples:

```java
Attribute href = new Attribute(" href ", "index.html");
href.getKey();                    // "href"
href.setValue(null);              // "index.html"
href.getValue();                  // ""
href.hasDeclaredValue();          // false

Attribute property = new Attribute("og:title", "News");
property.prefix();                // "og"
property.localName();             // "title"
```

### Actual Usage Modes

Use an `Attribute` as a mutable key/value presentation object. The supported state is only its key and optional value; it has no parent collection behavior in this bounded task.

### Supported Function Types

The supported function types are key validation and normalization, optional-value state, key/value mutation, and colon-based namespace-like key splitting. HTML output, XML namespace resolution, entity escaping, attribute collections, cloning, equality, parsing, and network operations are not required.

### Error Handling

Null, empty, and whitespace-only keys must fail promptly. A null value is valid and represents a declared boolean-style attribute with no value. No API may silently substitute a key, perform I/O, access network resources, or mutate external state.

## Detailed Implementation Nodes of Functions

### Node 1: Key construction and normalization

Validate keys before storing them. Trim leading and trailing Java whitespace and preserve case in the normalized remainder.

### Node 2: Optional values

Keep the distinction between a null stored value and the empty string, while exposing null as an empty string through the `Map.Entry` getter and previous-value return contract.

### Node 3: Key mutation

`setKey` applies the same validation and trim rule as construction. It updates only this value object.

### Node 4: Value mutation

`setValue` first reports the old observable value and then stores exactly the supplied value, including null.

### Node 5: Prefix and local name

Split only on the first colon. Do not lowercase, decode, or interpret further colons.

### Node 6: Determinism and state

All outcomes are deterministic and local to the instance. No function accesses a filesystem, parser, HTTP client, or external Maven artifact.

### Node 7: Source and package layout

Use the exact `org.jsoup.nodes` package and `Attribute` type. The project must compile with `javac --release 21` and the standard Maven layout.

### Node 8: Offline build behavior

Keep the Maven closure empty and do not download anything at runtime. The trusted verifier invokes candidate code through a JSON/JVM adapter rather than importing candidate classes.
