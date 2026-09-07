## Introduction and Goals of the Apache Commons BCEL Project

Apache Commons BCEL is a Java library for inspecting and manipulating Java
class files and bytecode. This task focuses on a small, deterministic public
slice of the library: `org.apache.bcel.util.ByteSequence`, a byte-array-backed
input stream used while reading class-file data. The implementation must
preserve Java `DataInputStream` behavior while exposing the BCEL-specific
cursor index.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons BCEL that implements the
following public behavior:

1. Provide the public class `org.apache.bcel.util.ByteSequence`.
2. Construct a sequence from a byte array without changing byte order or byte
   values.
3. Expose the current byte cursor through `getIndex()`.
4. Preserve the inherited `DataInputStream` read methods, including
   `readByte()`, `readUnsignedByte()`, `readUnsignedShort()`, `readInt()`, and
   `readFully(byte[])`.
5. Advance the cursor exactly by the number of bytes consumed and report EOF
   through the normal `IOException` behavior of Java input streams.
6. Keep the implementation under `src/main/java` in a single-module Maven
   project. Do not add external runtime dependencies or candidate-controlled
   build behavior.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java compilation and execution
Maven 3.9.11                # Offline project metadata validation
Linux amd64                 # Fixed execution platform
Runtime dependencies: none  # ByteSequence uses the Java standard library
Network access: unavailable # Agent and verifier are offline
```

## Apache Commons BCEL Project Architecture

### Project Directory Structure

```Plain
workspace/
├── pom.xml
└── src
    └── main
        └── java
            └── org
                └── apache
                    └── bcel
                        └── util
                            └── ByteSequence.java
```

The public package is `org.apache.bcel.util`. A candidate POM is metadata only:
do not add plugins, dependencies, profiles, repositories, modules, or custom
extensions to control compilation or verification.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import org.apache.bcel.util.ByteSequence;
```

#### 2. ByteSequence Constructor - Create a Cursor

```java
ByteSequence sequence = new ByteSequence(new byte[] {0x01, (byte) 0xff});
```

Signature:

```java
ByteSequence(byte[] bytes)
```

The sequence reads from the supplied bytes in array order. The constructor
must not reinterpret bytes as characters or reorder them.

#### 3. getIndex() - Read the Cursor

```java
int index = sequence.getIndex();
```

Signature:

```java
int getIndex()
```

The initial index is zero. After a successful read, the index equals the
number of bytes consumed. Reading beyond the end does not advance the index
past the available data.

#### 4. Inherited DataInputStream Reads

```java
int unsignedByte = sequence.readUnsignedByte();
int unsignedShort = sequence.readUnsignedShort();
int value = sequence.readInt();
byte signedByte = sequence.readByte();
```

The inherited methods use Java big-endian `DataInputStream` semantics. The
unsigned methods return non-negative integer values. `readFully(byte[])`
consumes exactly the destination length or throws `IOException` at EOF.

### Actual Usage Modes

#### Basic Sequential Reads

```java
ByteSequence sequence = new ByteSequence(new byte[] {1, 2, 3});
int first = sequence.readUnsignedByte();
int second = sequence.readUnsignedByte();
int position = sequence.getIndex();
```

#### Multi-byte Values

```java
ByteSequence sequence = new ByteSequence(new byte[] {0x01, 0x02, 0x03, 0x04});
int shortValue = sequence.readUnsignedShort(); // 0x0102
int intValue = sequence.readUnsignedShort();   // 0x0304
```

#### EOF Handling

```java
ByteSequence sequence = new ByteSequence(new byte[] {1});
sequence.readUnsignedByte();
// A further read follows DataInputStream's EOF IOException contract.
```

### Supported Function Types

The supported function types are byte-array construction, cursor inspection,
signed and unsigned byte reads, unsigned short reads, signed integer reads,
bulk reads, sequential cursor updates, and bounded EOF behavior.

### Error Handling

Null input, empty input, short input, and reads after exhaustion must follow
normal Java stream behavior. Do not return fabricated bytes, silently wrap the
cursor, or convert checked `IOException` failures into unrelated values.

## Detailed Implementation Nodes of Functions

### Node 1: Byte-array Construction

Wrap the supplied byte array in a stream that starts at index zero and keeps
the original byte order.

### Node 2: Cursor Tracking

Expose the current position through `getIndex()` and keep it synchronized with
successful stream reads.

### Node 3: Signed and Unsigned Reads

Preserve Java signed-byte and unsigned-byte return semantics, including values
whose high bit is set.

### Node 4: Big-endian Multi-byte Reads

Implement unsigned-short and integer reads with `DataInputStream` big-endian
behavior and exact cursor advancement.

### Node 5: Bulk Reads

Implement `readFully(byte[])` behavior for complete and truncated input,
including the corresponding cursor and exception results.

### Node 6: Empty and Boundary Inputs

Handle empty arrays and one-byte arrays deterministically. Do not read beyond
the available sequence or mutate the caller's expected data representation.

### Node 7: Maven Project Layout

Use the exact public package and standard Maven source layout. Compile with
Java 21 and no external runtime dependency.

### Node 8: Offline Build Behavior

Do not access the network or rely on candidate-controlled Maven configuration;
the implementation must work in the fixed offline verifier.
