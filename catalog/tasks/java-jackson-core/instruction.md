## Project Description

Build a small, single-module Java library that provides the bounded
`tools.jackson.core.JsonPointer` API. The library represents a JSON Pointer
like path as an immutable value. It is intended for callers that need to parse
slash-separated property and array segments, inspect the first segment, match
that segment, navigate through the remaining path, and append a new segment.

The target is a compatible implementation of the documented public slice, not
the complete Jackson Core project. A caller should be able to compile a text
pointer, inspect its decoded property or canonical array index, consume one
segment at a time, compare a segment with a property name or index, and render
the pointer back to text. The API is deterministic for the same finite Java
string and integer inputs.

Create exactly the public class `tools.jackson.core.JsonPointer` as a final,
immutable value type. The class must be usable without a JSON parser, an object
mapper, a tree model, a token stream, a filesystem, a clock, randomness, or
network access. Keep the implementation focused on this class and its public
contract. Do not add unrelated Jackson classes or a command-line application.

The in-scope behavior is:

- the static `compile` and `empty` factories;
- RFC 6901-style `~0` and `~1` segment decoding and the corresponding property
  escaping performed by `appendProperty`;
- first-segment property and canonical non-negative integer inspection;
- empty, one-segment, and multi-segment navigation with `head` and `tail`;
- property and array-element matching, including the returned remaining path;
- appending a property or non-negative array index;
- stable `toString`, `equals`, and `hashCode` behavior.

The out-of-scope behavior is the rest of Jackson Core: JSON lexical parsing,
JSON generation, streaming tokens, tree traversal, codecs, schema handling,
annotations, data binding, URI resolution, pointer evaluation against a JSON
document, and command-line or network interfaces. Do not expose or implement
private verifier helpers, test-only adapters, or APIs inferred only from the
upstream repository name. No additional public API is confidently bindable
from the bounded source asset used for this task.

## Natural Language Instruction

Create the Maven project described below from an empty `workspace/` directory.
Implement the public class `tools.jackson.core.JsonPointer` with the complete
factory, inspection, navigation, matching, append, rendering, equality, and
hashing contract in the API Usage Guide. Keep the class immutable and keep the
package declaration and source path exact. Preserve encoded pointer text while
matching decoded segment values, retain empty segments, and reject only the
invalid inputs described by the contract. The project must validate offline on
Java 21 with no third-party dependency and no network access.

## Supports

### Runtime and dependency boundary

- Run on Linux amd64 with glibc, Temurin JDK `21.0.12+8`.
- Use Maven `3.9.11` as the package/build entry point.
- Use Java release 21 language and class-file settings.
- The module has an empty third-party dependency closure and uses only
  `java.base` classes, such as `String`, `List`, `ArrayList`, and `Objects`.
- The candidate `pom.xml` is metadata for a single module. It must not declare
  repositories, external dependencies, modules, profiles, build extensions, or
  plugins for this task.
- Maven validation must work offline. The relevant command is
  `mvn --offline validate` (or the same command with a local Maven repository).
- Agent, candidate, verifier, Oracle, and controls run with no network. Do not
  fetch Jackson source, Maven artifacts, GitHub content, DNS records, or any
  other external service at runtime.

### Project Directory Structure

The generated project is rooted at `workspace/` and must use this layout:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── tools/
                └── jackson/
                    └── core/
                        └── JsonPointer.java
```

`pom.xml` identifies a single Maven project and contains no runtime dependency.
The package declaration in `JsonPointer.java` is exactly
`package tools.jackson.core;`. The file path, package name, and public class
name must agree so that a caller can import the class directly. No CLI,
resource directory, generated source directory, or test implementation is
required by the public task.

### Setup performed by the harness

The harness supplies the Java 21 and Maven environment, invokes offline
validation, and compiles the candidate class with the declared package. It
does not install a third-party library or provide a JSON document for pointer
evaluation. The candidate must therefore include all behavior needed by the
class itself. Do not rely on a working directory, environment variable,
current time, locale, system property, or mutable singleton.

## API Usage Guide

### `tools.jackson.core.JsonPointer`

Import the class with:

```java
import tools.jackson.core.JsonPointer;
```

The class is `public final`. Instances are immutable: parsing, navigation,
matching, and appending do not mutate an existing instance. Inputs are ordinary
finite Java `String` values and `int` values. All returned pointer objects are
deterministic for equal inputs.

### `public static JsonPointer compile(String expr)`

`compile` parses a pointer expression and returns a `JsonPointer`. A `null`
expression and the empty string both denote the empty pointer. A non-empty
expression must begin with `/`; otherwise the method throws
`IllegalArgumentException`.

Each slash begins a segment. Thus `/a/b` contains the decoded segments `a` and
`b`, while `/` contains one empty segment. The expression is split in order,
including empty segments between adjacent slashes and after a trailing slash.
The escape `~0` decodes to `~`, and `~1` decodes to `/`. Other tilde sequences
remain ordinary text rather than being interpreted as a supported escape.

Ordinary example:

```java
JsonPointer pointer = JsonPointer.compile("/users/0/name");
pointer.matchesProperty("users");       // true
pointer.tail().matchesElement(0);        // true
```

Edge examples:

```java
JsonPointer empty = JsonPointer.compile(null);
JsonPointer slash = JsonPointer.compile("/");
JsonPointer escaped = JsonPointer.compile("/a~1b/~0");
```

The three values represent an empty pointer, one empty property segment, and
the decoded property sequence `a/b`, `~`. Parsing has no I/O or global state.

### `public static JsonPointer empty()`

`empty()` returns the canonical empty pointer. The empty pointer has an empty
text form and zero textual length. It has no matching property or array index.
Its `matches()` result is true because there is no remaining segment to match.
Its `tail()` and `head()` results are `null`.

Ordinary example:

```java
JsonPointer pointer = JsonPointer.empty();
pointer.toString();                  // ""
pointer.length();                    // 0
pointer.getMatchingProperty();       // null
```

The empty result is also the navigation result after consuming the only
segment of a one-segment pointer. Calling the factory repeatedly must preserve
the same observable value and must not introduce mutable state.

### `public int length()` and `public String toString()`

`length()` returns the number of Java `char` values in the pointer's textual
representation, exactly as `toString().length()` would. `toString()` returns
the pointer text in its escaped form. Rendering does not decode segments or
perform I/O.

Ordinary example:

```java
JsonPointer pointer = JsonPointer.compile("/a~1b/0");
pointer.toString();                 // "/a~1b/0"
pointer.length();                   // pointer.toString().length()
```

An edge example is `JsonPointer.compile("/")`: its text is `/` and its length
is one even though its first decoded property is the empty string. Unicode
characters are retained as Java string content; do not count UTF-8 bytes.

### `public boolean matches()`

`matches()` reports whether this pointer is the final matching state. It is
true for the empty pointer. A non-empty pointer remains a path with a first
segment and is not the empty matching state until navigation consumes that
segment.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a/b");
path.matches();                     // false
path.tail().tail().matches();       // true
```

The empty edge case is `JsonPointer.empty().matches()`, which is true. This
method only reports pointer state and never tests a JSON value.

### `public String getMatchingProperty()`

`getMatchingProperty()` returns the decoded first segment for a non-empty
pointer. It returns `null` for the empty pointer. The result is a Java string;
an empty segment returns `""`, not `null`.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a~1b/rest");
path.getMatchingProperty();         // "a/b"
```

For the edge expression `/`, the result is the empty string. For `/~2`, the
result retains the unsupported escape spelling as `~2`. This method does not
alter the pointer or return the remaining path.

### `public int getMatchingIndex()`

`getMatchingIndex()` returns the first decoded segment as a non-negative
integer only when it is a canonical decimal array index. The accepted forms
are `0` or a non-zero digit followed by digits, with a value no greater than
`Integer.MAX_VALUE`. For a property, an empty segment, a leading-zero form
such as `01`, a negative-looking form, a non-decimal form, or an overflow, it
returns `-1` rather than throwing.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/10/name");
path.getMatchingIndex();            // 10
```

Edge examples include `compile("/0").getMatchingIndex()` returning `0`, and
`compile("/01").getMatchingIndex()` returning `-1`. The method has no state or
I/O side effects.

### `public boolean mayMatchProperty()` and `public boolean mayMatchElement()`

`mayMatchProperty()` indicates that a non-empty pointer has a property segment
available for matching. It is false for the empty pointer. A segment can be a
property even when its text looks numeric.

`mayMatchElement()` indicates that the first segment is a valid canonical
non-negative index. It is equivalent to the availability of a non-negative
result from `getMatchingIndex()` and is false for the empty pointer.

Ordinary example:

```java
JsonPointer property = JsonPointer.compile("/name");
property.mayMatchProperty();        // true
property.mayMatchElement();         // false
```

For `/0`, `mayMatchElement()` is true. For `/01`, it is false because leading
zeroes do not form a canonical index. Neither method evaluates a document.

### `public JsonPointer tail()`

`tail()` returns the pointer after removing its first segment. For a
multi-segment pointer it returns the remaining non-empty pointer. For a
one-segment pointer it returns the empty pointer. For the empty pointer it
returns `null` because there is no segment to consume.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a/b");
JsonPointer rest = path.tail();
rest.toString();                   // "/b"
```

The boundary examples are `compile("/a").tail()`, which is the empty pointer,
and `empty().tail()`, which is `null`. The original `path` remains unchanged.

### `public JsonPointer head()`

`head()` returns the pointer after removing its final segment. For a
multi-segment pointer it retains all preceding segments. For a one-segment
pointer it returns the empty pointer. For the empty pointer it returns `null`.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a/b/c");
path.head().toString();             // "/a/b"
```

For `compile("/a")`, `head()` is the empty pointer. For `empty()`, `head()` is
`null`. Escaped properties must remain correctly escaped in the returned text,
and the source object must not be mutated.

### `public boolean matchesProperty(String name)`

`matchesProperty` compares `name` with the decoded first property segment. It
returns false for the empty pointer and for a null name. A successful match
does not consume the pointer.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a~1b/rest");
path.matchesProperty("a/b");        // true
path.matchesProperty("a~1b");       // false
```

The edge cases are a null name, which returns false, and `compile("/")`,
which matches the empty string. Matching compares decoded Java strings and is
deterministic.

### `public JsonPointer matchProperty(String name)`

`matchProperty` performs the same decoded comparison as `matchesProperty`. If
it succeeds, it returns the same logical result as `tail()`, allowing a caller
to consume the matched property. If it fails, it returns `null`. A null name
therefore returns `null`.

Ordinary example:

```java
JsonPointer rest = JsonPointer.compile("/a/b").matchProperty("a");
rest.toString();                    // "/b"
```

For `compile("/a").matchProperty("a")`, the result is the empty pointer. A
failed name, including a null name, does not mutate the original pointer.

### `public boolean matchesElement(int index)`

`matchesElement` returns true only when `index` is non-negative and equals the
first segment's canonical integer index. Property segments and the empty
pointer return false. Negative caller input returns false rather than
throwing.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/2/item");
path.matchesElement(2);              // true
path.matchesElement(1);              // false
```

For `/01`, `matchesElement(1)` is false because the segment is not canonical.
For a negative argument, return false and leave the pointer unchanged.

### `public JsonPointer matchElement(int index)`

`matchElement` returns `tail()` when `matchesElement(index)` succeeds and
returns `null` otherwise. It must not reinterpret a property as an array index.

Ordinary example:

```java
JsonPointer rest = JsonPointer.compile("/2/item").matchElement(2);
rest.toString();                    // "/item"
```

The edge cases are a negative argument or a non-canonical `/01` segment; both
return `null`. A one-segment successful match returns the empty pointer.

### `public JsonPointer appendProperty(String property)`

`appendProperty` returns a pointer with one property segment appended. Escape
each `~` as `~0` and each `/` as `~1` in the property before appending it. An
empty property is valid and creates an empty segment. A null property is a
no-op that returns the current logical pointer unchanged. The existing pointer
and the returned pointer are immutable.

Ordinary example:

```java
JsonPointer path = JsonPointer.compile("/a");
JsonPointer extended = path.appendProperty("x~y/z");
extended.toString();                // "/a/x~0y~1z"
```

The edge examples are `empty().appendProperty("")`, which renders `/`, and
`path.appendProperty(null)`, which preserves the original path. Appending has
no filesystem, network, or global-state side effect.

### `public JsonPointer appendIndex(int index)`

`appendIndex` appends one array segment using the canonical decimal rendering
of the non-negative `int` value. A negative index throws
`IllegalArgumentException`. The current pointer is not modified.

Ordinary example:

```java
JsonPointer extended = JsonPointer.compile("/items").appendIndex(3);
extended.toString();                // "/items/3"
```

`empty().appendIndex(0)` renders `/0`. `appendIndex(-1)` is an error and must
throw `IllegalArgumentException`; it must not create a negative pointer
segment.

### `equals(Object)` and `hashCode()`

`equals` compares two `JsonPointer` instances by their textual pointer value,
including the original escape spelling. Equal pointers must have equal
`hashCode` values. A non-`JsonPointer` object, including null, is not equal.

Ordinary example:

```java
JsonPointer left = JsonPointer.compile("/a~1b");
JsonPointer right = JsonPointer.compile("/a~1b");
left.equals(right);                 // true
left.hashCode() == right.hashCode(); // true
```

The decoded-equivalent text `/a/b` is not required to compare equal to
`/a~1b`, because equality follows the rendered pointer representation. The
empty pointer compares equal to another empty pointer.

## Implementation Notes

Keep all implementation state private and final. A pointer may cache decoded
segment information, but no public operation may mutate an instance or depend
on call order. Navigation results must be safe to retain while the original
pointer is reused. Use normal Java exception types from the documented
contract, especially `IllegalArgumentException` for an invalid compile prefix
and a negative appended index.

Preserve the distinction between encoded text and decoded matching content.
Parsing `/a~1b` must make property matching see `a/b`, while rendering the
pointer retains an escaped slash. Appending must escape in the documented
order so that an input property containing both `~` and `/` round-trips as one
segment. Unsupported tilde forms are not permission to invent additional
escape rules.

Treat empty segments as real segments. The expressions `""`, `/`, `/a/`, and
`/a//b` have different segment boundaries. Do not drop a leading, trailing, or
adjacent empty segment while splitting. Numeric inspection is stricter than
general property inspection: leading zeroes, signs, non-ASCII digits, and
overflow do not become accepted array indexes.

Small verifiable examples:

```java
JsonPointer p = JsonPointer.compile("/a~1b/0");
assert p.getMatchingProperty().equals("a/b");
assert p.tail().getMatchingIndex() == 0;
```

```java
JsonPointer p = JsonPointer.empty().appendProperty("x/y").appendIndex(4);
assert p.toString().equals("/x~1y/4");
```

```java
assert JsonPointer.compile("/01").getMatchingIndex() == -1;
assert JsonPointer.compile("/a").matchElement(0) == null;
```

```java
try {
    JsonPointer.compile("a/b");
    throw new AssertionError("invalid prefix accepted");
} catch (IllegalArgumentException expected) {
    // expected boundary behavior
}
```

The examples are behavioral illustrations, not a request to copy an upstream
implementation or any hidden test. Keep the public surface limited to the
class and methods specified above. Do not add logging, subprocesses, network
access, environment mutation, or dependencies merely to implement the slice.
