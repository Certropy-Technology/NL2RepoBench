# Introduction and Goals of the Commons IO Project

Apache Commons IO is a Java library of utilities for input/output work. This
task isolates the deterministic, filesystem-free `EndianUtils` primitive
conversion helpers. Recreate the bounded public API as a normal single-module
Maven project; do not implement file operations, stream wrappers, or other
Commons IO modules.

## Natural Language Instruction (Prompt)

Create a Java Maven project named Commons IO that provides
`org.apache.commons.io.EndianUtils`. Implement the ten public static methods
listed below. They read and write primitive values in little-endian byte order
or reverse the byte order of an already decoded primitive. Use only the Java
standard library and keep implementation source under `src/main/java`.

## Environment Configuration

### Core Dependency Library Versions

```text
Temurin JDK 21.0.12+8
Maven 3.9.11 (offline metadata validation)
Linux amd64, glibc
Runtime dependencies: none
Network access: unavailable during agent, candidate, verifier, Oracle, and control execution
```

The candidate `pom.xml` is metadata only. It must not add dependencies,
plugins, profiles, repositories, modules, extensions, or custom test commands.
The verifier compiles the candidate in a separate JVM and owns all grading
reports.

## Commons IO Project Architecture

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/main/java/org/apache/commons/io/EndianUtils.java
```

The exact public type is `org.apache.commons.io.EndianUtils`. This bounded task
does not require a database, filesystem, network, native library, or external
Maven artifact.

## API Usage Guide

### Core APIs

All methods below are `public static` methods on
`org.apache.commons.io.EndianUtils`.

#### Byte-array readers

```java
int readSwappedInteger(byte[] data, int offset)
long readSwappedLong(byte[] data, int offset)
short readSwappedShort(byte[] data, int offset)
long readSwappedUnsignedInteger(byte[] data, int offset)
int readSwappedUnsignedShort(byte[] data, int offset)
```

Each reader starts at `offset` and consumes exactly 4, 8, 2, 4, or 2 bytes,
respectively. The least-significant byte is at the lowest index. Signed
methods preserve two's-complement Java values. Unsigned integer and short
methods return non-negative `long` and `int` values. The input array is not
modified. A null array, negative offset, or insufficient remaining bytes must
raise a runtime argument/bounds failure rather than padding or truncating the
input.

Examples:

```java
EndianUtils.readSwappedInteger(new byte[] { 0x78, 0x56, 0x34, 0x12 }, 0); // 0x12345678
EndianUtils.readSwappedUnsignedShort(new byte[] { (byte) 0xff, (byte) 0xff }, 0); // 65535
EndianUtils.readSwappedLong(new byte[] { 1, 0, 0, 0, 0, 0, 0, 0 }, 0); // 1L
```

#### Primitive byte swapping

```java
int swapInteger(int value)
long swapLong(long value)
short swapShort(short value)
```

These methods return the same primitive type with its byte order reversed.
They do not mutate state or access external resources. Applying a swap twice
returns the original bit pattern, including negative values.

```java
EndianUtils.swapInteger(0x12345678); // 0x78563412
EndianUtils.swapShort((short) 0x1234); // (short) 0x3412
```

#### Byte-array writers

```java
void writeSwappedInteger(byte[] data, int offset, int value)
void writeSwappedLong(byte[] data, int offset, long value)
```

Each writer stores exactly 4 or 8 little-endian bytes beginning at `offset`
and leaves all other bytes unchanged. A null array, negative offset, or
insufficient remaining space must fail instead of extending the array.

```java
byte[] data = new byte[6];
EndianUtils.writeSwappedInteger(data, 1, 0x12345678);
// data is {0, 0x78, 0x56, 0x34, 0x12, 0}
```

### Actual Usage Modes

Use the readers for decoding fixed-width binary headers, use the swapping
methods when a primitive was decoded in the opposite order, and use the
writers for creating fixed-width little-endian fields. All operations are
deterministic and local to the supplied primitive or byte array.

### Supported Function Types

The supported function types are fixed-width byte-array reads, unsigned
numeric reads, primitive byte reversal, and fixed-width byte-array writes.
Stream overloads, floating-point overloads, filesystem helpers, archive
helpers, charset handling, and process or network operations are outside the
contract.

### Error Handling

Preserve the public methods' normal runtime failure behavior for null arrays,
negative offsets, and ranges shorter than the required width. Do not silently
pad, wrap, or reinterpret a short buffer. A writer must not modify bytes
outside its requested window. No method may perform I/O or depend on the
machine's native byte order.

## Detailed Implementation Nodes of Functions

### Node 1: Little-endian signed reads

Read bytes in increasing index order, mask each byte to eight bits, and place
it at increasing multiples of eight. The 32-bit and 64-bit results retain
Java signed two's-complement semantics.

### Node 2: Little-endian unsigned reads

Decode four or two bytes without sign extension. Return the 32-bit result in a
`long` and the 16-bit result in an `int`, both in the inclusive ranges
`0..4294967295` and `0..65535`.

### Node 3: Primitive swapping

Reverse the eight-bit groups of the input while preserving the declared
primitive width. No arithmetic rounding or decimal conversion is involved.

### Node 4: Little-endian writes

Write the least-significant byte first into exactly the requested width. Keep
prefix and suffix sentinel bytes unchanged.

### Node 5: Offsets and boundaries

Offset zero, a non-zero offset with sentinel bytes, signed extrema, all-bit
patterns, null arrays, negative offsets, and too-short arrays are meaningful
boundaries. Do not read or write outside the specified window.

### Node 6: Determinism and state

All ten methods are stateless and deterministic. They return only the declared
primitive or mutate only the caller-provided writer array within its selected
range.

### Node 7: Source and package layout

Use the exact `org.apache.commons.io` package and `EndianUtils` type. The
project must compile with `javac --release 21` and the standard Maven layout.

### Node 8: Offline build behavior

Keep the Maven dependency closure empty and do not download artifacts at run
time. The trusted verifier invokes the candidate through a JSON/JVM adapter;
it does not import candidate classes into its own process.
