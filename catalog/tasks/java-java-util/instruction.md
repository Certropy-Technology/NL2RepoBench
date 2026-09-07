# Introduction and Goals of the Java Util Project

## Natural Language Instruction (Prompt)

Implement the bounded public API described below for the Java Util project. Your submission is a
small Maven project whose main source tree contains the class
`com.cedarsoftware.util.ByteUtilities`. Keep the public package and method signatures exactly as
specified. The implementation must be deterministic, self-contained, and usable without network
access or runtime downloads.

The requested class provides common operations on byte arrays and hexadecimal text. Implement the
conversion, gzip-header detection, and byte-pattern search behavior in the API Usage Guide. Do not
add a dependency or require a service, filesystem state, locale, current time, background thread,
reflection scan, or external process. A metadata-only Maven `pom.xml` is sufficient.

## Environment Configuration

The project is compiled with Temurin JDK 21.0.12+8 and Maven 3.9.11 on Linux amd64 with glibc.
Candidate, verifier, and control execution has no network access. The candidate POM is metadata-only:
it may identify the project but must not declare dependencies, repositories, modules, profiles, build
plugins, or plugin configuration. The implementation must compile with `javac --release 21` and
must not fetch artifacts during execution.

### Core Dependency Library Versions

This bounded contract has an empty Maven dependency closure. Use only Java SE classes available in
the configured JDK. Do not add the full upstream test dependency set or substitute another library
for the requested API.

## Java Util Project Architecture

### Project Directory Structure

Use the conventional Maven layout:

```text
pom.xml
src/main/java/com/cedarsoftware/util/ByteUtilities.java
```

The public class is final and consists of static utility methods. A private constructor is allowed.
No particular internal algorithm is required; correctness at the documented boundaries is required.

## API Usage Guide

### Core APIs

Import `com.cedarsoftware.util.ByteUtilities`.

`public static char toHexChar(int value)` returns one uppercase hexadecimal digit. The low four
bits of `value` are used, so values outside 0 through 15 wrap by the low-nibble rule (for example,
`toHexChar(16)` is `'0'` and `toHexChar(-1)` is `'F'`). The method has no side effects.

`public static String encode(byte[] bytes)` converts each byte to two uppercase hexadecimal
characters, preserving byte order. It returns `null` for a null array and returns the empty string
for an empty array. The operation does not mutate its input.

`public static byte[] decode(String value)` and
`public static byte[] decode(CharSequence value)` accept an even-length hexadecimal sequence and
return the corresponding bytes in order. Both uppercase and lowercase hexadecimal digits are
accepted. A null input, odd-length input, or input containing a non-ASCII/non-hex character returns
`null`; these invalid cases do not throw. A valid empty sequence returns a non-null empty byte array.

`public static boolean isGzipped(byte[] bytes)` returns true only when the first two bytes are the
GZIP magic bytes `0x1f` and `0x8b`. Null, empty, one-byte, and non-matching arrays return false.

`public static boolean isGzipped(byte[] bytes, int offset)` performs the same two-byte check
starting at `offset`. It returns false for null input, a negative offset, an offset outside the
array, fewer than two bytes remaining, or a non-matching pair. It does not inspect bytes before the
offset.

`public static int indexOf(byte[] data, byte[] pattern, int start)` returns the first index at or
after `start` where the complete pattern occurs. It returns `-1` for null inputs, a negative start,
an empty pattern, a pattern longer than the data, or when no complete occurrence fits. A pattern may
overlap another occurrence, and the returned index is the lowest valid index.

`public static int lastIndexOf(byte[] data, byte[] pattern, int start)` returns the greatest valid
pattern start at or before `start`. A start beyond the last possible position is treated as the
last possible position. It returns `-1` for null inputs, a negative start, an empty pattern, a
pattern longer than the data, or when no complete occurrence exists.

`public static int lastIndexOf(byte[] data, byte[] pattern)` is equivalent to searching backwards
from the last data index. It returns `-1` for null data or any invalid pattern.

### Actual Usage Modes

Typical use is to encode a binary value for text transport, decode a validated hexadecimal field,
recognize a GZIP header in a byte buffer, or locate a marker in a packet. Results depend only on the
provided arrays, sequences, and integer arguments. Calls do not change arrays, global state, or
configuration.

### Supported Function Types

The supported values are byte arrays, hexadecimal strings or character sequences, and integer
offsets or search positions. Byte order is the original left-to-right order. Hexadecimal output is
uppercase and uses exactly two characters per byte. Pattern searches compare signed Java bytes by
their exact eight-bit values.

### Error Handling

The conversion and search methods use their documented null/invalid sentinels: `decode` and
`encode` return null where specified, while searches and GZIP checks return `-1` or false. Do not
silently reinterpret malformed hexadecimal text as a different valid value. Normal valid inputs
must not throw.

## Detailed Implementation Nodes of Functions

1. Hexadecimal encoding must emit the high nibble before the low nibble for every byte and use
   uppercase digits.
2. Hexadecimal decoding must process pairs from left to right, accept either letter case, and
   reject odd length or any character outside `0-9`, `A-F`, and `a-f` with a null result.
3. GZIP detection must check exactly the two bytes at the requested starting position and must
   guard all null and boundary cases.
4. Forward pattern search must honor the inclusive start position and require the entire pattern to
   fit in the data array.
5. Reverse pattern search must clamp an oversized starting position to the final position where
   the pattern can fit, then examine candidate positions in descending order.
6. All public methods must remain deterministic and side-effect free for the documented inputs.
