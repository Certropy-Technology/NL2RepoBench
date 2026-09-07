# Introduction and Goals of the Commons Compress Project

Apache Commons Compress is a Java library for working with archive formats.
This task focuses on the self-contained `ZipEightByteInteger` value object,
which represents an eight-byte little-endian ZIP integer and exposes both
signed `long` and unsigned `BigInteger` views. Recreate this bounded public API
as a normal single-module Maven project.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Compress that implements the
public behavior below:

1. Provide `org.apache.commons.compress.archivers.zip.ZipEightByteInteger`.
2. Convert `long` values to and from exactly eight little-endian bytes.
3. Expose the unsigned `BigInteger` value for all 64-bit bit patterns,
   including values whose sign bit is set.
4. Support construction from `long`, `BigInteger`, byte arrays, and byte arrays
   with an offset.
5. Preserve value equality, the corresponding hash code, the `ZERO` constant,
   and unsigned decimal `toString()` output.
6. Keep the implementation under `src/main/java` in a single-module Maven
   project. Do not add external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime and compiler
Maven 3.9.11                # Offline project metadata validation
Linux amd64                 # Fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # Agent and verifier are offline
```

## Commons Compress Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── commons
                        └── compress
                            └── archivers
                                └── zip
                                    └── ZipEightByteInteger.java
```

The public package is `org.apache.commons.compress.archivers.zip`. The
candidate POM is metadata only; do not use dependencies, plugins, profiles,
repositories, modules, or custom extensions to control the verifier.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import java.math.BigInteger;
import org.apache.commons.compress.archivers.zip.ZipEightByteInteger;
```

#### 2. Constructors - Create a ZIP Integer

```java
ZipEightByteInteger fromLong = new ZipEightByteInteger(42L);
ZipEightByteInteger fromBig = new ZipEightByteInteger(BigInteger.valueOf(42));
ZipEightByteInteger fromBytes = new ZipEightByteInteger(new byte[] {42, 0, 0, 0, 0, 0, 0, 0});
ZipEightByteInteger fromOffset = new ZipEightByteInteger(buffer, 2);
```

Signatures:

```java
ZipEightByteInteger(long value)
ZipEightByteInteger(BigInteger value)
ZipEightByteInteger(byte[] bytes)
ZipEightByteInteger(byte[] bytes, int offset)
```

The byte-array constructors read eight bytes in little-endian order. The
`BigInteger` constructor stores the low 64 bits, matching Java `long`
conversion behavior.

#### 3. getBytes() - Serialize in Little-Endian Order

```java
byte[] bytes = fromLong.getBytes();
byte[] bytes2 = ZipEightByteInteger.getBytes(42L);
byte[] bytes3 = ZipEightByteInteger.getBytes(BigInteger.valueOf(42));
```

Signatures:

```java
byte[] getBytes()
static byte[] getBytes(long value)
static byte[] getBytes(BigInteger value)
```

Every returned array has length eight. The least significant byte is first.

#### 4. getLongValue() and getValue() - Read Numeric Views

```java
long signed = fromBytes.getLongValue();
BigInteger unsigned = fromBytes.getValue();
long decoded = ZipEightByteInteger.getLongValue(bytes);
BigInteger decodedUnsigned = ZipEightByteInteger.getValue(bytes, 0);
```

Signatures:

```java
long getLongValue()
BigInteger getValue()
static long getLongValue(byte[] bytes)
static long getLongValue(byte[] bytes, int offset)
static BigInteger getValue(byte[] bytes)
static BigInteger getValue(byte[] bytes, int offset)
```

`getLongValue()` preserves the signed Java bit pattern. `getValue()` treats
that same pattern as unsigned, returning a value from zero through
`2^64 - 1`.

#### 5. ZERO, equals(), hashCode(), and toString()

```java
ZipEightByteInteger zero = ZipEightByteInteger.ZERO;
boolean same = zero.equals(new ZipEightByteInteger(0L));
int hash = zero.hashCode();
String text = new ZipEightByteInteger(-1L).toString();
```

`ZERO` represents numeric zero. Equality compares the stored 64-bit value;
equal values have equal hash codes. `toString()` returns the unsigned decimal
representation.

### Actual Usage Modes

#### Basic Conversion

```java
byte[] encoded = ZipEightByteInteger.getBytes(0x0102030405060708L);
long value = ZipEightByteInteger.getLongValue(encoded);
```

#### Unsigned Boundary

```java
ZipEightByteInteger value = new ZipEightByteInteger(-1L);
value.getValue();    // 18446744073709551615
value.toString();    // "18446744073709551615"
```

#### Offset Decoding

```java
byte[] buffer = {99, 99, 1, 2, 3, 4, 5, 6, 7, 8, 99};
long value = ZipEightByteInteger.getLongValue(buffer, 2);
```

### Supported Function Types

The supported function types are little-endian byte conversion, signed long
decoding, unsigned `BigInteger` decoding, offset-based decoding, constructors,
constant access, value equality, hash codes, and unsigned string formatting.
Archive readers, writers, compression codecs, filesystem access, and native
libraries are outside this task's contract.

### Error Handling

Preserve Java's normal array bounds behavior for null, short, or invalid-offset
byte arrays. Do not silently pad short input, change byte order, or discard
high bits beyond the low 64 bits accepted by the `BigInteger` constructor.

## Detailed Implementation Nodes of Functions

### Node 1: Little-Endian Encoding

Encode every `long` as eight bytes with the least significant byte first.

### Node 2: Long Decoding

Decode eight bytes into the exact signed Java `long` bit pattern.

### Node 3: Unsigned BigInteger View

Convert negative signed longs into their unsigned 64-bit `BigInteger` value and
leave non-negative values unchanged.

### Node 4: Offset Handling

Read from the requested offset without changing the source array or reading
outside its eight-byte window.

### Node 5: BigInteger Construction

Store the low 64 bits using Java `longValue()` semantics and serialize them in
the same way as a directly constructed long.

### Node 6: Value Object Semantics

Implement `ZERO`, equality, hash code, and unsigned decimal text consistently
for all 64-bit patterns.

### Node 7: Boundary Conditions

Cover zero, one, maximum signed long, minimum signed long, all bits set,
offsets, and invalid array lengths without inventing recovery behavior.

### Node 8: Offline Maven Layout

Use the exact public package, standard Maven source layout, Java 21, no external
runtime dependencies, and no network or candidate-controlled Maven settings.
