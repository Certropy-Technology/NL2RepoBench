## Project Description

Build a small, single-module Java project that recreates the bounded public
contract of Joda-Time's deterministic integer-formatting utility. The only
required public type is `org.joda.time.format.FormatUtils`. It formats signed
primitive `int` and `long` values into caller-provided character destinations,
with optional zero padding, and reports the decimal digit count of a `long`.

The intended users are Java code that assembles date/time-like text without
depending on a clock, time zone, locale, filesystem, network service, or
third-party runtime library. The task is about observable character output and
the documented method contracts, not about reimplementing the complete
Joda-Time project.

### Natural Language Instruction

Create the project from an empty workspace. Add the exact class and package
shown in the API guide, keep production source below `src/main/java`, and
preserve every listed overload, primitive parameter type, return type, and
checked exception. The class must be usable through the import
`org.joda.time.format.FormatUtils`.

The implementation must support all of these capabilities:

1. Append or write signed `int` values with a requested minimum digit width.
2. Append or write signed `long` values with a requested minimum digit width.
3. Append or write signed values without padding when unpadded output is
   requested.
4. Count the decimal digits of every `long`, including zero, negatives, and
   `Long.MIN_VALUE`.

Padded output means decimal digits, not a localized number representation. For
 a negative value, the minus sign precedes any inserted zeroes. A width smaller
 than the natural magnitude width must not truncate or round the value. Every
 destination overload for the same value and width must produce equivalent
 characters.

Do not add a command-line application, a date/time engine, parsing support,
time-zone support, chronology support, serialization support, or public helper
types that are not part of this bounded contract. Do not require a third-party
dependency. The candidate `pom.xml` is metadata only and must not be used to
download dependencies or to change the source layout.

## Supports

### Runtime and Build Configuration

Use the following fixed environment and project identity:

```text
Language: Java
JDK: Temurin 21.0.12+8
Maven: 3.9.11
Platform: Linux amd64 with glibc
Runtime dependency closure: java.base only
Network: unavailable during agent, candidate, verifier, Oracle, and control runs
```

The project must be compilable as a normal single-module Maven project. A
minimal `pom.xml` may declare coordinates, packaging, and project metadata.
It must not declare repositories, modules, plugins, profiles, extensions,
custom build instructions, or runtime dependencies. The implementation must
compile with the Java 21 standard library and must not fetch artifacts during
execution.

The task has no CLI or shell entry point. The public entry point is the Java
type `org.joda.time.format.FormatUtils`; clients compile against that package
and invoke its static methods. All operations are synchronous and
deterministic. They do not inspect environment variables, current time,
locale, filesystem contents, process state, or network state.

### Project Directory Structure

Create this target structure, with `workspace/` as the project root:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── joda/
                    └── time/
                        └── format/
                            └── FormatUtils.java
```

The package declaration in `FormatUtils.java` must be
`package org.joda.time.format;`. The class is a utility class with static
operations; callers should not need to create an instance. No resource file,
configuration file, generated source, or command-line wrapper is required.

## API Usage Guide

All methods below are members of the public class
`org.joda.time.format.FormatUtils`. Use this import in client code:

```java
import org.joda.time.format.FormatUtils;
```

The destination types have their standard Java meanings. `StringBuffer` is a
mutable in-memory destination. `Appendable` is the general character sink and
may throw `IOException` while accepting characters. `Writer` is the stream
destination and may also throw `IOException`. Each method returns `void` except
`calculateDigitCount`, which returns `int`.

### `appendPaddedInteger(StringBuffer, int, int)`

Signature:

```java
public static void appendPaddedInteger(StringBuffer buf, int value, int size)
```

This overload appends the base-10 representation of `value` to `buf`. The
absolute decimal magnitude has at least `size` digits; zeroes are inserted
between a leading minus sign and the magnitude for negative values. Existing
characters in `buf` remain in place and the new text is appended at its end.
The method returns no value and performs no I/O. `StringBuffer` is non-null in
normal use; a null destination causes the normal unchecked null failure.

For example, `appendPaddedInteger(new StringBuffer("id="), 7, 4)` produces
`"id=0007"`. As an edge case,
`appendPaddedInteger(new StringBuffer(), -7, 4)` produces `"-0007"`, and a
size below the natural width, such as `size == 1` for `Integer.MIN_VALUE`,
still emits all digits of the value.

### `appendPaddedInteger(StringBuffer, long, int)`

Signature:

```java
public static void appendPaddedInteger(StringBuffer buf, long value, int size)
```

This is the `long` counterpart of the preceding overload. It appends the
complete signed decimal representation and adds leading zeroes only when the
requested magnitude width is larger than the existing digit count. The sign
is never counted as a padding digit. It mutates only the supplied buffer and
returns `void`; it performs no external I/O.

For example, `appendPaddedInteger(new StringBuffer(), 123L, 5)` yields
`"00123"`. The minimum `long` is an important boundary: padding
`Long.MIN_VALUE` with any width up to 19 must preserve
`"-9223372036854775808"` exactly, because that value cannot be represented as
a positive `long` magnitude.

### `appendPaddedInteger(Appendable, int, int)`

Signature:

```java
public static void appendPaddedInteger(Appendable out, int value, int size)
    throws IOException
```

This overload has the same decimal and padding contract as the `StringBuffer`
`int` overload, but accepts any `Appendable`. It appends in destination order
and returns `void`. A destination-specific `IOException` must be allowed to
propagate to the caller; it must not be converted into a different public
checked type or silently ignored. A null destination fails with normal Java
null behavior before useful output can be produced.

For example, passing a `StringBuilder` as the `Appendable` and `(42, 5)`
appends `"00042"`. For an edge case, an `Appendable` that throws on its first
append may cause `IOException` to escape from this method.

### `appendPaddedInteger(Appendable, long, int)`

Signature:

```java
public static void appendPaddedInteger(Appendable out, long value, int size)
    throws IOException
```

This overload applies the same rules to a signed `long`. The full value is
emitted, the minus sign is emitted before padding for negative values, and
zeroes are inserted only when needed to reach the requested magnitude width.
The destination is the only mutable object. Ordering is the normal left-to-
right decimal ordering, and `IOException` from the `Appendable` is part of the
public contract.

For example, an `Appendable` receiving `(9000000000L, 12)` receives
`"009000000000"`. For an edge case, `(Long.MIN_VALUE, 3)` still receives the
19-digit signed value without truncation.

### `writePaddedInteger(Writer, int, int)`

Signature:

```java
public static void writePaddedInteger(Writer out, int value, int size)
    throws IOException
```

Write the same padded decimal representation as the `int` appendable overload
to the supplied `Writer`. The method returns `void` and changes only the
writer's output state. It does not close or flush the writer, because ownership
of that resource remains with the caller. Any `IOException` reported by the
writer is propagated.

For example, writing `-9` with size `3` to a `StringWriter` produces `"-009"`.
For an edge case, a writer that rejects writes must expose its `IOException`
to the caller; a successful call with `size == 0` must still emit the complete
decimal representation rather than an empty or truncated value.

### `writePaddedInteger(Writer, long, int)`

Signature:

```java
public static void writePaddedInteger(Writer out, long value, int size)
    throws IOException
```

Write a padded signed `long` in decimal form to `out`. The output ordering,
minimum-width rule, sign placement, non-truncation rule, and exception
propagation are identical to the other padded overloads. The method must not
flush or close `out`.

For example, writing `1234567890123L` with size `15` produces
`"001234567890123"`. For an edge case, writing `Long.MIN_VALUE` with a width
larger than 19 adds zeroes after the sign while preserving every original
digit.

### `appendUnpaddedInteger(StringBuffer, int)`

Signature:

```java
public static void appendUnpaddedInteger(StringBuffer buf, int value)
```

Append the ordinary base-10 signed representation of `value` to `buf`, with no
additional zeroes. The existing buffer content is preserved and the method
returns `void`. No I/O or global state is involved.

For example, appending `-42` to `"value="` yields `"value=-42"`. The edge
values `0`, `Integer.MAX_VALUE`, and `Integer.MIN_VALUE` must each retain their
complete ordinary representation.

### `appendUnpaddedInteger(Appendable, int)`

Signature:

```java
public static void appendUnpaddedInteger(Appendable out, int value)
    throws IOException
```

Append the ordinary signed decimal `int` representation to the generic
`Appendable`. No padding is added, no characters are removed, and the method
returns `void`. `IOException` from the destination propagates unchanged; the
method does not close or otherwise own the destination.

For example, an empty `StringBuilder` receiving `0` becomes `"0"`. For an
edge case, a failing appendable may throw `IOException`, and the caller must
be able to observe that checked exception.

### `appendUnpaddedInteger(StringBuffer, long)`

Signature:

```java
public static void appendUnpaddedInteger(StringBuffer buf, long value)
```

Append the complete ordinary base-10 representation of a `long` to `buf`.
There are no width or padding parameters. The minus sign, when present, is
the first character of the appended value. The operation is deterministic and
returns `void`.

For example, appending `9223372036854775807L` produces that exact 19-digit
text. For an edge case, appending `Long.MIN_VALUE` must produce
`"-9223372036854775808"`, not an overflowed positive value.

### `appendUnpaddedInteger(Appendable, long)`

Signature:

```java
public static void appendUnpaddedInteger(Appendable out, long value)
    throws IOException
```

Append the complete ordinary signed decimal `long` representation to `out`.
The method has no padding behavior, mutates only the destination, returns
`void`, and propagates destination `IOException`.

For example, an appendable receiving `-9000000000L` receives
`"-9000000000"`. For an edge case, zero is represented by exactly one
character, `"0"`, and a failing appendable may report `IOException`.

### `writeUnpaddedInteger(Writer, int)`

Signature:

```java
public static void writeUnpaddedInteger(Writer out, int value)
    throws IOException
```

Write the ordinary signed decimal representation of an `int` to `out`. This
method adds no zeroes, does not flush or close the writer, returns `void`, and
propagates `IOException` from the writer.

For example, writing `0` produces `"0"`. For an edge case, writing
`Integer.MIN_VALUE` preserves its minus sign and all ten magnitude digits.

### `writeUnpaddedInteger(Writer, long)`

Signature:

```java
public static void writeUnpaddedInteger(Writer out, long value)
    throws IOException
```

Write the ordinary signed decimal representation of a `long` to `out`, with
no width adjustment. It returns `void`, does not close or flush the writer,
and propagates writer `IOException`.

For example, writing `42L` produces `"42"`. For an edge case, writing
`Long.MIN_VALUE` must preserve the exact 20-character signed representation.

### `calculateDigitCount(long)`

Signature:

```java
public static int calculateDigitCount(long value)
```

Return the number of decimal digits in the magnitude of `value`, excluding a
possible leading minus sign. The result is always positive: zero has one
digit, every single-digit magnitude returns `1`, and the maximum result for a
`long` is `19`. The method is pure, deterministic, performs no I/O, and throws
no checked exception for any `long` input.

For example, `calculateDigitCount(12345L)` returns `5`. Boundary examples are
`calculateDigitCount(0L) == 1`,
`calculateDigitCount(-1L) == 1`, and
`calculateDigitCount(Long.MIN_VALUE) == 19`.

### Destination and Exception Contract

`StringBuffer`, `Appendable`, and `Writer` overloads preserve the supplied
destination's prior content and append or write in left-to-right order. They
do not sort, normalize locale, or add a line terminator. The only checked
exception in this API is `java.io.IOException` on the generic appendable and
writer overloads. Null references fail through ordinary Java invocation
behavior; no special error message or recovery behavior is required.

The `size` argument is a minimum magnitude width, not a maximum. Negative,
zero, and unusually large sizes must never cause truncation. The contract does
not require rejecting a negative size; treating it as a width that requires no
padding preserves the non-truncating behavior.

## Implementation Notes

Keep `FormatUtils` stateless. The class may prevent ordinary instantiation,
but all listed methods must remain public and static. Do not expose a second
public class, substitute a different package, or change `int` to `long` (or
vice versa) in an overload. Java overload selection matters because
`StringBuffer` is also an `Appendable`.

Use only `java.base` APIs. The output must be independent of locale, default
charset, default time zone, current time, random state, process state, and
filesystem contents. Do not read from or write to files, sockets, environment
variables, or standard input. Do not close or flush caller-owned `Appendable`
or `Writer` destinations.

The implementation must preserve Java primitive boundary values. In
particular, an approach that first negates `Long.MIN_VALUE` or
`Integer.MIN_VALUE` can overflow; the observable result must nevertheless be
the exact signed decimal text. Padding is applied to the magnitude digit
count, while the minus sign stays at the front. A requested width smaller than
the existing digit count is harmless and cannot remove characters.

The following small examples are suitable for manual verification:

```java
StringBuffer a = new StringBuffer("year=");
FormatUtils.appendPaddedInteger(a, 7, 4);
// a.toString() == "year=0007"

StringBuffer b = new StringBuffer();
FormatUtils.appendPaddedInteger(b, -7, 4);
// b.toString() == "-0007"

StringWriter c = new StringWriter();
FormatUtils.writeUnpaddedInteger(c, -9000000000L);
// c.toString() == "-9000000000"

int digits = FormatUtils.calculateDigitCount(Long.MIN_VALUE);
// digits == 19
```

Additional boundary checks should compare every `int` and `long` overload for
the same value and width, use zero and both primitive minimum values, and use
an `Appendable`/`Writer` that deliberately throws `IOException`. These checks
should verify public output and exception behavior only; do not depend on a
particular internal algorithm, private helper, test name, verifier protocol,
or reference source layout.

The project must remain buildable offline. A metadata-only Maven invocation
may validate the project, but implementation correctness is determined by the
public Java class and its observable contract. No CLI command is part of this
task, and no API beyond the methods documented above is confidently bindable
from the bounded source slice.
