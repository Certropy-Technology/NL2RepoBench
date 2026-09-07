# Introduction and Goals of the Apache Commons Validator Project

Apache Commons Validator provides reusable validation routines. This task
focuses on the self-contained `RegexValidator` class, which compiles one or
more Java regular expressions and applies them to complete input strings.

## Natural Language Instruction (Prompt)

Create a standard single-module Java Maven project named Apache Commons
Validator. Implement the bounded public API below under
`src/main/java/org/apache/commons/validator/routines/RegexValidator.java`.
Do not add external runtime dependencies, network access, or command-line
entry points.

## Environment Configuration

### Core Dependency Library Versions

Use Temurin JDK `21.0.12+8`, Maven `3.9.11`, and Linux `amd64/glibc`.
Execution is offline. The candidate `pom.xml` may contain normal project
metadata only; do not use dependencies, build/plugins, profiles, repositories,
modules, extensions, or custom Maven settings to control verification.

## Apache Commons Validator Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/validator/routines/RegexValidator.java
```

The class must have package
`org.apache.commons.validator.routines` and may use `java.util.regex.Pattern`,
`Matcher`, and other JDK classes.

## API Usage Guide

### Core APIs

#### Construction

```java
import org.apache.commons.validator.routines.RegexValidator;

RegexValidator one = new RegexValidator("^item-[0-9]+$");
RegexValidator many = new RegexValidator(new String[] {"cat", "dog"});
RegexValidator insensitive = new RegexValidator("hello", false);
RegexValidator insensitiveMany = new RegexValidator(new String[] {"cat", "dog"}, false);
```

Required public signatures:

```java
public RegexValidator(String regex)
public RegexValidator(String... regexs)
public RegexValidator(String regex, boolean caseSensitive)
public RegexValidator(String[] regexs, boolean caseSensitive)
```

The one-string and varargs constructors compile case-sensitive patterns. The
boolean overload uses case-sensitive matching when `caseSensitive` is true and
case-insensitive matching when it is false. A constructor must preserve the
pattern order supplied by the caller.

#### Pattern inspection

```java
Pattern[] patterns = one.getPatterns();
```

Signature:

```java
public java.util.regex.Pattern[] getPatterns()
```

The result is a new array containing the compiled patterns in constructor
order. Callers may modify that returned array without changing the validator.

#### Boolean validation

```java
boolean accepted = one.isValid("item-42");
```

Signature:

```java
public boolean isValid(String value)
```

Matching uses the regular-expression engine's complete-match operation: a
pattern must match the entire input, not merely a prefix or substring. If
`value` is `null`, return `false`. When several patterns exist, return true if
the first matching pattern or any later pattern accepts the complete input.

#### Captured groups

```java
String[] groups = new RegexValidator("(item)-(\\d+)").match("item-42");
```

Signature:

```java
public String[] match(String value)
```

Return the capturing groups of the first pattern that completely matches,
excluding group zero. Preserve group order and return `null` for a null or
non-matching value. An unmatched optional group is represented by a null array
element. If the matching pattern has no capturing groups, return a non-null
empty array.

#### Aggregated groups

```java
String text = new RegexValidator("(item)-(\\d+)").validate("item-42");
```

Signature:

```java
public String validate(String value)
```

For the first complete match, concatenate non-null capturing groups in their
left-to-right order and return that string. With exactly one group, return the
group or an empty string when that group did not participate. Return `null`
for null or non-matching input. Do not include the complete match unless it is
also a capturing group.

#### Text form

```java
String description = new RegexValidator("cat", "dog").toString();
```

Signature:

```java
public String toString()
```

Return `RegexValidator{...}` with each original pattern's textual form in
constructor order, separated by commas and with no spaces after commas.

### Actual Usage Modes

```java
RegexValidator id = new RegexValidator("^id:(\\d+)$");
id.isValid("id:17");                 // true
id.match("id:17")[0];                // "17"
id.validate("id:17");                // "17"
id.isValid("prefix-id:17");          // false

RegexValidator words = new RegexValidator(new String[] {"cat", "dog"});
words.isValid("dog");                // true
words.getPatterns().length;           // 2
```

### Supported Function Types

The supported slice consists only of the four public constructors,
`getPatterns`, `isValid`, `match`, `validate`, and `toString`. Image, email,
URL, domain, credit-card, locale, filesystem, and network validators are
outside this task.

### Error Handling

Reject a null or empty pattern list and a null or empty individual pattern with
`IllegalArgumentException`. Invalid regular-expression syntax may propagate
the JDK `PatternSyntaxException` (a runtime exception). Do not silently skip,
rewrite, or reorder patterns. Null input to `isValid`, `match`, or `validate`
has the return behavior specified above. The API has no mutable shared state or
filesystem/network side effects.

## Detailed Implementation Nodes of Functions

### Node 1: Pattern compilation

Compile every supplied pattern once during construction with the selected JDK
case-sensitivity flag. Preserve the input order and reject missing patterns.

### Node 2: Complete validation

For `isValid`, call complete matching for each compiled pattern in order and
return true on the first success. Null input is false.

### Node 3: Capturing-group extraction

For `match`, return groups 1 through `groupCount()` from the first complete
match, preserving null optional groups and returning null when no pattern
matches.

### Node 4: Group aggregation

For `validate`, concatenate only participating capturing groups. A single
missing group produces the empty string; no match produces null.

### Node 5: Defensive pattern inspection

`getPatterns` returns an array clone, while each compiled `Pattern` remains the
JDK immutable pattern object. Array mutation must not alter later validation.

### Node 6: Deterministic representation and boundaries

`toString` is deterministic and reflects pattern order. Cover null input,
empty patterns, optional groups, case-insensitive matching, multiple patterns,
and complete-match versus prefix behavior. Every hidden leaf corresponds to
one of Nodes 1–6 and to the public API examples above.
