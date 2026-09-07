## Project Description

Create a single-module Java Maven project that recreates the bounded public
behavior of Apache Commons Compress's `ZipEightByteInteger` value object.

The project is a small, deterministic compatibility implementation, not a
general archive utility. The required public class is
`org.apache.commons.compress.archivers.zip.ZipEightByteInteger`.

The value object represents exactly eight bytes in ZIP little-endian order.
It must preserve the same 64-bit bit pattern when values are encoded and
decoded. The signed Java `long` view and the unsigned `BigInteger` view are
two interpretations of that one bit pattern.

The implementation must be placed at:

```text
workspace/src/main/java/org/apache/commons/compress/archivers/zip/ZipEightByteInteger.java
```

Use a normal single-module Maven layout with a metadata-only `pom.xml`.
The candidate project must compile with the specified JDK and Maven versions
without downloading dependencies. Do not add archive readers, writers,
compression codecs, filesystem behavior, command-line interfaces, or native
code. Those features are outside this task's public contract.

The implementation must be self-contained and use only Java standard-library
types needed by the documented API, principally `java.math.BigInteger`.

### Natural Language Instruction

Implement the described `ZipEightByteInteger` class in a Java 21 Maven
project. Reproduce its exact eight-byte little-endian conversion behavior,
signed `long` and unsigned `BigInteger` views, constructors, constant, and
value-object methods. Keep the implementation deterministic, offline, and
self-contained under the exact package and Maven layout below. Do not add
unrelated archive features or dependencies.

## Supports

### Environment and build contract

The fixed build environment is:

```text
Operating system: Debian Bookworm, Linux amd64
JDK: Temurin 21.0.12+8
Maven: 3.9.11
Runtime dependency closure: empty
Agent network: unavailable
Candidate network: unavailable
Verifier network: unavailable
```

The project must compile as Java 21 source under Maven. Keep the project
single-module and keep production code under `src/main/java`. A POM may carry
the project coordinates and compiler metadata required for the build, but it
must not use repositories, plugins, profiles, modules, custom extensions, or
network access to influence the result.

### Project directory structure

The candidate workspace must have this shape:

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── compress/
                            └── archivers/
                                └── zip/
                                    └── ZipEightByteInteger.java
```

The package declaration must be:

```java
package org.apache.commons.compress.archivers.zip;
```

The public API is intentionally limited to the class and members described in
the API Usage Guide. Do not create a replacement package, an alternate class
with the same behavior, or a CLI entry point.

### Supported behavior

Support all of the following behavior:

1. Constructing a value from a signed `long`.
2. Constructing a value from a `BigInteger` using the low-64-bit Java
   `longValue()` interpretation.
3. Constructing a value from eight bytes beginning at offset zero.
4. Constructing a value from eight bytes beginning at a supplied offset.
5. Serializing a value to exactly eight little-endian bytes.
6. Serializing a `long` or `BigInteger` through the corresponding static
   helpers.
7. Reading the signed `long` bit pattern from an instance or byte array.
8. Reading the same bit pattern as an unsigned `BigInteger` from an instance
   or byte array.
9. Exposing the `ZERO` constant.
10. Value-based `equals`, matching `hashCode`, and unsigned decimal
    `toString` behavior.

### Determinism and state

The class is a value object. For a fixed constructor input, every accessor
must return the same result on every call. Serialization must not mutate the
object or the caller's input array. Static helpers must not retain global
state, use the clock, use randomness, inspect the filesystem, or perform
network access.

There are no checked exceptions in the documented API. Preserve ordinary
unchecked Java behavior for invalid null arrays, short arrays, invalid offsets,
and null `BigInteger` arguments. Do not silently pad input, truncate a byte
window, or invent a recovery value for invalid input.

## API Usage Guide

### Imports and class identity

Use these imports for the complete documented API:

```java
import java.math.BigInteger;
import org.apache.commons.compress.archivers.zip.ZipEightByteInteger;
```

The one confidently bindable public class is:

```java
public class org.apache.commons.compress.archivers.zip.ZipEightByteInteger
```

No CLI is documented for this task. No other public class is part of the
contract.

### `ZERO` constant

The class exposes the canonical zero value:

```java
public static final ZipEightByteInteger ZERO
```

`ZERO` represents the 64-bit pattern whose eight bytes are all zero. It is a
value, so callers must compare it with `equals` or compare numeric accessors;
do not require object identity for separately constructed zero values.

Normal example:

```java
ZipEightByteInteger zero = ZipEightByteInteger.ZERO;
assert zero.getLongValue() == 0L;
assert zero.getValue().equals(BigInteger.ZERO);
```

Edge example:

```java
assert ZipEightByteInteger.ZERO.equals(new ZipEightByteInteger(0L));
```

The constant has no side effects and is deterministic.

### `ZipEightByteInteger(long)` constructor

Construct an instance from the exact 64-bit Java `long` pattern:

```java
public ZipEightByteInteger(long value)
```

The input domain is every Java `long`, including `0L`, `Long.MAX_VALUE`,
`Long.MIN_VALUE`, and `-1L`. The constructor stores the bits, not a decimal
text representation. It returns a new `ZipEightByteInteger` instance and has
no external side effects.

Normal example:

```java
ZipEightByteInteger number = new ZipEightByteInteger(42L);
assert number.getLongValue() == 42L;
```

Edge example:

```java
ZipEightByteInteger allBitsSet = new ZipEightByteInteger(-1L);
assert allBitsSet.getLongValue() == -1L;
assert allBitsSet.getValue().equals(new BigInteger("18446744073709551615"));
```

The constructor throws no checked exception and has no invalid `long` input.

### `ZipEightByteInteger(BigInteger)` constructor

Construct an instance from a `BigInteger`:

```java
public ZipEightByteInteger(java.math.BigInteger value)
```

The input domain is a non-null `BigInteger`. Store the low 64 bits according
to `BigInteger.longValue()` semantics. Values outside the signed-long range
are therefore represented by the corresponding Java `long` bit pattern; do
not reject them merely because they are larger than `Long.MAX_VALUE`.

Normal example:

```java
ZipEightByteInteger number =
    new ZipEightByteInteger(BigInteger.valueOf(42L));
assert number.getLongValue() == 42L;
```

Edge example:

```java
BigInteger unsignedMax = new BigInteger("18446744073709551615");
ZipEightByteInteger number = new ZipEightByteInteger(unsignedMax);
assert number.getLongValue() == -1L;
assert number.getValue().equals(unsignedMax);
```

A null `BigInteger` is invalid and must retain ordinary unchecked null-input
behavior. There are no checked exceptions or side effects.

### `ZipEightByteInteger(byte[])` constructor

Construct an instance by reading eight bytes from the beginning of an array:

```java
public ZipEightByteInteger(byte[] bytes)
```

The method reads `bytes[0]` through `bytes[7]` as an unsigned little-endian
encoding of one 64-bit pattern. The input array may be longer than eight
bytes; bytes after index seven are ignored. The source array is not mutated.

Normal example:

```java
byte[] bytes = {42, 0, 0, 0, 0, 0, 0, 0};
ZipEightByteInteger number = new ZipEightByteInteger(bytes);
assert number.getLongValue() == 42L;
```

Edge example:

```java
byte[] bytes = {(byte) 0xff, (byte) 0xff, (byte) 0xff, (byte) 0xff,
                (byte) 0xff, (byte) 0xff, (byte) 0xff, (byte) 0xff};
assert new ZipEightByteInteger(bytes).getValue()
    .equals(new BigInteger("18446744073709551615"));
```

A null or shorter-than-eight array is invalid. Preserve the normal unchecked
array/null failure rather than padding or returning a partial value.

### `ZipEightByteInteger(byte[], int)` constructor

Construct an instance from an eight-byte window at an offset:

```java
public ZipEightByteInteger(byte[] bytes, int offset)
```

Read `bytes[offset]` through `bytes[offset + 7]` in little-endian order. The
offset is measured in bytes and may be zero or any value for which the full
eight-byte window fits. Bytes outside that window are ignored and the source
array is not changed.

Normal example:

```java
byte[] buffer = {99, 99, 1, 2, 3, 4, 5, 6, 7, 8, 99};
ZipEightByteInteger number = new ZipEightByteInteger(buffer, 2);
assert number.getLongValue() == 0x0807060504030201L;
```

Edge example:

```java
byte[] buffer = new byte[9];
// offset 2 cannot provide bytes 2 through 9.
// It must fail rather than reading outside the array or padding the value.
```

Null arrays, negative offsets, and offsets whose eight-byte window exceeds the
array are invalid and retain ordinary unchecked Java array/index behavior.

### `getBytes()` instance method

Serialize the stored 64-bit pattern:

```java
public byte[] getBytes()
```

Return a new array of exactly length eight. Byte zero is the least significant
byte, and byte seven is the most significant byte. Repeated calls return equal
contents without exposing mutable internal state.

Normal example:

```java
byte[] bytes = new ZipEightByteInteger(0x0102030405060708L).getBytes();
assert bytes.length == 8;
assert bytes[0] == 0x08;
assert bytes[7] == 0x01;
```

Edge example:

```java
byte[] bytes = new ZipEightByteInteger(Long.MIN_VALUE).getBytes();
assert bytes[0] == 0;
assert bytes[7] == (byte) 0x80;
```

The method has no checked exceptions, mutates no state, and performs no I/O.

### `getBytes(long)` static method

Encode a signed Java `long` as eight little-endian bytes:

```java
public static byte[] getBytes(long value)
```

Accept every `long`. Return a new eight-byte array containing the exact bit
pattern, least significant byte first.

Normal example:

```java
byte[] bytes = ZipEightByteInteger.getBytes(0x0102030405060708L);
assert bytes[0] == 0x08;
assert bytes[7] == 0x01;
```

Edge example:

```java
byte[] bytes = ZipEightByteInteger.getBytes(-1L);
for (byte value : bytes) assert value == (byte) 0xff;
```

The method has no checked exceptions, global state, or side effects.

### `getBytes(BigInteger)` static method

Encode a `BigInteger` using its low-64-bit `longValue()` interpretation:

```java
public static byte[] getBytes(java.math.BigInteger value)
```

Return exactly eight little-endian bytes. A value larger than the signed-long
range is reduced to the same low 64 bits that the BigInteger constructor uses.

Normal example:

```java
byte[] bytes = ZipEightByteInteger.getBytes(BigInteger.valueOf(42L));
assert bytes[0] == 42;
assert bytes[1] == 0;
```

Edge example:

```java
byte[] bytes = ZipEightByteInteger.getBytes(
    new BigInteger("18446744073709551615"));
for (byte value : bytes) assert value == (byte) 0xff;
```

A null argument is invalid and retains ordinary unchecked null behavior. There
are no checked exceptions or external side effects.

### `getLongValue()` instance method

Read the stored pattern as a signed Java `long`:

```java
public long getLongValue()
```

Return the exact two's-complement `long` represented by the stored bits. This
does not reinterpret negative values as positive numbers.

Normal example:

```java
assert new ZipEightByteInteger(123L).getLongValue() == 123L;
```

Edge example:

```java
assert new ZipEightByteInteger(
    new byte[] {0, 0, 0, 0, 0, 0, 0, (byte) 0x80})
    .getLongValue() == Long.MIN_VALUE;
```

The method has no checked exceptions, mutation, or I/O.

### `getValue()` instance method

Read the stored pattern as an unsigned `BigInteger`:

```java
public java.math.BigInteger getValue()
```

Return a non-negative `BigInteger` in the inclusive range zero through
`18446744073709551615`. The result is a numeric copy and does not expose
mutable object state.

Normal example:

```java
assert new ZipEightByteInteger(42L).getValue()
    .equals(BigInteger.valueOf(42L));
```

Edge example:

```java
assert new ZipEightByteInteger(-1L).getValue()
    .equals(new BigInteger("18446744073709551615"));
```

The method has no checked exceptions, mutation, or external side effects.

### `getLongValue(byte[])` static method

Decode eight bytes at offset zero as a signed `long`:

```java
public static long getLongValue(byte[] bytes)
```

Read bytes zero through seven in little-endian order and return the exact
signed two's-complement result. A longer array is permitted; trailing bytes
are ignored.

Normal example:

```java
byte[] bytes = {1, 0, 0, 0, 0, 0, 0, 0};
assert ZipEightByteInteger.getLongValue(bytes) == 1L;
```

Edge example:

```java
byte[] bytes = {0, 0, 0, 0, 0, 0, 0, (byte) 0x80};
assert ZipEightByteInteger.getLongValue(bytes) == Long.MIN_VALUE;
```

Null or short arrays are invalid and retain ordinary unchecked array behavior.

### `getLongValue(byte[], int)` static method

Decode an eight-byte window as a signed `long`:

```java
public static long getLongValue(byte[] bytes, int offset)
```

Read from `offset` through `offset + 7`, in little-endian order, without
changing the source array. The returned value is the signed interpretation of
the complete 64-bit pattern.

Normal example:

```java
byte[] buffer = {9, 9, 8, 7, 6, 5, 4, 3, 2, 1, 9};
assert ZipEightByteInteger.getLongValue(buffer, 2)
    == 0x0102030405060708L;
```

Edge example:

```java
byte[] buffer = new byte[8];
// offset 1 is invalid because the requested window would need byte 8.
```

Null arrays, negative offsets, and incomplete windows are invalid and must not
be padded or silently truncated.

### `getValue(byte[])` static method

Decode eight bytes at offset zero as an unsigned `BigInteger`:

```java
public static java.math.BigInteger getValue(byte[] bytes)
```

Read exactly the first eight bytes in little-endian order and return a value
from zero through `2^64 - 1`. The input array is not modified.

Normal example:

```java
byte[] bytes = {1, 2, 0, 0, 0, 0, 0, 0};
assert ZipEightByteInteger.getValue(bytes)
    .equals(BigInteger.valueOf(0x0201L));
```

Edge example:

```java
byte[] bytes = {(byte) 0xff, (byte) 0xff, (byte) 0xff, (byte) 0xff,
                (byte) 0xff, (byte) 0xff, (byte) 0xff, (byte) 0xff};
assert ZipEightByteInteger.getValue(bytes).bitLength() == 64;
```

Null or short arrays are invalid and retain ordinary unchecked array behavior.

### `getValue(byte[], int)` static method

Decode an offset-based eight-byte window as an unsigned `BigInteger`:

```java
public static java.math.BigInteger getValue(byte[] bytes, int offset)
```

Read bytes `offset` through `offset + 7` in little-endian order. Return a
non-negative `BigInteger` and ignore bytes outside that window.

Normal example:

```java
byte[] buffer = {0, 0, 1, 0, 0, 0, 0, 0, 0, 0};
assert ZipEightByteInteger.getValue(buffer, 2)
    .equals(BigInteger.ONE);
```

Edge example:

```java
byte[] buffer = new byte[8];
// A negative offset or offset 1 must fail; neither may be normalized to zero.
```

Null arrays and offsets without a complete eight-byte window are invalid and
retain ordinary unchecked Java behavior.

### `equals(Object)` method

Compare value objects by their stored 64-bit pattern:

```java
public boolean equals(java.lang.Object other)
```

Return true for another `ZipEightByteInteger` with the same bits, including
values that have different signed/unsigned textual interpretations only when
their bits are actually equal. Return false for null, unrelated types, or a
different 64-bit pattern. The method does not mutate either object.

Normal example:

```java
assert new ZipEightByteInteger(7L)
    .equals(new ZipEightByteInteger(7L));
```

Edge example:

```java
assert !new ZipEightByteInteger(7L).equals(Long.valueOf(7L));
assert !new ZipEightByteInteger(7L).equals(null);
```

### `hashCode()` method

Return the value-based hash code for the stored pattern:

```java
public int hashCode()
```

Equal `ZipEightByteInteger` instances must have equal hash codes. The exact
hash formula is part of Java object behavior but callers must rely primarily
on the equality/hashCode contract, not on a particular distribution.

Normal example:

```java
ZipEightByteInteger a = new ZipEightByteInteger(7L);
ZipEightByteInteger b = new ZipEightByteInteger(7L);
assert a.hashCode() == b.hashCode();
```

Edge example:

```java
assert ZipEightByteInteger.ZERO.hashCode()
    == new ZipEightByteInteger(0L).hashCode();
```

### `toString()` method

Render the stored value as unsigned decimal text:

```java
public java.lang.String toString()
```

Return a deterministic base-10 string with no sign prefix for any 64-bit
pattern. Zero renders as `"0"`; a negative signed `long` is rendered as its
corresponding value in the range above `Long.MAX_VALUE`.

Normal example:

```java
assert new ZipEightByteInteger(42L).toString().equals("42");
```

Edge example:

```java
assert new ZipEightByteInteger(-1L).toString()
    .equals("18446744073709551615");
```

### Error and boundary contract

The byte APIs require a complete eight-byte window. Do not reverse the byte
order, sign-extend individual bytes incorrectly, silently pad short input, or
read past the requested window. Invalid null, negative-offset, short-array,
and out-of-range inputs must fail with ordinary unchecked Java behavior; no
checked exception contract is required.

The BigInteger APIs preserve low-64-bit `longValue()` semantics. This means a
large positive BigInteger can become a negative signed `long` while retaining
the expected unsigned `getValue()` result. Do not clamp, reject, or round such
values.

## Implementation Notes

### Cross-module and package constraints

Keep all production behavior in the one public class and the exact package
`org.apache.commons.compress.archivers.zip`. The class may use standard-library
implementation details, but it must not require Apache Commons dependencies
or any other runtime artifact. Do not add a second implementation under a
different package and do not expose private helper types as task APIs.

The POM is build metadata only. Maven must operate offline, and the candidate
must not download artifacts, invoke external commands, read environment secrets,
or access the filesystem beyond normal compilation behavior.

### Byte representation constraints

Every encoding is exactly eight bytes, little-endian. For a value whose
lowest eight bits are `0x08` and whose next byte is `0x07`, the first two
serialized bytes are `0x08, 0x07`. Java byte signedness must not change the
underlying bit pattern.

Decoding an offset must consume exactly eight bytes starting at that offset.
The caller's array may contain prefix and suffix sentinels; those sentinels
must have no effect on the result.

### Numeric and object constraints

Treat the object as immutable after construction. Each `getBytes()` result
must be independent so that mutating a returned array cannot alter a later
result. Numeric accessors must agree on the same stored bits:

```java
ZipEightByteInteger value = new ZipEightByteInteger(-1L);
assert value.getLongValue() == -1L;
assert value.getValue().equals(new BigInteger("18446744073709551615"));
assert value.toString().equals("18446744073709551615");
```

### Small verifiable examples

The following examples summarize the expected observable behavior:

```java
ZipEightByteInteger one = new ZipEightByteInteger(1L);
assert java.util.Arrays.equals(
    one.getBytes(), new byte[] {1, 0, 0, 0, 0, 0, 0, 0});
```

```java
byte[] window = {99, 1, 2, 3, 4, 5, 6, 7, 8, 99};
assert ZipEightByteInteger.getLongValue(window, 1)
    == 0x0807060504030201L;
```

```java
ZipEightByteInteger boundary = new ZipEightByteInteger(Long.MIN_VALUE);
assert boundary.getValue().equals(new BigInteger("9223372036854775808"));
assert boundary.toString().equals("9223372036854775808");
```

```java
ZipEightByteInteger fromBig = new ZipEightByteInteger(
    new BigInteger("18446744073709551616"));
assert fromBig.getLongValue() == 0L;
assert fromBig.equals(ZipEightByteInteger.ZERO);
```

These examples are behavior checks, not an implementation algorithm. Choose
any clear implementation that satisfies the public contract without copying
the reference source or relying on hidden verifier details.

### Out-of-scope behavior

Do not implement or document archive extraction, archive creation, ZIP entry
processing, compression streams, filesystem operations, command-line flags,
network services, native integrations, or classes that are not confidently
bindable to this task's public contract. No private test names, grader paths,
Oracle files, verifier entrypoints, or reference-source retrieval mechanisms
belong in the candidate implementation or its public instruction.
