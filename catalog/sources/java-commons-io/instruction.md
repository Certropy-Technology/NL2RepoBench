## Project Description

Create a small Java Maven project named `commons-io` that recreates the
bounded, deterministic byte-order conversion slice of Apache Commons IO.
The required public type is `org.apache.commons.io.EndianUtils`. It reads and
writes fixed-width primitive values in little-endian order and reverses the
byte order of already decoded primitive values.

This is a library task, not a command-line application. The implementation
must be usable from another Java class through the exact package and method
names below. Keep the project focused on the ten methods in this contract.
Do not add unrelated Commons IO utilities, stream adapters, archive helpers,
filesystem operations, logging, network access, or third-party libraries.

The behavior is local to the supplied primitive values and byte arrays. It is
deterministic for the same arguments, independent of the host native byte
order, locale, current time, environment variables, and filesystem state.

### Natural Language Instruction (Prompt)

Implement the bounded `org.apache.commons.io.EndianUtils` API described in
this document. A caller must be able to compile the project with the declared
offline Maven environment, import the exact class, and use the ten static
methods without any external service or persistent state.

## Supports

Use Temurin JDK `21.0.12+8` and Maven `3.9.11` on Linux amd64 with glibc.
Runtime dependencies are empty: the implementation may use the Java standard
library, but it must not require a downloaded artifact. Candidate, verifier,
Oracle, and control execution is offline.

The public project layout is:

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/io/EndianUtils.java
```

The Maven file is metadata only. Use the standard Maven coordinates and keep
the dependency closure empty. The implementation source belongs under
`src/main/java`, and the public class must declare package
`org.apache.commons.io`.

There is no task CLI or `main` entry point. A caller should compile the Maven
project and import `org.apache.commons.io.EndianUtils`. Do not expose a
different package, a wrapper class, or a command-specific protocol as the
library API.

The import is exactly:

```java
import org.apache.commons.io.EndianUtils;
```

The supported function families are:

* signed little-endian reads for `int`, `long`, and `short`;
* unsigned little-endian reads returning widened non-negative values;
* primitive byte reversal for `int`, `long`, and `short`; and
* little-endian writes for `int` and `long` into caller-owned arrays.

For array operations, offsets are zero-based. A read consumes exactly the
width of its return type, and a write changes exactly the width of its value.
Bytes outside a write window remain unchanged. The methods do not resize,
copy, persist, or otherwise retain caller arrays.

## API Usage Guide

All ten methods are `public static` methods on the exact type
`org.apache.commons.io.EndianUtils`. The examples below are ordinary Java
expressions. They do not prescribe an internal algorithm; they specify the
observable contract.

### `readSwappedInteger`

Import path: `org.apache.commons.io.EndianUtils`.

Signature: `public static int readSwappedInteger(byte[] data, int offset)`.

The method reads four bytes at indexes `offset` through `offset + 3`, with
the lowest-addressed byte as the least-significant byte, and returns a signed
32-bit Java `int`. It does not mutate `data` and has no other side effect.
Ordering is fixed by the array indexes and therefore deterministic.

Normal example: `readSwappedInteger(new byte[] {0x78, 0x56, 0x34, 0x12}, 0)`
returns `0x12345678` (decimal `305419896`).

```java
int value = EndianUtils.readSwappedInteger(
    new byte[] {0x78, 0x56, 0x34, 0x12}, 0);
```

Edge example: `{0xff, 0xff, 0xff, 0xff}` returns `-1`, preserving the
two's-complement signed `int` bit pattern.

For a null array, the unchecked `NullPointerException` behavior is acceptable.
For a negative offset or an offset with fewer than four remaining bytes, the
method must fail with an unchecked bounds failure such as
`ArrayIndexOutOfBoundsException`; it must not pad, truncate, or silently wrap.

### `readSwappedLong`

Signature: `public static long readSwappedLong(byte[] data, int offset)`.

Read exactly eight little-endian bytes and return the signed 64-bit `long`.
The input array is not changed, and no state is retained. The byte at
`offset` contributes the least-significant eight bits.

Normal example: `readSwappedLong(new byte[] {1, 0, 0, 0, 0, 0, 0, 0}, 0)`
returns `1L`.

```java
long value = EndianUtils.readSwappedLong(
    new byte[] {1, 0, 0, 0, 0, 0, 0, 0}, 0);
```

Edge example: eight `0xff` bytes return `-1L`, not an unsigned decimal
string or a truncated value.

A null array raises unchecked `NullPointerException` behavior. A negative
offset or fewer than eight available bytes raises an unchecked bounds failure.
No checked exception is part of this method's contract.

### `readSwappedShort`

Signature: `public static short readSwappedShort(byte[] data, int offset)`.

Read exactly two bytes in little-endian order and return a signed Java
`short`. The returned value has the original 16-bit two's-complement pattern.
The array is read-only from this method's perspective.

Normal example: `readSwappedShort(new byte[] {0x34, 0x12}, 0)` returns
`(short) 0x1234`, or decimal `4660`.

Edge example: `{(byte) 0xfe, (byte) 0xff}` returns `(short) -2`.

Null input has unchecked `NullPointerException` behavior. A negative offset or
an offset not followed by two bytes has unchecked bounds-failure behavior.

### `readSwappedUnsignedInteger`

Signature: `public static long readSwappedUnsignedInteger(byte[] data, int offset)`.

Read four little-endian bytes without sign extension and return the unsigned
32-bit value widened to a non-negative `long`. The return range is inclusive
`0` through `4294967295`. No array mutation or external I/O occurs.

Normal example: `readSwappedUnsignedInteger(new byte[] {1, 0, 0, 0}, 0)`
returns `1L`.

Edge example: four `0xff` bytes return `4294967295L`, not `-1L`.

Null input raises unchecked `NullPointerException` behavior. A negative or
out-of-range offset raises an unchecked bounds failure; short input is not
accepted and is not padded. The method declares no checked exceptions.

### `readSwappedUnsignedShort`

Signature: `public static int readSwappedUnsignedShort(byte[] data, int offset)`.

Read two little-endian bytes without sign extension and return the unsigned
16-bit value as a non-negative `int`. The return range is inclusive `0`
through `65535`. The input array remains unchanged.

Normal example: `readSwappedUnsignedShort(new byte[] {(byte) 0xff, (byte) 0xff}, 0)`
returns `65535`.

Edge example: `{0, (byte) 0x80}` returns `32768`, not a negative `short`.

Null input has unchecked `NullPointerException` behavior. A negative offset or
fewer than two remaining bytes has unchecked bounds-failure behavior.

### `swapInteger`

Signature: `public static int swapInteger(int value)`.

Return a new `int` value whose four eight-bit groups are in reverse order.
The method does not access memory, mutate state, or perform I/O. Applying it
twice returns the original `int` bit pattern, including negative values.

Normal example: `swapInteger(0x12345678)` returns `0x78563412`.

Edge example: `swapInteger(-1)` returns `-1`; all four bytes are already
`0xff`. No checked or normal unchecked exception is expected for any `int`.

### `swapLong`

Signature: `public static long swapLong(long value)`.

Reverse the eight bytes of the supplied `long` and return the resulting
64-bit value. It is pure and deterministic; applying it twice restores the
input bit pattern.

Normal example: `swapLong(0x0102030405060708L)` returns
`0x0807060504030201L`.

Edge example: `swapLong(Long.MIN_VALUE)` returns `1L`, because only the most
significant input bit becomes the least-significant output bit. No checked
exception is declared or needed.

### `swapShort`

Signature: `public static short swapShort(short value)`.

Reverse the two bytes of the supplied 16-bit `short` and return a `short`.
The operation preserves the width and is pure, deterministic, and involutive.

Normal example: `swapShort((short) 0x1234)` returns `(short) 0x3412`.

Edge example: `swapShort((short) 0xff80)` returns `(short) 0x80ff`, with
Java signed interpretation preserved. Every `short` input is valid.

### `writeSwappedInteger`

Signature: `public static void writeSwappedInteger(byte[] data, int offset, int value)`.

Write exactly four bytes of `value` in little-endian order at indexes
`offset` through `offset + 3`. Return type is `void`. The only side effect is
the requested in-place mutation; prefix and suffix bytes remain unchanged.

Normal example: with `byte[] data = {0, 0, 0, 0, 0, 0}`, writing
`writeSwappedInteger(data, 1, 0x12345678)` produces
`{0, 0x78, 0x56, 0x34, 0x12, 0}`.

```java
byte[] data = {0, 0, 0, 0, 0, 0};
EndianUtils.writeSwappedInteger(data, 1, 0x12345678);
```

Edge example: writing `-1` into a four-byte window writes four `0xff` bytes
and must not alter a sentinel byte immediately before or after that window.

Null input has unchecked `NullPointerException` behavior. A negative offset
or fewer than four available bytes raises an unchecked bounds failure. The
method must not partially write outside the valid requested window.

### `writeSwappedLong`

Signature: `public static void writeSwappedLong(byte[] data, int offset, long value)`.

Write exactly eight little-endian bytes of `value` in place. The return value
is `void`; the array is the only mutable object and no reference is retained.
The operation is deterministic and leaves every byte outside the eight-byte
window unchanged.

Normal example: writing `0x0102030405060708L` at offset `1` in a ten-byte
array places `08 07 06 05 04 03 02 01` at indexes `1..8`.

Edge example: an array containing one sentinel byte on each side must retain
both sentinels after a valid write at offset `1`.

Null input raises unchecked `NullPointerException` behavior. A negative offset
or fewer than eight remaining bytes raises an unchecked bounds failure. There
is no checked exception and no implicit array growth.

## Implementation Notes

Keep the implementation in one public source file at
`src/main/java/org/apache/commons/io/EndianUtils.java` and use the exact
package declaration. A minimal `pom.xml` is sufficient; do not add a
dependency, plugin, repository, module, profile, or custom runtime command.

The ten methods must remain public, static, and callable without constructing
an `EndianUtils` instance. Do not change primitive return types to boxed types,
strings, arrays, or generic numbers. The unsigned methods widen to `long` and
`int` exactly as specified above.

All array reads and writes use the caller's zero-based offset. Valid boundary
cases include offset zero, a non-zero offset, an exact-width array, and a
larger array with sentinel bytes. Invalid cases include null arrays, negative
offsets, and insufficient remaining capacity. Preserve the normal unchecked
Java failure behavior for invalid array access rather than inventing padding,
clamping, or a separate error protocol.

The following small checks should be verifiable by a caller:

```java
EndianUtils.readSwappedInteger(new byte[] {0x78, 0x56, 0x34, 0x12}, 0)
// 305419896
EndianUtils.readSwappedUnsignedInteger(new byte[] {(byte) 0xff, (byte) 0xff,
    (byte) 0xff, (byte) 0xff}, 0)
// 4294967295L
EndianUtils.swapLong(0x0102030405060708L)
// 0x0807060504030201L
byte[] field = {(byte) 0xaa, 0, 0, 0, 0, (byte) 0xbb};
EndianUtils.writeSwappedInteger(field, 1, 0x12345678);
// aa 78 56 34 12 bb
```

A second boundary check should confirm that swapping twice restores the
original bits and that writing at a non-zero offset leaves both sentinels
unchanged. A third should confirm the unsigned maximum values `4294967295L`
and `65535`. A fourth should exercise a short or null array and observe an
unchecked failure rather than a fabricated result.

Do not implement a CLI: `task.toml` declares no command-line entry point.
Do not add stream overloads, floating-point overloads, file operations,
archive operations, charset APIs, or other Commons IO classes. The synthetic
`IOUtils` helper used by the harness is not part of the requested public
contract.

The following items are intentionally not confidently bindable from the
task-local contract and must not be invented: any Commons IO type other than
`EndianUtils`, overloads not listed in this document, constructors or
instance state, CLI flags, and behavior of the upstream project's unrelated
modules. Keep the solution limited to the ten documented methods.

Build and test offline with the declared JDK/Maven versions. The verifier may
invoke the candidate in a separate JVM, so do not rely on verifier classpath
state, static initialization in another process, native byte order, or network
access. The implementation must compile under Java release 21 and produce no
trusted reports, grading files, or generated artifacts in the workspace.
