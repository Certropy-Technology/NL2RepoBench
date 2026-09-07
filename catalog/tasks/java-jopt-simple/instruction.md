## Project Description

Recreate the bounded, deterministic value-object portion of jopt-simple as a
small Java/Maven project. The target user needs a type for an option value that
may be written as `key=value`, including values that contain additional equals
signs. The implementation must expose the public type
`net.sf.joptsimple.KeyValuePair` with the record shape and behavior described
in this specification.

This task is intentionally limited to one pure value object. It does not ask
for the jopt-simple option parser, option specifications, converters, help
formatting, command-line argument collection, logging, configuration files,
filesystem access, network access, or a command-line executable. Do not add
those unrelated APIs.

### Natural Language Instruction

Create a single-module Maven project rooted at `workspace/`. Put the public
source at `src/main/java/net/sf/joptsimple/KeyValuePair.java` and make it
compile on Java 21. Implement `KeyValuePair` as a public record with exactly
two components, `String key` followed by `String value`.

The project must provide these capabilities:

1. Construct a pair from a key and a value using the record's public canonical
   constructor.
2. Parse a string with `KeyValuePair.valueOf(String)` using only the first
   equals sign as the separator.
3. Return the two components through the generated public `key()` and
   `value()` accessors without trimming or normalizing them.
4. Preserve normal Java record equality and hash-code semantics for both
   components.
5. Produce the stable string representation specified by `toString()`.

Use package declaration `net.sf.joptsimple`. The public import is:

```java
import net.sf.joptsimple.KeyValuePair;
```

The implementation may use the Java standard library only. Do not introduce
third-party Maven dependencies or require a network download. The candidate
project must be usable from an empty workspace with the stated Maven and JDK
versions.

## Supports

### Runtime and Build Environment

The supported environment is:

```text
Language: Java
JDK: Temurin 21.0.12+8
Compiler language level: Java 21 / --release 21
Build tool: Apache Maven 3.9.11
Platform: Linux amd64 with glibc
Runtime dependencies: none
```

The project is a single Maven module. A minimal `pom.xml` is required as
project metadata and must identify the Java 21 source and target level. The
implementation must compile with:

```bash
mvn --offline validate
mvn --offline test
```

No extra dependency is needed for the public class. Do not add repositories,
plugins, profiles, modules, extensions, generated sources, or custom test
commands merely to implement this contract. A standard Maven build may be
used to compile the source, but behavior must not depend on Maven at runtime.

### Network and Side-Effect Boundary

Agent, candidate, verifier, Oracle, and control execution all run with no
network access. They must not contact GitHub, Maven Central, DNS, or any
external service. The implementation must not read or write files, inspect
environment variables, start processes, use global mutable state, or perform
I/O. All supported operations are local and deterministic.

### Project Directory Structure

Create this public project layout:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── net/
                └── sf/
                    └── joptsimple/
                        └── KeyValuePair.java
```

The package directory and file name must match the import path exactly. No
CLI entry point, resource directory, service loader, or additional public
module is required. If a Maven module descriptor is included, it may export
`net.sf.joptsimple`, but it must not create additional task APIs.

## API Usage Guide

### `net.sf.joptsimple.KeyValuePair`

Import the public record with:

```java
import net.sf.joptsimple.KeyValuePair;
```

The exact public type is:

```java
public record KeyValuePair(String key, String value)
```

The component order is part of the contract: `key` is first and `value` is
second. The type is immutable in the normal Java record sense. The record does
not perform I/O, mutate shared state, or retain any mutable collection.

### Public canonical constructor

Signature:

```java
public KeyValuePair(String key, String value)
```

The constructor accepts any `String` reference for either component, including
`null` and the empty string. It stores the two references as the record
components in their original order. It does not split, trim, decode, validate,
or otherwise transform either argument. It returns a new
`net.sf.joptsimple.KeyValuePair` instance and has no side effects.

Normal example:

```java
KeyValuePair pair = new KeyValuePair("mode", "fast");
// pair.key().equals("mode")
// pair.value().equals("fast")
```

Edge example:

```java
KeyValuePair emptyParts = new KeyValuePair("", null);
// emptyParts.key().isEmpty()
// emptyParts.value() == null
```

There is no task-specific checked or unchecked exception for null components.
The constructor has the ordinary allocation behavior of a Java record.

### `valueOf` parser

Import path and signature:

```java
net.sf.joptsimple.KeyValuePair.valueOf(String asString)
public static KeyValuePair valueOf(String asString)
```

`asString` is any non-null Java string. The method searches for the first
literal `=` character. When no `=` is present, it returns a new pair whose key
is the complete input and whose value is `null`. When `=` is present, the key
is the substring before that first character and the value is the complete
substring after it. The value may contain later `=` characters unchanged.

The method preserves every other character, including whitespace, tabs,
Unicode characters, punctuation, and line terminators. It does not trim,
case-fold, escape, URL-decode, or convert either component. Parsing is
deterministic for the same input and has no filesystem, environment, process,
network, logging, or global-state side effect.

Normal example:

```java
KeyValuePair setting = KeyValuePair.valueOf("mode=fast");
// setting.key().equals("mode")
// setting.value().equals("fast")
```

Value-preservation example:

```java
KeyValuePair expression = KeyValuePair.valueOf("query=a=b=c");
// expression.key().equals("query")
// expression.value().equals("a=b=c")
```

No-separator example:

```java
KeyValuePair flag = KeyValuePair.valueOf("debug");
// flag.key().equals("debug")
// flag.value() == null
```

The method throws `NullPointerException` when `asString` is `null`. Empty input
is valid: `KeyValuePair.valueOf("")` has an empty key and a null value. The
method must not replace that null with an empty string.

### Generated component accessor `key`

Signature:

```java
public String key()
```

The accessor returns the key component exactly as stored by the canonical
constructor or produced by `valueOf`. Its return type is `String`; it may be
`null` for a directly constructed pair, but a parsed pair always has a
non-null key because the input string itself is non-null. The accessor has no
side effects and throws no task-specific exception.

Example:

```java
String key = KeyValuePair.valueOf("  user name =Ada ").key();
// key.equals("  user name ")
```

### Generated component accessor `value`

Signature:

```java
public String value()
```

The accessor returns the value component exactly as stored. It returns `null`
when a directly constructed pair was given null or when `valueOf` received a
non-empty string with no separator. It returns the empty string for a trailing
separator such as `"key="`. It does not trim whitespace or collapse later
separators, and it has no side effects or task-specific exception.

Example:

```java
String value = KeyValuePair.valueOf("key=  value  ").value();
// value.equals("  value  ")
```

### Record equality and `hashCode`

The record must retain the standard generated public methods:

```java
public boolean equals(Object other)
public int hashCode()
```

Two `KeyValuePair` instances compare equal exactly when both their key and
value components compare equal under normal record component semantics. A
null component compares equal only to another null component. Equality with
`null` or with an object of another type is false. `hashCode()` is consistent
with `equals()` and incorporates both components. Neither operation performs
I/O or changes the pair.

Example:

```java
KeyValuePair first = KeyValuePair.valueOf("a=b");
KeyValuePair second = new KeyValuePair("a", "b");
// first.equals(second) is true
// first.hashCode() == second.hashCode()
```

Edge example:

```java
KeyValuePair withoutValue = KeyValuePair.valueOf("a");
KeyValuePair emptyValue = new KeyValuePair("a", "");
// withoutValue.equals(emptyValue) is false because null != ""
```

### `toString`

Signature:

```java
public String toString()
```

The string form is the key, followed by one literal `=`, followed by the
standard string representation of the value component. In particular, a null
value is rendered as the four characters `null`; it is not rendered as an
empty value. Existing equals signs in either component are not escaped.
The method is deterministic, has no side effects, and returns a non-null
`String` for every valid pair.

Normal example:

```java
KeyValuePair pair = new KeyValuePair("mode", "fast");
// pair.toString().equals("mode=fast")
```

Edge examples:

```java
KeyValuePair noSeparator = KeyValuePair.valueOf("debug");
// noSeparator.toString().equals("debug=null")

KeyValuePair trailing = KeyValuePair.valueOf("key=");
// trailing.toString().equals("key=")
```

## Implementation Notes

Keep the public surface narrow: the only required public project type is
`net.sf.joptsimple.KeyValuePair`. Do not implement or expose `OptionParser`,
option specifications, converters, help formatters, or command-line parsing.
Those classes exist in the upstream library but are outside this bounded
contract and are not confidently bindable to this task's public behavior.

Use Java record syntax so that component declaration, canonical construction,
accessors, equality, and hashing have their normal Java 21 semantics. The
component order must remain `String key, String value`. Do not add validation
that changes the constructor's acceptance of null or empty components.

For `valueOf`, preserve the distinction among null, empty, and absent values:

```java
KeyValuePair.valueOf("")       // key "", value null
KeyValuePair.valueOf("=")      // key "", value ""
KeyValuePair.valueOf("key=")   // key "key", value ""
KeyValuePair.valueOf("=value") // key "", value "value"
```

Use only the first separator. These examples describe observable behavior,
not a required algorithm:

```java
KeyValuePair.valueOf("a=b=c");       // key "a", value "b=c"
KeyValuePair.valueOf("  a = b  ");   // key "  a ", value " b  "
KeyValuePair.valueOf("na\u00efve=\u7ec8\u70b9"); // preserve Unicode text
KeyValuePair.valueOf("a==");         // key "a", value "="
```

Do not split on every equals sign, trim either side, discard whitespace,
reject repeated separators, or reinterpret Unicode. Do not add escaping or
type conversion. A malformed-looking but non-null string is still valid input;
only a null parser argument has the specified exception behavior.

The implementation must remain deterministic across repeated calls and across
processes. It must not use the clock, randomness, locale, default charset,
system properties, environment variables, filesystem, subprocesses, or
network services. A Maven build may compile and test the source, but no
runtime behavior may depend on Maven or an installed jopt-simple artifact.

Before completion, verify that the package declaration, filename, record
components, public signatures, Java 21 compilation, and no-dependency Maven
layout match this specification. Keep tests small and behavior-focused if
tests are added locally; do not copy upstream tests, private verifier cases,
hidden leaf identifiers, or an implementation algorithm into the public
instruction.
