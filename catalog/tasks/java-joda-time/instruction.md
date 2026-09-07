# Introduction and Goals of the Joda-Time Project

Joda-Time is a Java date and time library. This task isolates the deterministic
integer-formatting utility `org.joda.time.format.FormatUtils`. Recreate the
documented formatting surface in a normal single-module Maven project. Date
time zones, clocks, chronology, parsing, and serialization are outside this
bounded task.

## Natural Language Instruction (Prompt)

Implement `org.joda.time.format.FormatUtils` with the public methods listed in
this document. Keep implementation source under `src/main/java` and preserve
the exact package, class, method signatures, overloads, and checked exceptions.
Use only the Java standard library. The class is stateless and all formatting
is deterministic.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11
Linux amd64, glibc
Runtime dependencies: none; only java.base is required
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It may contain project coordinates,
packaging, and harmless metadata, but must not declare dependencies, plugins,
profiles, repositories, modules, extensions, or custom build instructions.

## Joda-Time Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/joda/time/format/FormatUtils.java
```

## API Usage Guide

### Core APIs

Import `org.joda.time.format.FormatUtils`. The class provides these overloads:

* `appendPaddedInteger(StringBuffer, int, int)` and
  `appendPaddedInteger(StringBuffer, long, int)` append a decimal value with
  at least `size` digits and a leading minus sign for negative values.
* `appendPaddedInteger(Appendable, int, int)` and
  `appendPaddedInteger(Appendable, long, int)` provide the same result and
  propagate `IOException` from the appendable.
* `writePaddedInteger(Writer, int, int)` and
  `writePaddedInteger(Writer, long, int)` write the same padded representation.
* `appendUnpaddedInteger(StringBuffer, int|long)` and
  `appendUnpaddedInteger(Appendable, int|long)` append ordinary decimal text
  without adding zeroes; the appendable overloads propagate `IOException`.
* `writeUnpaddedInteger(Writer, int|long)` writes ordinary decimal text.
* `calculateDigitCount(long)` returns the number of decimal digits, ignoring a
  leading minus sign; zero has one digit and `Long.MIN_VALUE` has 19 digits.

### Actual Usage Modes

Use a `StringBuffer` for in-memory construction, an `Appendable` when the
destination is generic, and a `Writer` when the caller owns a character
stream. The methods mutate only the supplied destination and return `void`.

### Supported Function Types

Values are signed Java `int` or `long` values. Padding applies when `size` is
larger than the value's digit count; a smaller size never truncates digits.
Negative zero is not a Java value and therefore needs no special handling.

### Error Handling

The appendable and writer methods preserve `IOException` from the destination.
The methods do not perform network or filesystem access. Null destinations
fail according to normal Java invocation behavior.

## Detailed Implementation Nodes of Functions

1. Preserve the exact decimal value, including the minus sign, for both
   primitive widths and for their minimum values.
2. Add zero padding between a negative sign and the magnitude, not before the
   sign. For example, padding `-7` to four digits yields `-0007`.
3. Do not remove digits when the requested size is below the natural width.
4. Ensure every overload has equivalent output for the same value and size.
5. Count digits deterministically for positive, zero, negative, and minimum
   `long` values.
