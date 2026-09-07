## Project Description

Create a small, offline Java Maven project that recreates the bounded public
arithmetic and collection-query contract of Apache Commons JEXL. The project is
for callers that need deterministic conversion of ordinary Java values,
identifier parsing, size queries, emptiness checks, and character-prefix
checks.

The public type is `org.apache.commons.jexl3.JexlArithmetic`. It must be
available from the normal Maven source layout at
`src/main/java/org/apache/commons/jexl3/JexlArithmetic.java`. A caller creates
one arithmetic object with a strictness flag and then invokes the documented
instance methods, or invokes the static identifier helper on the class.

The input boundary is ordinary Java objects supplied directly to these
methods: `null`, booleans, numeric wrappers, characters, strings and other
`CharSequence` values, arrays, collections, maps, and ordinary objects. The
output boundary is a Java primitive or wrapper value, a string, or a nullable
wrapper as specified below. Methods must not mutate caller-owned objects.

This is a bounded compatibility task, not a complete expression engine. Do
not implement a parser, evaluator, namespace system, introspector, sandbox,
logging subsystem, expression AST, filesystem integration, database, network
client, or additional Commons JEXL modules. Do not add runtime dependencies.

The project must compile with JDK 21 and Maven 3.9.11 without network access.
Keep the class in the exact package above; package or class renaming makes the
public contract unavailable to callers.

## Supports

### Natural Language Instruction

Implement a single-module Maven project named `commons-jexl` containing the
public class `org.apache.commons.jexl3.JexlArithmetic`. Implement all public
signatures in the API Usage Guide and preserve the stated null, numeric,
string, container, ordering, and exception behavior.

The implementation must provide these capabilities:

1. Coerce booleans, numbers, characters, strings, and null values to boolean,
   double, integer, long, and string results.
2. Parse a decimal identifier into an `Integer` only when it satisfies the
   documented grammar and length bound.
3. Report the size of character sequences, arrays, collections, and maps, with
   the documented fallback for null and unsupported objects.
4. Determine whether a value is empty and compare character sequences using a
   prefix operation with its documented nullable result.

Use only the JDK classes needed for these behaviors, including
`java.lang.reflect.Array` and the relevant `java.util` interfaces. The strict
constructor argument is object state and must affect null coercion as
documented; it must not be ignored or replaced by a global setting.

### Environment Configuration

Use the following fixed environment:

```text
Language: Java
JDK: Temurin 21.0.12+8
Build tool: Maven 3.9.11
Platform: Linux amd64 with glibc
Runtime dependencies: none
Network: unavailable during agent, candidate, verifier, Oracle, and control runs
```

The root `pom.xml` is metadata for a single jar module. It must use a normal
Maven coordinate and may not declare dependencies, plugins, profiles,
repositories, modules, or custom extensions. A minimal offline validation
command is `mvn --offline validate`; compilation must be possible with the
JDK 21 compiler and no downloaded library.

### Project Directory Structure

The workspace created by the implementation must have this public structure:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── jexl3/
                            └── JexlArithmetic.java
```

Do not require a CLI or an additional entry point. There is no network-backed
configuration and no application-global data file. The only public entry is
the class and methods documented below.

## API Usage Guide

### Public class and constructor

#### `org.apache.commons.jexl3.JexlArithmetic`

Import path:

```java
import org.apache.commons.jexl3.JexlArithmetic;
```

Public constructor:

```java
public JexlArithmetic(boolean strict)
```

The `strict` parameter selects null handling for the conversion methods. Store
the value per object. Constructing `new JexlArithmetic(false)` enables the
lenient null behavior described below; constructing `new
JexlArithmetic(true)` makes null conversion fail with `ArithmeticException`.
Construction returns a new object, has no I/O or global side effect, and is
deterministic for the same argument.

Normal example:

```java
JexlArithmetic arithmetic = new JexlArithmetic(false);
```

Boundary example: `new JexlArithmetic(true).toInteger(null)` must throw an
`ArithmeticException`, while the same call on a lenient instance returns `0`.

### `toBoolean`

Import and signature:

```java
import org.apache.commons.jexl3.JexlArithmetic;

public boolean toBoolean(Object value)
```

The input may be null, a `Boolean`, any `Number`, a `CharSequence`, or another
object. Return a primitive boolean and do not mutate the input. For null, a
lenient instance returns `false` and a strict instance throws
`ArithmeticException`. A Boolean returns its value. A numeric value returns
false for numeric zero or `NaN`, and true otherwise. A character sequence is
false when it is empty or exactly equal to the lowercase text `"false"`; all
other non-empty character sequences are true. Any other non-null object is
true.

The result is deterministic and has no state, filesystem, environment, or
network side effect.

Normal example:

```java
new JexlArithmetic(false).toBoolean("ready"); // true
```

Edge examples: `toBoolean(0)` and `toBoolean(Double.NaN)` return `false`;
`toBoolean("false")` returns `false`; `toBoolean("False")` returns `true`.

### `toDouble`

Signature:

```java
public double toDouble(Object value)
```

Accept null, `Number`, `Boolean`, `Character`, and `CharSequence` inputs.
Number values use `doubleValue()`. A Boolean maps to `1.0` or `0.0`. A
Character maps to its numeric character value. A non-empty character sequence
is parsed as a Java decimal double. An empty character sequence returns
`Double.NaN`.

A lenient null returns `0.0`; a strict null throws `ArithmeticException`.
Unsupported non-null objects and malformed numeric character sequences throw
`ArithmeticException` (the implementation may use an internal unchecked
numeric failure, but callers observe `ArithmeticException`). The method does
not mutate input and does not access external state.

Normal example:

```java
double value = new JexlArithmetic(false).toDouble("12.5"); // 12.5
```

Edge examples: `toDouble("")` returns `Double.NaN`; `toDouble(true)` returns
`1.0`; `toDouble("not-a-number")` throws `ArithmeticException`.

### `toInteger`

Signature:

```java
public int toInteger(Object value)
```

Accept null, `Number`, `Boolean`, `Character`, and `CharSequence` inputs.
Number values use `intValue()`, including the ordinary Java narrowing behavior
for fractional numeric wrapper inputs. A Boolean maps to `1` or `0`. A
Character maps to its numeric character value. A character sequence is first
interpreted as a decimal double and must represent an integral value in the
`int` range.

A lenient null and an empty string return `0`; a strict null throws
`ArithmeticException`. A fractional or out-of-range numeric string, malformed
numeric string, or unsupported object throws `ArithmeticException`. The
method is deterministic and does not mutate its input.

Normal example:

```java
int count = new JexlArithmetic(false).toInteger("12"); // 12
```

Edge examples: `toInteger(1.9d)` follows `Number.intValue()` and returns `1`,
while `toInteger("1.5")` throws `ArithmeticException`; `toInteger("")`
returns `0`.

### `toLong`

Signature:

```java
public long toLong(Object value)
```

Accept null, `Number`, `Boolean`, `Character`, and `CharSequence` inputs.
Number values use `longValue()`. A Boolean maps to `1L` or `0L`. A Character
maps to its numeric character value. A character sequence is parsed as a
decimal double and must represent an integral value before conversion.

A lenient null and an empty string return `0L`; a strict null throws
`ArithmeticException`. Malformed or fractional numeric strings and unsupported
objects throw `ArithmeticException`. Numeric wrapper narrowing follows the
ordinary Java `longValue()` behavior. There are no side effects.

Normal example:

```java
long value = new JexlArithmetic(false).toLong("3.0"); // 3L
```

Edge example: `toLong("3.5")` throws `ArithmeticException`, while
`toLong(false)` returns `0L`.

### `toString`

Signature:

```java
public String toString(Object value)
```

Accept any object, including null. A lenient null returns the empty string; a
strict null throws `ArithmeticException`. A `Double` containing `NaN` returns
the empty string. Every other non-null value returns its ordinary
`toString()` representation. The result is a new or immutable string value;
the input is not changed and no external state is accessed.

Normal example:

```java
String text = new JexlArithmetic(false).toString(42); // "42"
```

Edge examples: `toString(Double.NaN)` returns `""`; `toString(null)` returns
`""` only on a lenient instance.

### `parseIdentifier`

Static signature:

```java
public static Integer parseIdentifier(Object value)
```

The method accepts a `Number` or a `CharSequence`; other values return null.
For a Number, return `intValue()`. For a character sequence, accept exactly the
decimal grammar `0` or a non-zero digit followed by zero or more digits. The
sequence must be non-empty and no longer than ten characters. Return the
corresponding `Integer` on success.

Return null for an empty sequence, a leading-zero form such as `"01"`, a
sign, decimal point, whitespace, non-digit, or a sequence outside the length
bound. If the accepted text cannot fit `Integer.valueOf`, return null rather
than leaking a parsing failure. This pure static method has no side effects
and is deterministic.

Normal example:

```java
Integer id = JexlArithmetic.parseIdentifier("7"); // 7
```

Edge examples: `parseIdentifier("0")` returns `0`, while
`parseIdentifier("01")`, `parseIdentifier("+1")`, and
`parseIdentifier("")` return null.

### `size(Object)`

Signature:

```java
public Integer size(Object value)
```

Return the size of a character sequence, Java array, `Collection<?>`, or
`Map<?, ?>`. Character sequences use `length()`, arrays use reflective array
length, collections use `size()`, and maps use `size()`. Null returns zero.
For a non-null unsupported object, return one. The returned wrapper is
deterministic and the supplied container is not mutated or reordered.

Normal example:

```java
Integer count = new JexlArithmetic(false).size(java.util.List.of("x", "y"));
// 2
```

Edge examples: `size(new int[0])` returns `0`; `size(new Object())` returns
`1`; `size(null)` returns `0`.

### `size(Object, Integer)`

Signature:

```java
public Integer size(Object value, Integer defaultValue)
```

Use the same character-sequence, array, collection, and map rules as the
one-argument method. For null, return `defaultValue`. For an unsupported
non-null object, also return `defaultValue`. The default may itself be null;
the method then returns null for those two fallback cases. Supported container
sizes never use the default. No input is mutated.

Normal example:

```java
Integer fallback = new JexlArithmetic(false).size(new Object(), 9); // 9
```

Edge example: `size(null, null)` returns null, while `size("abc", 9)` returns
`3`, because a supported value takes precedence over the default.

### `empty`

Signature:

```java
public Boolean empty(Object value)
```

Return true for null, an empty `CharSequence`, a zero-length array, an empty
collection, or an empty map. Return false for non-empty supported values and
for an unsupported non-null object. Numeric values are unsupported for size
purposes and therefore are not considered empty. The method is a read-only
query and does not mutate or iterate beyond what the relevant size operation
requires.

Normal example:

```java
Boolean result = new JexlArithmetic(false).empty(java.util.List.of()); // true
```

Edge examples: `empty("")` and `empty(new int[0])` return true;
`empty(0)` and `empty(new Object())` return false.

### `startsWith`

Signature:

```java
public Boolean startsWith(Object left, Object right)
```

If both arguments are null, return true. If exactly one argument is null,
return false. If the left argument is not a `CharSequence`, return null. For a
non-null `CharSequence` left argument, convert both non-null arguments with
the class's string conversion behavior and return whether the left text starts
with the right text. The right argument may therefore be another
`CharSequence` or another non-null object with a meaningful `toString()`.

The operation is deterministic, does not mutate either argument, and has no
filesystem or network side effect. A strict arithmetic object only affects
the null behavior if its conversion helper is reached; the explicit two-null
and one-null results above take precedence.

Normal example:

```java
Boolean prefix = new JexlArithmetic(false).startsWith("commons", "com");
// true
```

Edge examples: `startsWith(null, null)` returns true;
`startsWith("commons", "x")` returns false; `startsWith(12, "1")` returns
null.

## Implementation Notes

Keep the package declaration exactly `org.apache.commons.jexl3` and expose the
class as public. All listed methods must remain public with the exact
parameter and return types. Do not add overloads that change how a caller's
null or numeric value is resolved.

Use Java's standard `Collection`, `Map`, `CharSequence`, and reflective array
contracts. A Java array may be an object array or a primitive array; do not
cast only to `Object[]`. Query operations must preserve the supplied
container and must not sort, remove, or replace its elements.

Conversion behavior must be independent of locale, current time, process
environment, default charset, filesystem contents, and network availability.
Repeated calls with equal inputs and the same strictness state must produce
the same results or the same documented exception type.

Use unchecked `ArithmeticException` for invalid conversion inputs visible to
callers. Do not print diagnostics, swallow malformed input, or substitute a
silent fallback where the API specifies an exception. Nullable query results
such as `size(value, defaultValue)` and `startsWith` must remain nullable.

The following small checks illustrate the intended composition without
prescribing an implementation algorithm:

```java
JexlArithmetic a = new JexlArithmetic(false);
assert a.toBoolean("ready");
assert a.toInteger("12") == 12;
assert Double.isNaN(a.toDouble(""));
assert JexlArithmetic.parseIdentifier("7").equals(7);
assert a.size(new int[] {1, 2, 3}) == 3;
assert a.empty(java.util.Map.of());
assert a.startsWith("commons-jexl", "commons");
```

Additional boundary checks should cover strict and lenient null construction,
`Double.NaN`, Boolean conversion, numeric wrapper narrowing, empty and
fractional numeric strings, leading-zero identifiers, ten-character
identifier limits, primitive arrays, empty and non-empty collections/maps,
unsupported objects, both-null prefixes, one-null prefixes, and a non-string
left prefix operand.

Build and run entirely offline. The root `pom.xml` must remain a simple
single-module metadata file, and the implementation must not fetch or require
Apache Commons JEXL or any other external artifact at runtime. Keep all
behavior inside the documented class so a clean workspace containing only the
shown files is sufficient to compile the project.
