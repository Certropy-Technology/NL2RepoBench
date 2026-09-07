## Project Description

Apache Commons Validator contains small, reusable validation components for Java
applications. This task asks you to recreate the bounded, dependency-free
regular-expression validator used by callers that need to accept or reject a
complete text value and optionally retrieve its capturing groups.

The deliverable is a single Maven project rooted at `workspace/`. Its public
library type is `org.apache.commons.validator.routines.RegexValidator`. The
type owns a fixed, ordered collection of compiled JDK regular expressions and
provides deterministic validation, group extraction, group aggregation, and a
human-readable representation of the configured expressions.

The supported boundary is intentionally small. Implement the public
`RegexValidator` constructors and the public methods documented in the API
section below. Do not add image, e-mail, URL, domain, credit-card, locale,
filesystem, network, servlet, or command-line validation features. Do not add a
CLI, service, database, persistent store, or network client.

### Natural Language Instruction

Create a standard single-module Java Maven project named Apache Commons
Validator. Place the implementation at
`src/main/java/org/apache/commons/validator/routines/RegexValidator.java` and
use exactly the package shown by that path. The project must compile on the
declared JDK with Maven offline.

The implementation must provide these capabilities:

1. Construct a validator from one expression or an ordered array of
   expressions, with optional case-sensitive or case-insensitive matching.
2. Validate complete input strings, returning a boolean and never accepting a
   prefix or substring merely because it matches a pattern fragment.
3. Return capturing groups from the first expression that completely matches,
   preserving group order and null values for groups that did not participate.
4. Aggregate participating groups into a deterministic string and expose a
   defensive copy of the compiled pattern array.
5. Render the original expression order in a stable `toString()` value.

Keep the public API compatible with the fully qualified names and signatures
below. Public behavior must be deterministic for the same constructor inputs
and method arguments. The implementation may use `java.util.regex.Pattern`,
`java.util.regex.Matcher`, and other Java Platform classes, but it must not
require a runtime dependency from Maven Central or any other external source.

The candidate project is judged as a library. A normal `pom.xml` is required
for Maven project metadata and compilation, but it must not add repositories,
modules, profiles, plugins, extensions, dependency downloads, or custom Maven
settings that alter verification. The verifier supplies its own harness; do not
create a verifier, test protocol, or grader-facing entry point in the project.

## Supports

### Runtime and Build Configuration

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64`, and glibc. The
project must be a single Maven module with Java sources under `src/main/java`.
Compilation and execution occur offline. The implementation's dependency
closure is the JDK only; do not declare third-party dependencies.

The candidate must work with commands equivalent to:

```text
mvn --offline validate
mvn --offline test
```

The verification environment may compile the source directly with
`javac --release 21`, so do not rely on Maven-generated sources or generated
resources. Do not inspect, download, or contact GitHub, Maven Central, DNS, or
any external service at agent, candidate, verifier, Oracle, or control runtime.

### Project Directory Structure

Create the following public project structure. `workspace/` is the project
root, not a package name to invent in Java source.

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── validator/
                            └── routines/
                                └── RegexValidator.java
```

The `pom.xml` should identify the project and configure Java 21 compilation
without introducing a runtime library. Do not add public classes in a second
package, and do not move `RegexValidator` to a default or shortened package.
No CLI entry point is required or supported for this task.

### Dependency and Side-Effect Boundary

`RegexValidator` is an in-memory value-like object. It may compile patterns
during construction and retain them for later calls. It must not read or write
files, consult environment variables, change the process working directory,
start threads or processes, open sockets, use reflection to load remote code,
or mutate caller-owned arrays.

## API Usage Guide

The following is the complete supported public API for this task. The full
package path is part of each contract. Do not add overloads whose behavior is
not described here merely to broaden the surface.

### Type: `org.apache.commons.validator.routines.RegexValidator`

Import the type with:

```java
import org.apache.commons.validator.routines.RegexValidator;
```

The object stores the expressions in constructor order. Calls on one instance
must observe that same order, and a caller must not be able to change the
stored configuration by mutating an array passed to construction or returned by
`getPatterns()`.

### `public RegexValidator(String regex)`

This constructor accepts one non-null, non-empty regular-expression string and
compiles it with case-sensitive matching. The expression is interpreted by the
JDK regular-expression engine; anchors, character classes, quantifiers,
capturing groups, and other supported Java syntax retain their normal meaning.

The constructor returns a new `RegexValidator` object and has no external side
effect. It must reject a null or empty expression with
`IllegalArgumentException`. If the expression is non-empty but not valid Java
regular-expression syntax, the JDK `PatternSyntaxException` may propagate as a
runtime exception. Do not silently repair, skip, or reorder an invalid
expression.

Normal example:

```java
RegexValidator ids = new RegexValidator("^item-[0-9]+$");
```

Edge example:

```java
new RegexValidator(""); // throws IllegalArgumentException
```

### `public RegexValidator(String... regexs)`

This varargs constructor accepts one or more non-null, non-empty expressions.
It is also callable with a `String[]`; the expressions are compiled in the
array's existing order using case-sensitive matching. The validator must make
its own stable representation of the caller's input, so later changes to the
array passed to the constructor cannot change validation results or
`toString()`.

Passing no expressions, a null array, a null element, or an empty element is an
invalid input and must produce `IllegalArgumentException`. A syntactically
invalid non-empty expression may produce the JDK `PatternSyntaxException`.
There is no file, network, process, or global-state side effect.

Normal example:

```java
RegexValidator names = new RegexValidator(new String[] {"cat", "dog"});
boolean accepted = names.isValid("dog"); // true
```

Edge example:

```java
new RegexValidator(new String[0]); // throws IllegalArgumentException
```

### `public RegexValidator(String regex, boolean caseSensitive)`

This constructor accepts one non-null, non-empty expression and a matching-mode
flag. When `caseSensitive` is `true`, matching uses the normal case-sensitive
JDK behavior. When it is `false`, matching uses the JDK case-insensitive flag.
The expression remains one ordered pattern in the validator.

Null or empty expressions must produce `IllegalArgumentException`. Invalid
regular-expression syntax may propagate `PatternSyntaxException`. The boolean
flag affects matching only; it does not rewrite the expression text returned by
`toString()`.

Normal example:

```java
RegexValidator word = new RegexValidator("hello", false);
word.isValid("HeLLo"); // true
```

Edge example:

```java
new RegexValidator(null, false); // throws IllegalArgumentException
```

### `public RegexValidator(String[] regexs, boolean caseSensitive)`

This constructor accepts a non-null array containing at least one non-null,
non-empty expression and a matching-mode flag. It compiles every expression in
the supplied order. `caseSensitive == true` selects case-sensitive matching;
`false` selects case-insensitive matching for every compiled pattern.

Reject a null array, an empty array, a null element, or an empty element with
`IllegalArgumentException`. Preserve all valid expressions and their order. A
bad non-empty Java regular expression may throw `PatternSyntaxException`.
Copy input configuration as needed so that later caller mutation is harmless.

Normal example:

```java
RegexValidator words = new RegexValidator(
    new String[] {"cat", "dog"}, false);
words.isValid("DOG"); // true
```

Edge example:

```java
new RegexValidator(new String[] {"ok", ""}, true);
// throws IllegalArgumentException
```

### `public java.util.regex.Pattern[] getPatterns()`

Return the compiled patterns in exactly the order supplied to the constructor.
The return type is a new array on each call. Its elements are the corresponding
immutable JDK `Pattern` objects; replacing an element in the returned array
must not change this validator's later behavior.

The method accepts no arguments, returns a non-null array, and has no external
side effect. The array length equals the number of configured expressions. A
caller may inspect `pattern.pattern()` and `pattern.flags()` using the standard
JDK API, but must not depend on a custom subclass or a reordered result.

Normal example:

```java
RegexValidator validator = new RegexValidator("cat", "dog");
Pattern[] patterns = validator.getPatterns();
int count = patterns.length; // 2
```

Edge example:

```java
Pattern[] copy = validator.getPatterns();
copy[0] = Pattern.compile("never");
validator.isValid("cat"); // remains true
```

### `public boolean isValid(String value)`

Test whether `value` is accepted by at least one configured expression. Each
expression must match the complete input, equivalent to applying the JDK
matcher operation that requires the entire region to match. A prefix or
substring match is not sufficient.

Return `false` when `value` is null. For a non-null value, evaluate patterns in
constructor order and return `true` at the first complete match; return
`false` only when no pattern completely matches. The method does not mutate the
validator and has no filesystem, network, or process side effect.

Normal example:

```java
RegexValidator id = new RegexValidator("^id:(\\d+)$");
id.isValid("id:17"); // true
```

Edge example:

```java
id.isValid("prefix-id:17"); // false
id.isValid(null);            // false
```

### `public String[] match(String value)`

Find the first configured expression that completely matches `value` and
return its capturing groups. Exclude group zero, which represents the complete
match. Return groups one through `groupCount()` in their source order.

Return `null` when `value` is null or when no configured expression completely
matches. If the selected expression has no capturing groups, return a non-null
empty array. If an optional group did not participate, preserve that position
with a null array element. Select the first matching expression in constructor
order, and do not combine groups from different expressions.

Normal example:

```java
RegexValidator id = new RegexValidator("(id):(\\d+)");
String[] groups = id.match("id:17");
// groups is {"id", "17"}
```

Edge example:

```java
String[] groups = new RegexValidator("(a)?b").match("b");
// groups is a one-element array containing null
```

### `public String validate(String value)`

Find the first complete match in constructor order and concatenate its
participating capturing groups from left to right. Do not include group zero
unless the expression also declares it as an ordinary capturing group. A null
capturing-group value is omitted from the concatenation.

Return `null` when `value` is null or no configured expression completely
matches. For a selected expression with one optional group that did not
participate, the result is the empty string. For an expression with no groups,
the successful result is also an empty string. The method is deterministic and
does not mutate the validator.

Normal example:

```java
RegexValidator id = new RegexValidator("(item)-(\\d+)");
id.validate("item-42"); // "item42"
```

Edge example:

```java
new RegexValidator("(a)?b").validate("b"); // ""
new RegexValidator("item").validate("other"); // null
```

### `public String toString()`

Return a stable textual description containing the original pattern text in
constructor order. The representation starts with `RegexValidator{`, places
commas between pattern texts without spaces after those commas, and ends with
`}`. It must not depend on object identity, hash codes, locale, filesystem
state, or iteration over an unordered collection.

Normal example:

```java
new RegexValidator("cat", "dog").toString();
// "RegexValidator{cat,dog}"
```

Edge example:

```java
new RegexValidator("^x$").toString(); // "RegexValidator{^x$}"
```

### Unsupported Entry Points

There is no command-line command, `main` method, shell integration, file
format, service endpoint, or additional Commons Validator class in this
bounded task. An implementation is complete when the documented
`RegexValidator` type is usable from another Java class in the stated package;
do not publish guessed APIs for classes that are not part of this contract.

## Implementation Notes

### Construction and State

Compile each expression during construction with the selected case-sensitivity
mode. Retain the compiled patterns and the original expression text needed by
`toString()`. Preserve input order. Treat the object as safe to reuse across
repeated read-only calls; no method should alter the configured expressions.

Do not retain a mutable caller-owned array as the validator's authoritative
configuration. A defensive copy is required for constructor input, and
`getPatterns()` must return a defensive array copy. The JDK `Pattern` objects
themselves may be shared because they are immutable.

### Matching Semantics

Use complete-match semantics for `isValid`, `match`, and `validate`. For
multiple patterns, stop conceptually at the first pattern that completely
matches so that group results are deterministic. A pattern that matches a
prefix but leaves trailing input must not be accepted.

Capturing groups are numbered by the Java regular-expression engine. Return
only groups one through the count reported by the selected match. Preserve
nulls for optional groups and preserve the group's left-to-right order.

### Error and Boundary Behavior

The following boundaries are part of the public contract:

1. Null input to `isValid`, `match`, or `validate` is handled without a
   matching attempt: boolean validation returns `false`, group extraction and
   aggregation return `null`.
2. A null or empty expression, null expression array, empty expression array,
   or null array element is rejected with `IllegalArgumentException`.
3. Invalid non-empty regular-expression syntax may propagate the JDK's
   unchecked `PatternSyntaxException` from construction.
4. A successful expression with no capturing groups produces an empty group
   array from `match` and an empty string from `validate`.
5. An unmatched optional group is represented as null by `match` and omitted
   by `validate`, without shifting later group positions.
6. A returned pattern array can be changed by the caller without changing a
   later call to `isValid`, `match`, `validate`, or `toString`.

### Determinism and Resource Limits

For the same ordered expressions, case flag, and input string, return the same
type, values, group order, and text representation on every invocation. Do not
use current time, random numbers, locale-sensitive formatting, thread races,
or unordered map iteration. Keep all work in memory and bounded by the input
expressions and strings; do not create background work or perform I/O.

### Small Verifiable Usage Scenarios

These examples describe observable behavior without prescribing an algorithm:

```java
RegexValidator route = new RegexValidator("^/users/(\\d+)$");
route.isValid("/users/42");          // true
route.isValid("/users/42/details");  // false
route.match("/users/42")[0];         // "42"
```

```java
RegexValidator alternatives = new RegexValidator(
    new String[] {"^cat$", "^dog$"});
alternatives.isValid("dog");         // true
alternatives.isValid("catalog");     // false
```

```java
RegexValidator optional = new RegexValidator("(prefix-)?(item)");
optional.match("item")[0];           // null
optional.validate("item");           // "item"
```

```java
RegexValidator insensitive = new RegexValidator("ready", false);
insensitive.isValid("READY");        // true
insensitive.isValid("already");      // false
```

Do not copy an upstream implementation verbatim, expose private verifier
details, add hidden-test-specific branches, or weaken the no-network and
no-dependency boundaries to obtain a result. The task is to recreate the
documented public behavior as a clean Java library.
