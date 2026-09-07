## Project Description

### Natural Language Instruction

Create a small Maven project that reimplements the bounded public API of the Java Util
project. The project is a dependency-free Java utility library for deterministic operations
on byte arrays and hexadecimal text. A user should be able to compile the project from an
empty workspace and import the utility class below.

The implementation must provide these capabilities:

1. Convert a single integer nibble to an uppercase hexadecimal character.
2. Encode a byte array as an uppercase hexadecimal string and decode hexadecimal text back
   to bytes through both String and CharSequence overloads.
3. Detect the two-byte GZIP magic header at the beginning of an array or at a supplied
   offset, without reading outside the array.
4. Find the first or last complete occurrence of a byte pattern, including the overload
   that searches backwards from the final possible position.

Keep the public package and signatures exactly as specified in the API Usage Guide. The
main public type is `com.cedarsoftware.util.ByteUtilities`. It must be a stateless utility
class with static methods; a private constructor is acceptable. Do not add unrelated
upstream classes, a command-line interface, a service, or a second public API.

All observable results must depend only on method arguments. Do not require a database,
configuration file, locale, current time, random source, thread, reflection scan, external
process, filesystem state, or network service. Do not change caller-owned arrays or shared
global state. A metadata-only POM is sufficient because the contract has no Maven runtime
dependencies.

The requested behavior is a bounded contract rather than a request to reproduce every
class in the upstream repository. Classes or methods outside `ByteUtilities` are not
confidently bindable for this task and are out of scope.

## Supports

### Environment Configuration

Use the following build and execution environment:

- Language: Java.
- Runtime: Temurin JDK 21.0.12+8.
- Compiler target: `javac --release 21`.
- Package manager: Apache Maven 3.9.11.
- Platform: Linux amd64 with glibc.
- Network: no network access during agent, candidate, verifier, Oracle, or control runs.
- Runtime dependency closure: empty; use Java SE classes supplied by the JDK only.

The project must compile without downloading an artifact. If a POM is present, keep it
metadata-only: it may declare the project coordinates, but it must not declare external
dependencies, repositories, modules, profiles, or build plugins that need downloading.
The source must also compile directly when the only source file supplied to `javac` is
`src/main/java/com/cedarsoftware/util/ByteUtilities.java`.

### Installation and Build

From the project root, the normal build entry is:

```text
mvn --offline validate
```

The Java source entry can be checked independently with:

```text
javac --release 21 -d target/classes src/main/java/com/cedarsoftware/util/ByteUtilities.java
```

There is no CLI entry point and no required runtime command beyond using the Java class from
another Java program. Do not invent flags, `main` methods, shell wrappers, or generated
resources.

### Project Directory Structure

Create the project with `workspace/` as its root:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── com/
                └── cedarsoftware/
                    └── util/
                        └── ByteUtilities.java
```

The package declaration in `ByteUtilities.java` must be:

```java
package com.cedarsoftware.util;
```

The file name, directory casing, package name, and public class name must agree. No other
source package or resource directory is needed for this bounded task.

## API Usage Guide

### Public Type and Import

Import the utility class with:

```java
import com.cedarsoftware.util.ByteUtilities;
```

Declare the public type as `public final class ByteUtilities` with static utility methods.
The class has no required instance state. Calling any method must not mutate an input array,
write a file, read environment variables, access the network, or change process-wide state.

### `toHexChar`

Signature:

```java
public static char toHexChar(int value)
```

The method returns one uppercase hexadecimal character (`0` through `9`, or `A` through
`F`). It uses the low four bits of the supplied `int`, so the accepted input domain is all
Java `int` values rather than only the range 0 through 15. Values outside that range wrap
according to their low nibble.

The return type is a single `char`. The method has no side effects and does not throw for
any integer value.

Normal example:

```java
char digit = ByteUtilities.toHexChar(10);  // 'A'
```

Edge example:

```java
char wrapped = ByteUtilities.toHexChar(-1); // 'F'
char zero = ByteUtilities.toHexChar(16);    // '0'
```

### `encode`

Signature:

```java
public static String encode(byte[] bytes)
```

For a non-null array, encode each byte as exactly two uppercase hexadecimal characters in
the original left-to-right byte order. The high nibble precedes the low nibble. The result
length is exactly `bytes.length * 2`, and the result is a new immutable `String`.

For `null`, return `null`. For a non-null empty array, return the empty string. The method
does not modify the input array and has no filesystem, network, locale, or global-state side
effects. Normal valid input does not throw.

Normal example:

```java
String text = ByteUtilities.encode(new byte[] {0x00, (byte) 0xAF, 0x10});
// text is "00AF10"
```

Edge example:

```java
String empty = ByteUtilities.encode(new byte[0]); // ""
String absent = ByteUtilities.encode(null);        // null
```

### `decode(String)`

Signature:

```java
public static byte[] decode(String value)
```

Accept a hexadecimal `String` whose length is even. Each adjacent pair of ASCII digits
represents one byte, and pairs are decoded from left to right. Accept `0-9`, `A-F`, and
`a-f`; letter case does not change the resulting byte values. Return a new byte array whose
length is `value.length() / 2`.

Return `null` instead of throwing when `value` is `null`, has odd length, or contains any
character outside the ASCII hexadecimal set. A valid empty string returns a non-null empty
array. Whitespace, signs, prefixes such as `0x`, and non-ASCII look-alike digits are not
valid hexadecimal input. The input `String` is immutable and there are no other side
effects.

Normal example:

```java
byte[] bytes = ByteUtilities.decode("00aF10");
// bytes contains 0x00, (byte) 0xAF, and 0x10, in that order
```

Edge examples:

```java
byte[] empty = ByteUtilities.decode(""); // non-null, length 0
byte[] odd = ByteUtilities.decode("ABC"); // null
byte[] bad = ByteUtilities.decode("0G");  // null
```

### `decode(CharSequence)`

Signature:

```java
public static byte[] decode(CharSequence value)
```

Apply the same even-length, ASCII-hex pair rules and return shape as `decode(String)`, but
accept any `CharSequence` implementation. Read its characters in index order and do not
modify the sequence. `null`, odd length, and a non-hex character return `null`; a valid empty
sequence returns a non-null empty array. Invalid input is represented by the null sentinel,
not by a checked or unchecked exception.

Normal example:

```java
CharSequence field = new StringBuilder("aBcD");
byte[] bytes = ByteUtilities.decode(field);
// bytes contains (byte) 0xAB and (byte) 0xCD
```

Edge example:

```java
byte[] malformed = ByteUtilities.decode((CharSequence) "12-3"); // null
```

### `isGzipped(byte[])`

Signature:

```java
public static boolean isGzipped(byte[] bytes)
```

Return `true` only when the first two array elements are the GZIP magic bytes `0x1f` and
`0x8b`, respectively. The method only requires the two-byte header; it does not validate a
complete compressed stream, flags, optional fields, checksum, or payload.

Return `false` for `null`, an empty array, an array of length one, or an array whose first
two bytes do not match. Do not inspect or mutate any other part of the input. The method has
no side effects and does not throw for these boundary cases.

Normal example:

```java
boolean compressed = ByteUtilities.isGzipped(new byte[] {0x1f, (byte) 0x8b, 0x00});
// true: only the leading magic pair is required
```

Edge example:

```java
boolean noHeader = ByteUtilities.isGzipped(new byte[] {0x1f}); // false
```

### `isGzipped(byte[], int)`

Signature:

```java
public static boolean isGzipped(byte[] bytes, int offset)
```

Check the same two-byte magic pair beginning at the inclusive `offset`. Return `true` when
`bytes[offset]` is `0x1f` and `bytes[offset + 1]` is `0x8b`. Bytes before `offset` must not
affect the result.

Return `false` for a null array, a negative offset, an offset outside the array, fewer than
two bytes remaining from the offset, or a non-matching pair. The method must guard all array
boundaries and must not throw an index-related exception for these cases.

Normal example:

```java
byte[] buffer = new byte[] {0x00, 0x00, 0x1f, (byte) 0x8b, 0x01};
boolean found = ByteUtilities.isGzipped(buffer, 2); // true
```

Edge example:

```java
boolean truncated = ByteUtilities.isGzipped(buffer, 4); // false: one byte remains
```

### `indexOf`

Signature:

```java
public static int indexOf(byte[] data, byte[] pattern, int start)
```

Search `data` from the inclusive index `start` in ascending order. Return the lowest index
at or after `start` at which every byte of `pattern` occurs consecutively and completely.
Compare byte values exactly as Java bytes; do not decode them as text or apply character
normalization. Overlapping matches are allowed.

Return `-1` for null `data`, null `pattern`, a negative `start`, an empty pattern, a pattern
longer than `data`, or when no complete occurrence fits at or after `start`. A match that
would begin in the final element but extend past the array is not complete and must not be
returned. No input array is changed and no exception is required for invalid search inputs.

Normal example:

```java
byte[] data = new byte[] {0x00, 0x11, 0x22, 0x11, 0x22};
int first = ByteUtilities.indexOf(data, new byte[] {0x11, 0x22}, 0); // 1
```

Edge examples:

```java
int overlap = ByteUtilities.indexOf(
    new byte[] {1, 1, 1}, new byte[] {1, 1}, 1); // 1
int absent = ByteUtilities.indexOf(data, new byte[0], 0); // -1
```

### `lastIndexOf(byte[], byte[], int)`

Signature:

```java
public static int lastIndexOf(byte[] data, byte[] pattern, int start)
```

Search backwards and return the greatest valid pattern start at or before `start`. A valid
start is one where the whole pattern fits within `data`. If `start` is greater than the last
possible pattern start, clamp the search to that last possible start before searching in
descending order.

Return `-1` for null inputs, a negative `start`, an empty pattern, a pattern longer than
`data`, or when no complete occurrence exists. As with `indexOf`, compare exact byte values,
allow overlapping occurrences, preserve array contents, and do not throw for the documented
invalid search cases.

Normal example:

```java
byte[] data = new byte[] {0x00, 0x11, 0x22, 0x11, 0x22};
int last = ByteUtilities.lastIndexOf(data, new byte[] {0x11, 0x22}, 4); // 3
```

Edge example:

```java
int clamped = ByteUtilities.lastIndexOf(data, new byte[] {0x11, 0x22}, 99); // 3
int invalid = ByteUtilities.lastIndexOf(data, new byte[0], 4); // -1
```

### `lastIndexOf(byte[], byte[])`

Signature:

```java
public static int lastIndexOf(byte[] data, byte[] pattern)
```

Search backwards from the final possible start. This overload is equivalent to calling the
three-argument overload with a start at the end of `data`, while still requiring the complete
pattern to fit. Return the greatest matching index, or `-1` for null inputs, an empty pattern,
a pattern longer than `data`, or no match.

Normal example:

```java
int last = ByteUtilities.lastIndexOf(
    new byte[] {5, 6, 5, 6}, new byte[] {5, 6}); // 2
```

Edge example:

```java
int none = ByteUtilities.lastIndexOf(null, new byte[] {1}); // -1
```

### Error and Return Contract

This bounded API uses sentinel results rather than checked exceptions for malformed or
out-of-range inputs: `encode` and both `decode` overloads use `null` where specified,
GZIP checks use `false`, and pattern searches use `-1`. `toHexChar` accepts every integer
without throwing. Do not replace these sentinels with a different exception or with a
silently transformed value.

## Implementation Notes

### Cross-Module Constraints

Keep all listed public operations in `com.cedarsoftware.util.ByteUtilities`. The source path,
package declaration, and import path must remain aligned. There is no CLI, no `main` entry
point, and no required secondary module. Keep the POM free of runtime dependencies so offline
compilation is reproducible.

### Determinism and State

Use only the supplied arguments and Java SE behavior. Repeated calls with unchanged arguments
must return the same character, string, boolean, index, or byte contents. Do not mutate input
arrays during encoding, decoding, header checks, or searches. Do not cache results in mutable
static state. Byte order is always the original array order, and search results are determined
by the stated ascending or descending index order.

### Boundary Checklist

The following small examples must be explainable and verifiable from the public contract:

1. Encoding `{0x00, 0x7f, (byte) 0xff}` produces `"007FFF"`.
2. Decoding `"007fff"` produces three bytes with the same eight-bit values.
3. Decoding `"0"`, `"0x10"`, or `"GG"` returns `null`.
4. A GZIP pair at offset 1 is detected even when byte 0 is unrelated, while an offset with
   only one remaining byte returns `false`.
5. Forward search returns the first complete match and reverse search returns the last one.
6. Null arrays, empty patterns, negative search starts, and patterns that cannot fit return
   the documented sentinels without changing the arrays.

Do not hard-code only these examples. Implement the complete documented input domains and
preserve the overload distinctions, especially `String` versus `CharSequence` decoding and
the explicit offset/search-start arguments.

### Scope Boundary

Do not copy an upstream implementation, private verifier behavior, hidden test identifiers,
or internal harness protocols into the project. Do not add undocumented classes or methods
merely because they may exist in the full upstream library. No additional public API is
confidently bindable for this task beyond `ByteUtilities` and the signatures listed above.
