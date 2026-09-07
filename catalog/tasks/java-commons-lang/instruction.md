# Introduction and Goals of the Apache Commons Lang Project

Apache Commons Lang supplies dependency-free utilities for common Java language
operations. This task focuses on a bounded, null-safe slice of
`org.apache.commons.lang3.StringUtils` for predicates, counting, case changes,
reversal, splitting, and bounded substring extraction. Implement it as a
normal single-module Maven project rather than copying the upstream repository.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Apache Commons Lang that provides the
public `StringUtils` methods documented below. The required class is
`org.apache.commons.lang3.StringUtils`, and all methods are static. Keep the
implementation under `src/main/java/org/apache/commons/lang3/StringUtils.java`.
Do not add external runtime dependencies, network clients, filesystem behavior,
or command-line entry points.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # compilation and execution
Maven 3.9.11                # offline project metadata validation
Linux amd64                 # fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # agent and verifier execution are offline
```

The POM is metadata only. It must not contain dependencies, plugins, profiles,
repositories, modules, build extensions, or custom Maven settings intended to
alter verification.

## Apache Commons Lang Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/lang3/StringUtils.java
```

Use the exact package and public class name. `StringUtils` is a stateless
utility class; calls do not mutate shared state and have deterministic results.

## API Usage Guide

### Core APIs

All signatures below are exact. `CharSequence` arguments may be ordinary
`String` values or another implementation; operations inspect their character
sequence contents without mutating them.

#### Predicates and containment

```java
static boolean isEmpty(CharSequence cs)
static boolean isBlank(CharSequence cs)
static boolean contains(CharSequence seq, int searchChar)
```

`isEmpty` returns `true` for `null` or length zero, and `false` for a single
space. `isBlank` returns `true` for `null`, empty input, or input whose every
UTF-16 code unit satisfies `Character.isWhitespace`; it returns `false` as soon
as a non-whitespace code unit appears. `contains` returns `false` for null or
empty input and otherwise searches for the requested Unicode code point, with
the same semantics as `CharSequence`/`String` index search.

```java
StringUtils.isEmpty(null);       // true
StringUtils.isEmpty(" ");         // false
StringUtils.isBlank(" \t");       // true
StringUtils.contains("alpha", 'p'); // true
```

#### Counting

```java
static int countMatches(CharSequence str, char ch)
static int countMatches(CharSequence str, CharSequence sub)
```

The character overload counts every matching UTF-16 code unit. The substring
overload counts non-overlapping occurrences from left to right: after a match,
the next search starts after the complete matched substring. Either null input,
or an empty substring, produces zero; no exception or overlap counting is
introduced.

```java
StringUtils.countMatches("banana", 'a');       // 3
StringUtils.countMatches("ababa", "aba");     // 1
StringUtils.countMatches(null, "a");            // 0
```

#### Null defaults

```java
static String defaultString(String str)
static String defaultString(String str, String nullDefault)
```

The one-argument overload changes only null into `""`; a non-null value is
returned unchanged. The two-argument overload returns `nullDefault` only when
`str` is null, and otherwise returns `str`, including when either value is
empty. `nullDefault` itself may be null.

#### Case and reversal

```java
static String capitalize(String str)
static String uncapitalize(String str)
static String reverse(String str)
```

All three return null for null input and return the empty string unchanged.
`capitalize` changes only the first Unicode code point to title case;
`uncapitalize` changes only the first code point to lower case; remaining code
points preserve their original order and case. `reverse` follows
`StringBuilder.reverse()` semantics, including its handling of UTF-16 surrogate
pairs. A string that is already in the requested case may be returned with the
same value.

```java
StringUtils.capitalize("cat");    // "Cat"
StringUtils.uncapitalize("CAT");  // "cAT"
StringUtils.reverse("stressed"); // "desserts"
```

#### Splitting

```java
static String[] split(String str)
static String[] split(String str, char separatorChar)
```

Both overloads return null for null input and a zero-length array for empty
input. The no-separator overload treats `Character.isWhitespace` characters
as separators, collapses adjacent separators, and omits leading/trailing
separators. The character overload uses only the specified character as a
separator, also collapses adjacent separators and omits empty edge tokens.
Returned tokens preserve their left-to-right order and do not include the
separator.

```java
StringUtils.split("  red  green\tblue "); // ["red", "green", "blue"]
StringUtils.split("a::b:c", ':');          // ["a", "b", "c"]
```

#### Substring and edge extraction

```java
static String substring(String str, int start)
static String substring(String str, int start, int end)
static String left(String str, int len)
static String right(String str, int len)
```

These methods are null-safe and return null for null input. `substring(str,
start)` treats a negative start as an offset from the end, clamps a still-
negative start to zero, and returns `""` when start is beyond the end.
`substring(str,start,end)` treats negative bounds as offsets from the end,
clamps end above the length and both bounds below zero, and returns `""` if the
effective start is greater than the effective end; the end is exclusive.
`left` and `right` return `""` for negative lengths, return the whole string
when the requested length reaches the string length, and otherwise return the
requested edge without leaving a lone UTF-16 surrogate when a cut would split
a surrogate pair.

```java
StringUtils.substring("abcdef", -3);       // "def"
StringUtils.substring("abcdef", -4, -1);  // "cde"
StringUtils.left("abcdef", 2);             // "ab"
StringUtils.right("abcdef", 2);            // "ef"
```

### Actual Usage Modes

Use static calls through `StringUtils`; no object construction or initialization
sequence is required. A Maven project with only the standard library must
compile and run offline. Preserve null return values for null-safe methods and
preserve token order for all split operations.

### Supported Function Types

The supported slice consists only of the 16 exact methods listed above. Archive
processing, reflection helpers, random generators, pluralization, regex
replacement, `ArrayUtils`, and all other Commons Lang classes are outside this
task and need not be implemented.

### Error Handling

Do not replace null-safe behavior with `NullPointerException`, silently coerce
null to a visible text token, or add checked exceptions. Invalid or negative
lengths follow the per-method rules above. Inputs are read-only and no method
may write files, access the network, depend on locale/time, or mutate global
state.

## Detailed Implementation Nodes of Functions

### Node 1: Null-safe predicates and search

Implement null and empty checks before reading characters. `isBlank` uses Java
whitespace classification, while `contains` searches the requested code point
without changing the source sequence.

### Node 2: Deterministic counting

Count character matches one UTF-16 code unit at a time. Count substring matches
left-to-right without overlap and return zero for null or empty search input.

### Node 3: Default and case operations

Default methods preserve non-null references. Case methods change only the first
code point and return null/empty values unchanged; reverse uses Java string
builder behavior so supplementary characters remain well formed.

### Node 4: Tokenization

Split methods collapse runs of separators, omit empty edge tokens, and preserve
the order and exact text of non-separator runs. Null remains null and empty input
produces an empty array.

### Node 5: Bounded extraction

Apply negative-index normalization and clamping exactly as documented. End
positions are exclusive. Edge extraction must avoid cutting a surrogate pair.

### Node 6: Packaging and determinism

Use the exact package/class/method signatures and standard Maven source layout.
The project must compile with `javac --release 21` and validate with Maven in a
no-network environment without third-party runtime artifacts.
