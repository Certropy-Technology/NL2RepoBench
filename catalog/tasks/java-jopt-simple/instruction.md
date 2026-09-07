# Introduction and Goals of the jopt-simple Project

jopt-simple is a Java command-line option parsing library. This task isolates
its small deterministic `KeyValuePair` value object. Create a normal
single-module Maven project that supplies the exact public type below. Option
parsing, converters, help formatting, and command-line I/O are outside this
bounded task.

## Natural Language Instruction (Prompt)

Implement `net.sf.joptsimple.KeyValuePair` as a Java record with the exact
public API described here. It represents the first `=` separated key and value
from an input string. Keep source under `src/main/java` and use only the Java
standard library.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies,
plugins, profiles, repositories, modules, extensions, or custom test commands.
The trusted verifier invokes candidate code through a separate JVM and owns
grading reports.

## jopt-simple Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/net/sf/joptsimple/KeyValuePair.java
```

The exact public type is `net.sf.joptsimple.KeyValuePair`. No option parser,
CLI entry point, filesystem behavior, network behavior, or external library is
required.

## API Usage Guide

### Core APIs

```java
public record KeyValuePair(String key, String value)
public static KeyValuePair valueOf(String asString)
public String key()
public String value()
public String toString()
```

`valueOf` finds the first `=` character. If no equals sign exists, `key()` is
the complete input and `value()` is `null`. Otherwise `key()` is every
character before the first equals sign and `value()` is every character after
it. An equals sign at the beginning gives an empty key; an equals sign at the
end gives an empty value. Later equals signs remain in the value unchanged.
A null argument throws `NullPointerException`.

The generated record accessors return the original strings. Record equality and
hash code use both components. `toString()` returns `key + "=" + value`; a
null value therefore appears as the four characters `null`.

```java
KeyValuePair plain = KeyValuePair.valueOf("debug");
// plain.key() == "debug", plain.value() == null, plain.toString().equals("debug=null")

KeyValuePair configured = KeyValuePair.valueOf("mode=fast=trace");
// configured.key().equals("mode"), configured.value().equals("fast=trace")
```

### Actual Usage Modes

Use this value object to represent a local key/value argument such as a JVM
property. Parsing is deterministic, preserves whitespace and all characters
after the first equals sign, and has no side effects.

### Supported Function Types

The supported functions are record construction, first-separator string
splitting, component access, record equality, record hashing, and the stable
string form. Delimiter escaping, trimming, type conversion, repeated-option
collection, and command-line parsing are not part of this task.

### Error Handling

`valueOf(null)` must throw `NullPointerException`. Empty input is valid and
produces an empty key with a null value. Do not trim, normalize, discard, or
split later equals signs. No supported API performs I/O.

## Detailed Implementation Nodes of Functions

### Node 1: Exact record layout

Declare the exact package, record name, component names, and component order:
`String key` followed by `String value`.

### Node 2: First-equals parsing

Locate only the first equals sign. With no sign, preserve the entire input as
the key and use null for the value.

### Node 3: Empty component boundaries

Inputs `""`, `"="`, `"key="`, and `"=value"` are meaningful. Empty is not
the same as null.

### Node 4: Value preservation

Keep all text after the first equals sign byte-for-character, including later
equals signs and surrounding spaces.

### Node 5: Record semantics

Accessors, equality, hash code, and `toString()` follow normal Java record
semantics. The string form always includes one equals sign followed by the
value's string representation.

### Node 6: Determinism and isolation

All behavior is local and deterministic. The implementation must compile with
`javac --release 21`, require no Maven dependencies, and perform no network,
filesystem, process, or environment access.
