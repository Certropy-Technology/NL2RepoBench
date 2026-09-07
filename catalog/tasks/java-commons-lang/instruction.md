## Project Description

Recreate a small, dependency-free Java library named Apache Commons Lang for a
bounded slice of `org.apache.commons.lang3.StringUtils`. The target users are
Java applications that need null-safe predicates, counting, case conversion,
reversal, tokenization, and substring extraction without adding a runtime
dependency. The candidate must build a normal Maven project from an empty
workspace and provide the one public class and the 16 static methods specified
in this document.

The in-scope behavior is the exact `StringUtils` slice listed in the API guide:
null and blank predicates, containment, character and substring counting,
default values, capitalization, uncapitalization, reversal, two split forms,
two substring forms, and left/right extraction. Preserve input ordering,
null-safe results, and the documented boundary behavior. The implementation
must be deterministic and must not rely on locale, wall-clock time, shared
mutable state, filesystem access, a network, reflection-based discovery, or
external libraries.

The out-of-scope surface includes every other Commons Lang class or method,
including array utilities, numeric utilities, builders, reflection helpers,
random utilities, date utilities, pluralization, regex replacement, archive
processing, logging, and deprecated forwarding APIs. Do not create a command
line program, shell integration, web service, plugin, or additional public
package merely to imitate the upstream repository.

Create the following public contract:

* Class: `org.apache.commons.lang3.StringUtils`.
* All listed operations are `public static`; callers do not instantiate the
  utility class or perform an initialization step.
* Inputs are read-only. Returned arrays and strings contain only results of the
  requested call and have deterministic left-to-right ordering.
* Null behavior is method-specific as stated below. Do not replace it with
  `NullPointerException`, a text sentinel, or an unchecked dependency error.

### Natural Language Instruction

Implement the bounded StringUtils API as a single-module Java Maven project.
Use the exact package and class name, keep production code under
`src/main/java/org/apache/commons/lang3/StringUtils.java`, and make the project
compile with the offline JDK/Maven environment described below. The public
methods must accept the declared Java types, return the declared types, and
follow all null, empty, Unicode, separator, negative-index, and length rules.

Do not copy a full upstream checkout. Do not add tests, private verifier code,
network clients, filesystem writes, a CLI, or dependencies that are not part
of the standard JDK. A minimal `pom.xml` is required for Maven metadata and
offline validation; it must not introduce repositories, modules, profiles,
build extensions, or runtime dependencies.

## Supports

### Runtime and installation

Use Temurin JDK `21.0.12+8` on Linux amd64 with Maven `3.9.11`. The package
manager is Maven, but the dependency closure is empty: use only Java SE APIs
available in the JDK. The harness performs offline Maven metadata validation
and compiles the candidate with `javac --release 21`; do not require a Maven
download, a remote repository, or a custom settings file.

The agent, candidate, verifier, Oracle, and controls run with no network. Do
not contact GitHub, Maven Central, DNS, or any external service at runtime.
The project has no runtime dependency and no generated resource that must be
fetched during setup. The fixed platform is Linux amd64 with glibc; do not
make behavior depend on platform-specific path separators or default locale.

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── lang3/
                            └── StringUtils.java
```

`pom.xml` identifies a single Maven project and may contain Java 21 compiler
configuration, but no dependency, repository, profile, module, plugin, or
custom network configuration is needed by this task. The only public entry
point is the static class `org.apache.commons.lang3.StringUtils`; there is no
CLI entry point and no `main` method requirement.

## API Usage Guide

All examples assume:

```java
import org.apache.commons.lang3.StringUtils;
```

The signatures below are exact. `CharSequence` accepts `String` and other
read-only implementations; methods inspect the sequence without mutating it.
The return type of each split operation is `String[]`. Unless a method says
otherwise, no method throws a checked exception.

### `isEmpty`

Signature: `public static boolean isEmpty(CharSequence cs)`.

Return `true` for `null` or a sequence of length zero, and `false` for a
sequence containing a space or any other character. The result depends only
on the sequence length and is deterministic; the argument is not changed.

```java
boolean a = StringUtils.isEmpty(null); // true
boolean b = StringUtils.isEmpty(" ");  // false
```

An empty custom `CharSequence` returns `true`; a one-character sequence,
including `"\0"`, returns `false`. Do not treat whitespace as emptiness.

### `isBlank`

Signature: `public static boolean isBlank(CharSequence cs)`.

Return `true` for `null`, empty input, or input whose characters are all
classified as whitespace by Java's `Character.isWhitespace`. Return `false` as
soon as a non-whitespace character is present. Preserve the input and avoid
locale-dependent classification.

```java
boolean a = StringUtils.isBlank(" \t\n"); // true
boolean b = StringUtils.isBlank(" x ");    // false
```

The empty sequence is the edge case and returns `true`; a string containing a
non-whitespace Unicode character returns `false`. Do not make `isBlank` an
alias for `isEmpty`.

### `contains`

Signature: `public static boolean contains(CharSequence seq, int searchChar)`.

Search `seq` for the requested integer character value using the sequence
search semantics of the Java API. Return `false` for a null or empty sequence
and `true` when the requested value occurs. The method does not alter `seq`.

```java
boolean a = StringUtils.contains("alpha", 'p'); // true
boolean b = StringUtils.contains(null, 'p');     // false
```

Searching an empty sequence is the required edge case and returns `false`.
Do not convert a missing value into an exception or search a different string.

### `countMatches(CharSequence, char)`

Signature: `public static int countMatches(CharSequence str, char ch)`.

Count matching UTF-16 `char` values in `str` from left to right. Return zero
for null or empty input. Every matching code unit is counted, including
repeated adjacent matches; the input and its ordering remain unchanged.

```java
int count = StringUtils.countMatches("banana", 'a'); // 3
int empty = StringUtils.countMatches(null, 'a');     // 0
```

For `"aaa"` and `'a'`, return `3`, not `1`; for a character that does not
occur, return `0`. Do not count Unicode code points as a substitute for the
declared `char` contract.

### `countMatches(CharSequence, CharSequence)`

Signature: `public static int countMatches(CharSequence str, CharSequence sub)`.

Count non-overlapping occurrences of `sub` in `str` from left to right. Return
zero if either argument is null, if either searchable value is empty, or if no
occurrence exists. After a match, continue after the complete matched
substring; overlapping matches are not counted.

```java
int count = StringUtils.countMatches("banana", "na"); // 2
int overlap = StringUtils.countMatches("ababa", "aba"); // 1
```

The null and empty cases are deliberately ordinary results, not exceptions.
For `"aaaa"` and `"aa"`, count two non-overlapping occurrences.

### `defaultString(String)`

Signature: `public static String defaultString(String str)`.

Return the empty string only when `str` is null. Return every non-null value
unchanged, including an empty string and a string containing whitespace. This
method has no state or I/O side effects.

```java
String a = StringUtils.defaultString(null); // ""
String b = StringUtils.defaultString(" ");  // " "
```

The empty string edge case must remain empty. Do not trim, copy into a visible
placeholder, or normalize non-null content.

### `defaultString(String, String)`

Signature: `public static String defaultString(String str, String nullDefault)`.

Return `nullDefault` exactly when `str` is null; otherwise return `str`
unchanged. `nullDefault` may itself be null. Neither argument is modified.

```java
String a = StringUtils.defaultString(null, "fallback"); // "fallback"
String b = StringUtils.defaultString("value", "fallback"); // "value"
```

`defaultString(null, null)` returns null, while
`defaultString("", "fallback")` returns the empty string. Do not apply the
fallback to empty or whitespace-only non-null values.

### `capitalize`

Signature: `public static String capitalize(String str)`.

Return null for null input and the empty string unchanged. Otherwise change
only the first character according to the package's case-conversion contract;
preserve the remaining characters and their order. The result is a new string
value as required by Java string operations and is deterministic without
locale state.

```java
String a = StringUtils.capitalize("cat"); // "Cat"
String b = StringUtils.capitalize("");    // ""
```

An already-capitalized input remains equivalent to its original value. Do not
capitalize every word, trim the string, or change later characters.

### `uncapitalize`

Signature: `public static String uncapitalize(String str)`.

Return null for null input and the empty string unchanged. Otherwise change
only the first character according to the package's case-conversion contract;
preserve all later characters and their order.

```java
String a = StringUtils.uncapitalize("CAT"); // "cAT"
String b = StringUtils.uncapitalize("");    // ""
```

Do not lower-case the complete string or use the process locale. A string whose
first character needs no change remains equivalent to the original value.

### `reverse`

Signature: `public static String reverse(String str)`.

Return null for null input and the empty string unchanged. Reverse the string
using Java `StringBuilder.reverse()` semantics, including preservation of
well-formed UTF-16 surrogate pairs. Do not mutate the original `String`.

```java
String a = StringUtils.reverse("stressed"); // "desserts"
String b = StringUtils.reverse("");         // ""
```

The ordinary case reverses character order; the edge case is empty input.
Supplementary characters must not be split into an invalid surrogate order.

### `split(String)`

Signature: `public static String[] split(String str)`.

Return null for null input and a zero-length array for empty input. Treat Java
whitespace characters as separators, collapse adjacent separators, omit empty
leading and trailing tokens, and preserve the remaining tokens in their
original left-to-right order.

```java
String[] words = StringUtils.split("  red  green\tblue ");
// ["red", "green", "blue"]
String[] none = StringUtils.split(""); // []
```

A whitespace-only string produces a zero-length array. Do not return separator
characters or empty elements between adjacent separators.

### `split(String, char)`

Signature: `public static String[] split(String str, char separatorChar)`.

Return null for null input and a zero-length array for empty input. Use only
the specified `separatorChar` as the separator, collapse adjacent separators,
omit empty edge tokens, and preserve token order.

```java
String[] parts = StringUtils.split("a::b:c", ':'); // ["a", "b", "c"]
String[] none = StringUtils.split("::", ':');      // []
```

Other whitespace remains part of a token when it is not the requested
separator. Do not treat an arbitrary punctuation character as a regular
expression or split on every whitespace character in this overload.

### `substring(String, int)`

Signature: `public static String substring(String str, int start)`.

Return null for null input. A negative `start` is counted from the end of the
string. Clamp an effective start below zero to zero; if the effective start is
beyond the string length, return the empty string. The end boundary is the
string length and the result is deterministic.

```java
String a = StringUtils.substring("abcdef", -3); // "def"
String b = StringUtils.substring("abc", 8);     // ""
```

For an empty non-null string, return the empty string for any start. Do not
throw merely because the index is negative or beyond the end.

### `substring(String, int, int)`

Signature: `public static String substring(String str, int start, int end)`.

Return null for null input. Convert negative bounds to offsets from the end,
clamp effective bounds below zero to zero, clamp `end` above the length to the
length, and use an exclusive end boundary. If the effective start is greater
than the effective end, return the empty string.

```java
String a = StringUtils.substring("abcdef", -4, -1); // "cde"
String b = StringUtils.substring("abcdef", 4, 2);   // ""
```

The empty input edge case returns an empty string for non-null input. Do not
interpret the end as inclusive and do not reject ordinary negative bounds.

### `left`

Signature: `public static String left(String str, int len)`.

Return null for null input. Return the empty string for a negative length,
return the complete string when `len` reaches its length, and otherwise return
the requested left edge. Do not leave a lone UTF-16 surrogate if the boundary
would split a surrogate pair.

```java
String a = StringUtils.left("abcdef", 2); // "ab"
String b = StringUtils.left("abcdef", -1); // ""
```

For an empty string, every length returns the empty string. The input is not
mutated and no filesystem or locale state is consulted.

### `right`

Signature: `public static String right(String str, int len)`.

Return null for null input. Return the empty string for a negative length,
return the complete string when `len` reaches its length, and otherwise return
the requested right edge. Avoid returning a lone UTF-16 surrogate when the
boundary would split a surrogate pair.

```java
String a = StringUtils.right("abcdef", 2); // "ef"
String b = StringUtils.right("abcdef", -1); // ""
```

For an empty string, every length returns the empty string. Preserve the
original order within the selected suffix and do not reverse the result.

## Implementation Notes

Keep the implementation stateless: no static mutable cache, environment probe,
clock read, locale mutation, file write, subprocess, or network request is
allowed. The class may use Java standard-library character and string helpers,
but every public method must remain callable in an offline, dependency-free
JVM. Preserve the declared `CharSequence` inputs and do not require callers to
convert them to a particular concrete implementation.

Keep all public API in `org.apache.commons.lang3.StringUtils`. The Maven
project should compile the package with Java 21 and leave generated build
outputs outside the source layout. There is no command line interface to
implement and no public class besides the specified utility class is required.

Check boundary handling independently for null, empty, whitespace-only,
adjacent separators, repeated substrings, negative indexes, reversed ranges,
lengths larger than the input, and surrogate pairs. Examples of verifiable
combinations include:

```java
StringUtils.isBlank("\t \n");             // true
StringUtils.countMatches("aaaa", "aa");  // 2, non-overlapping
StringUtils.split("::a::b::", ':');       // ["a", "b"]
StringUtils.substring("abcdef", -4, -1);  // "cde"
```

These examples describe observable behavior without prescribing a particular
algorithm. Keep ordinary results and edge results consistent across repeated
calls. Do not widen the API based on unrelated upstream classes, and do not
copy private test cases, verifier protocols, source files, or hidden assertions.
