# Introduction and Goals of the Commons JEXL Project

Apache Commons JEXL provides an embeddable expression language and the
`JexlArithmetic` class that defines coercion and collection-query behavior.
This task selects a deterministic, dependency-free slice of that public class.
Implement it as a normal single-module Maven project.

## Natural Language Instruction (Prompt)

Create a Java Maven project named Commons JEXL implementing
`org.apache.commons.jexl3.JexlArithmetic`. The project must provide the public
constructors and methods listed below, under the normal `src/main/java` layout.
Do not add a database, network client, expression parser, external dependency,
Maven plugin, or candidate-controlled test command.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compilation and execution
Maven 3.9.11                # offline metadata validation
Linux amd64 with glibc      # fixed platform
Runtime dependencies: none  # only java.lang, java.util, java.lang.reflect
Network access: unavailable # agent, candidate, verifier, Oracle, controls
```

The candidate `pom.xml` is metadata only. It may not declare dependencies,
plugins, profiles, repositories, modules, or custom extensions.

## Commons JEXL Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/jexl3/JexlArithmetic.java
```

Only the public type above is in this contract. Other JEXL engine types,
introspection, logging, parser, and expression evaluation are out of scope.

## API Usage Guide

### Core APIs

Import and construct the arithmetic object:

```java
import org.apache.commons.jexl3.JexlArithmetic;
JexlArithmetic arithmetic = new JexlArithmetic(false);
```

Required signatures:

```java
JexlArithmetic(boolean strict)
boolean toBoolean(Object value)
double toDouble(Object value)
int toInteger(Object value)
long toLong(Object value)
String toString(Object value)
static Integer parseIdentifier(Object value)
Integer size(Object value)
Integer size(Object value, Integer defaultValue)
Boolean empty(Object value)
Boolean startsWith(Object left, Object right)
```

`strict` is retained as construction state. This task invokes the conversion
methods with `false`; null conversion therefore yields false, `0.0`, `0`, `0L`,
or the empty string as appropriate. Numeric wrappers use their ordinary Java
numeric values. `Boolean` converts to 1/0 for numeric methods. A `String` is
parsed as a decimal number; an empty string converts to `NaN` for `toDouble`
and to zero for integral methods. `toBoolean` treats null, false, numeric zero,
`NaN`, and the empty string as false; other non-null values are true.

`toString(Double.NaN)` returns `""`; other values use their ordinary
`String.valueOf` representation, with lenient null returning `""`.

`parseIdentifier` accepts a number (returning `intValue`) or a decimal
character sequence matching `0` or a non-zero digit followed by digits. It
returns null for empty strings, leading-zero forms such as `"01"`, signs,
non-digits, and strings longer than ten characters.

`size` returns the length of a `CharSequence`, array length, collection size,
or map size. The one-argument form returns zero for null and one for an
otherwise unrecognized non-null object. The two-argument form returns the
provided default for an unrecognized object. `empty` is true for null, empty
strings, zero-length arrays, empty collections, and empty maps; it is false
for non-empty values and non-empty numbers.

`startsWith` compares two character sequences after string conversion. Two
null values return true, exactly one null returns false, and unsupported
non-character left values return null.

### Actual Usage Modes

```java
JexlArithmetic a = new JexlArithmetic(false);
a.toInteger("12");                 // 12
a.toBoolean("ready");              // true
a.toString(Double.NaN);             // ""
JexlArithmetic.parseIdentifier("7"); // 7
a.size(java.util.List.of("x"));    // 1
a.empty("");                       // true
a.startsWith("commons", "com");   // true
```

### Supported Function Types

The supported functions are primitive coercion, identifier validation, size
queries, emptiness checks, and string-prefix checks. Arithmetic operators,
expression parsing/evaluation, namespace resolution, logging, sandboxing,
reflection, and filesystem behavior are outside this task.

### Error Handling

Malformed numeric strings raise `ArithmeticException` (the upstream public
coercion contract uses its `CoercionException` subtype). Fractional strings
passed to integral methods raise `ArithmeticException`; integral strings are
accepted. Null follows the lenient behavior above. Do not silently accept
malformed identifiers or invent fallback values. Collection and array queries
must preserve Java ordering and sizes.

## Detailed Implementation Nodes of Functions

### Node 1: Primitive Coercion

Implement the exact public conversion signatures and preserve boolean,
numeric, character, string, `NaN`, and lenient-null behavior.

### Node 2: Identifier Validation

Validate the decimal grammar `0|[1-9][0-9]*`, enforce the ten-character
bound, and return an `Integer` or null deterministically.

### Node 3: Size and Emptiness

Handle strings, arrays, collections, maps, null, and default values without
mutating the supplied object.

### Node 4: Prefix Predicate

Preserve the null truth table and perform deterministic `startsWith` behavior
for character sequences.

### Node 5: Exceptions and State

Retain constructor strictness as object state. Propagate coercion failures as
`ArithmeticException`; do not print diagnostics or access external state.

### Node 6: Offline Maven Layout

Compile with Java 21 in a single-module project, use no runtime dependencies,
and leave all tests and grading to the separate verifier.

### Node 7: Fixed Verification Contract

The verifier collects exactly sixteen positive leaves covering conversions,
identifier grammar, size/default behavior, emptiness, prefix behavior, and
numeric error handling. Every leaf is traceable to Nodes 1-4 and the examples
above; candidate code cannot write the JUnit report, collection, or reward.

### Node 8: Boundaries

Cover null, empty strings, `NaN`, booleans, zero, fractional numeric input,
leading-zero identifiers, empty and non-empty containers, and both-null and
one-null prefix comparisons. Do not add behavior outside this bounded API.
