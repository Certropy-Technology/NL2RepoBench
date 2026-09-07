## Project Description

Build a small Java Maven project that recreates the bounded public value-object
contract of jsoup's `org.jsoup.nodes.Attribute` class.

The project is for callers that need one HTML-style attribute key and its
optional value without requiring an HTML parser or a complete DOM. A caller
must be able to create an attribute, read its normalized key, distinguish an
absent value from an empty value, mutate the key and value, and split a key at
its first colon.

The implementation target is one public class:

```java
org.jsoup.nodes.Attribute
```

The class must implement `java.util.Map.Entry<String, String>` and
`java.lang.Cloneable`, as declared by the public type contract. Preserve the
exact package, public class name, public method names, parameter types, return
types, and mutability described in this document.

This task is a value-object slice. In scope are key validation and trimming,
nullable value state, `Map.Entry`-style key/value access, first-colon prefix
and local-name extraction, and deterministic behavior that is local to an
instance.

The candidate must build from an empty workspace using the standard Maven
layout. It must expose the class from
`src/main/java/org/jsoup/nodes/Attribute.java` and must not require a custom
launcher, service, database, parser, or generated source file.

The following are out of scope: parsing HTML or XML, serializing an element,
CSS selectors, DOM parent or owner relationships, document traversal, HTTP
requests, URL handling, entity escaping, namespace lookup, collections of
attributes, source-location tracking, plugin systems, and command-line
commands. Do not add substitute public APIs for those features.

The implementation must not perform filesystem, environment, network,
process, clock, locale, or global-state I/O. All observable results depend
only on the constructor arguments and current object state.

### Natural Language Instruction

Create the Maven project described below and implement the public
`org.jsoup.nodes.Attribute` contract from an empty workspace. Keep the exact
package and signatures, provide the mutable key/value state, preserve the
null-versus-empty value distinction, and implement first-colon prefix and
local-name extraction. Use only Java SE APIs, keep the dependency closure
empty, and make every operation deterministic and offline-safe. Do not broaden
the task into an HTML parser or DOM implementation.

## Supports

### Runtime and Build Contract

- Operating system: Linux amd64 with glibc.
- Java runtime and compiler: Temurin JDK `21.0.12+8`.
- Java language level: compile with `javac --release 21`.
- Build tool: Apache Maven `3.9.11`.
- Package manager: Maven, with an empty runtime dependency closure.
- Runtime dependencies: none beyond the Java SE 21 standard library.
- Network mode: no network access during agent, candidate, verifier, Oracle,
  or control execution.
- Do not download artifacts, resolve repositories, call DNS, or contact an
  external service at runtime.

The root `pom.xml` is required as Maven project metadata. It may identify the
project as `org.jsoup:jsoup`, but it must not add third-party dependencies,
repositories, modules, profiles, extensions, generated sources, or custom test
commands. The implementation must remain compilable when Maven is run
offline. Direct JDK compilation of the public source must also work.

### Project Directory Structure

Create this public project shape, rooted at `workspace/`:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── jsoup/
                    └── nodes/
                        └── Attribute.java
```

`pom.xml` is the Maven entry point. `Attribute.java` is the only required
production source file and its package declaration must be:

```java
package org.jsoup.nodes;
```

The verifier compiles and calls the class through a small Java adapter. Do not
add a required CLI entry point, `main` method, shell script, resource file,
test fixture, or network configuration. Ordinary Maven lifecycle commands must
not depend on a project-local repository.

### Installation and Harness Boundary

The harness creates or supplies the workspace, invokes offline build commands,
and owns test reporting. The candidate owns only the source and minimal Maven
metadata in the directory tree above.

The candidate must not write grading files, alter verifier-owned reports, read
hidden test files, or assume that a jsoup jar is available. The public class
must be usable directly after compilation with no initialization call.

## API Usage Guide

All APIs in this guide are members of the exact class
`org.jsoup.nodes.Attribute`. Unless stated otherwise, calls mutate only the
current `Attribute` instance and are deterministic. Java `null` is a valid
value argument but is not a valid key argument.

Import the public class from its exact package:

```java
import org.jsoup.nodes.Attribute;
```

### `Attribute(String key, String value)`

```java
public Attribute(String key, String value)
```

The constructor creates one mutable attribute object. `key` must be a
non-null string that is not empty after Java `String.trim()` normalization.
Leading and trailing characters removed by `trim()` are not stored. The
remaining key text, including its case, internal whitespace, additional
colons, and other ordinary characters, is preserved.

`value` may be any `String`, including `null`. A null value means that the
object currently has no declared value. The constructor stores the supplied
value state without converting null to an empty string.

The constructor returns an initialized `Attribute` and has no external side
effects. A null key, an empty key, or a key containing only characters removed
by `trim()` must fail promptly with `IllegalArgumentException`.

```java
Attribute title = new Attribute(" title ", "News");
title.getKey();
// returns "title"
title.getValue();
// returns "News"
```

```java
Attribute flag = new Attribute("disabled", null);
flag.hasDeclaredValue();
// returns false
flag.getValue();
// returns ""
```

```java
new Attribute(null, "x");
new Attribute("", "x");
new Attribute("   ", "x");
// each call throws IllegalArgumentException
```

### `getKey()`

```java
public String getKey()
```

Returns the normalized key stored by the constructor or the most recent
successful `setKey` call. The return type is `String`, and for every valid
object it is non-null and non-empty after construction normalization.

The method does not mutate the object or perform I/O. It returns the exact
stored key, preserving case and internal characters. Repeated calls return
the same text until `setKey` succeeds.

```java
Attribute a = new Attribute("  DATA-id  ", null);
String first = a.getKey();
String second = a.getKey();
// first and second are both "DATA-id"
```

### `setKey(String key)`

```java
public void setKey(String key)
```

Validates, trims, and replaces the current key. The input domain and
normalization rules are identical to the constructor: null, empty, and
whitespace-only keys are invalid; leading and trailing `trim()` characters are
removed; case and internal characters are preserved.

The return type is `void`. On success, later `getKey`, `prefix`, and
`localName` calls observe the new normalized key. The current value is not
changed. The operation has no external side effects.

If validation fails, throw `IllegalArgumentException` and leave the previous
key and value unchanged. This failed call must not install a null or empty
key.

```java
Attribute a = new Attribute("old", "value");
a.setKey("  new:key  ");
a.getKey();
// returns "new:key"
a.getValue();
// still returns "value"
```

```java
Attribute a = new Attribute("stable", "value");
try {
    a.setKey("  ");
} catch (IllegalArgumentException expected) {
    // the previous key remains "stable"
}
```

### `getValue()`

```java
public String getValue()
```

Returns the observable value of the entry as a `String`. A non-null stored
value is returned unchanged. A null stored value is exposed as the empty
string `""`.

This method does not mutate the object. It cannot by itself distinguish a
stored empty string from a stored null; use `hasDeclaredValue()` for that
distinction. Repeated calls are deterministic until `setValue` is called.

```java
Attribute present = new Attribute("class", "card");
present.getValue();
// returns "card"

Attribute absent = new Attribute("hidden", null);
absent.getValue();
// returns ""
```

### `hasDeclaredValue()`

```java
public boolean hasDeclaredValue()
```

Reports whether the internal value state is non-null. It returns `true` for a
non-null value, including the empty string, and `false` only when the stored
value is null. The return type is the primitive `boolean`.

The method has no side effects and does not inspect the key. It is the
deterministic way to distinguish these two states:

```java
Attribute empty = new Attribute("data-x", "");
Attribute missing = new Attribute("data-y", null);
empty.hasDeclaredValue();
// true
missing.hasDeclaredValue();
// false
```

### `setValue(String value)`

```java
public String setValue(String value)
```

Replaces the stored value and returns the previous observable value. The
argument may be null. The return type is `String`; if the previous stored
value was null, the returned string is `""`; otherwise it is the previous
value unchanged.

The new value is stored exactly as supplied, including null. Consequently,
`setValue(null)` makes `hasDeclaredValue()` false, while `setValue("")` makes
it true. The method changes only this object and has no external side effect.

```java
Attribute a = new Attribute("title", "before");
String previous = a.setValue("after");
// previous is "before"
a.getValue();
// returns "after"
```

```java
Attribute a = new Attribute("disabled", null);
String previous = a.setValue(null);
// previous is ""
a.setValue("");
// returns ""
a.hasDeclaredValue();
// now returns true
```

### `prefix()`

```java
public String prefix()
```

Examines the current normalized key and returns the substring before its first
colon (`:`). If the key contains no colon, return the empty string. Split only
at the first colon; do not interpret later colons, lowercase text, decode
entities, or resolve an XML namespace.

The return type is `String`, and the method does not mutate the object. A
leading colon produces an empty prefix. A later `setKey` call changes the
result because the method reads the current key.

```java
Attribute a = new Attribute("og:title", "News");
a.prefix();
// returns "og"

Attribute b = new Attribute("title", "News");
b.prefix();
// returns ""
```

```java
Attribute a = new Attribute(":name", "x");
a.prefix();
// returns ""
Attribute b = new Attribute("a:b:c", "x");
b.prefix();
// returns "a"
```

### `localName()`

```java
public String localName()
```

Examines the current normalized key and returns the substring after its first
colon. If the key contains no colon, return the full normalized key. Split
only at the first colon and preserve every later colon in the returned suffix.
Do not lowercase, decode, or perform namespace lookup.

The return type is `String`. The method is deterministic, has no side effects,
and observes the current key after successful `setKey` calls.

```java
Attribute a = new Attribute("og:title", "News");
a.localName();
// returns "title"

Attribute b = new Attribute("title", "News");
b.localName();
// returns "title"
```

```java
new Attribute(":name", "x").localName();
// returns "name"
new Attribute("og:", "x").localName();
// returns ""
new Attribute("a:b:c", "x").localName();
// returns "b:c"
```

### Public API Boundary

The confidently bindable task-specific API is the constructor plus
`getKey`, `setKey`, `getValue`, `hasDeclaredValue`, `setValue`, `prefix`, and
`localName` on `org.jsoup.nodes.Attribute`. Inherited `Map.Entry` default
behavior, `Object.equals`, `Object.hashCode`, `Object.toString`, and any
`clone()` behavior are not confidently bindable requirements for this slice;
do not infer additional semantics from the interface or marker interface.

## Implementation Notes

Keep the implementation compact and instance-local. Two private string fields
for the normalized key and nullable value are sufficient, but the public
contract matters more than a particular field layout. Do not copy source code
from an upstream implementation or add behavior that is not specified here.

Key validation is shared conceptually by construction and mutation. A valid
key is checked before it replaces existing state. This ensures a failed
`setKey` call cannot partially mutate the object. Value mutation is separate:
null is a meaningful state and must not be collapsed into the empty string
internally.

The observable `getValue` and `setValue` contracts deliberately map null to
`""` when returning a value. `hasDeclaredValue` is the separate state query
that exposes whether the stored value was null. Preserve this distinction
through repeated mutation.

Prefix and local-name operations are string views over the current key. Use
the first colon only. For example, these independent checks must hold:

```java
Attribute a = new Attribute("x:y:z", "v");
a.prefix();
// "x"
a.localName();
// "y:z"
```

```java
Attribute a = new Attribute("  :  ", null);
a.getKey();
// ":"
a.prefix();
// ""
a.localName();
// ""
```

```java
Attribute a = new Attribute("Flag", "");
a.hasDeclaredValue();
// true
a.setValue(null);
a.getValue();
// ""
a.hasDeclaredValue();
// false
```

```java
Attribute a = new Attribute("old", "v");
a.setKey("new:key");
a.setValue("w");
// getKey() is "new:key", prefix() is "new", localName() is "key",
// and getValue() is "w"
```

All methods must be deterministic for equal object state and must avoid
iteration, collection ordering, timestamps, randomness, locale-sensitive
conversion, and external resources. The class should compile and run in an
offline verifier process. No command-line interface or additional module is
required for this task.
