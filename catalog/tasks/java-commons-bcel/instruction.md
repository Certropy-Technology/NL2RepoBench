## Project Description

Create a small, installable Java Maven project named Apache Commons BCEL.
The project recreates the bounded byte-sequence behavior required by this task.
It is intended for code that reads class-file or other binary data in a stable,
forward-only cursor while retaining the ordinary Java data-input contracts.

The public package is `org.apache.bcel.util`.
The public type required by this task is `ByteSequence`.
`ByteSequence` is a final stream-like class backed by a caller-provided byte
array and exposes the number of bytes consumed through `getIndex()`.

The implementation must preserve byte values and their array order.
Multi-byte values must use the big-endian behavior of `DataInputStream`.
Successful reads advance the cursor by exactly the number of bytes consumed.
Reads that cannot obtain all required bytes must report the normal checked
`IOException` contract rather than returning fabricated data.

This is a bounded library task, not a request to recreate every Apache BCEL
package or every class-file manipulation feature.
Do not add unrelated BCEL classes, a command-line application, a network
client, a bytecode optimizer, or a custom serialization format.
Do not copy a complete upstream source tree into the candidate workspace.

The candidate starts from an empty `workspace/` directory.
It must create a compilable single-module Maven project whose source layout,
package name, constructor, cursor method, and inherited read behavior match
the contract in this document.

## Supports

### Natural Language Instruction

Implement the following observable capabilities.

1. Create `org.apache.bcel.util.ByteSequence` as a public final Java class.
2. Make the class extend `java.io.DataInputStream` so its standard data-input
   methods remain available with their normal signatures and checked errors.
3. Accept a `byte[]` in the public constructor and read it in its original
   order without converting bytes through characters or text encodings.
4. Expose the current zero-based byte position through `public int getIndex()`.
5. Preserve signed-byte, unsigned-byte, unsigned-short, and signed-integer
   `DataInputStream` semantics, including big-endian multi-byte decoding.
6. Preserve complete-read behavior for `readFully`, including its EOF error
   and cursor behavior when the requested range is truncated.
7. Keep the build deterministic and offline with no runtime dependencies.

The Java package declaration must be exactly `org.apache.bcel.util`.
The public class name and constructor must be exactly `ByteSequence`.
The Maven coordinates may identify the project as Commons BCEL, but the POM
must remain metadata for a single module and must not install build behavior
that bypasses the verifier.

### Environment Configuration

Use the fixed environment below when compiling and checking the project.

| Component | Required value |
| --- | --- |
| Operating system | Debian Bookworm, Linux amd64 |
| Java runtime | Temurin JDK 21.0.12+8 |
| Java language level | `--release 21` / Java 21 |
| Package manager | Maven 3.9.11 |
| Runtime dependencies | None; use the Java standard library |
| Network policy | No network during agent, candidate, verifier, or Oracle execution |

Use Maven's offline mode for validation:
`mvn --offline validate`.
Do not access GitHub, Maven Central, DNS, or any other external service at
build or runtime.
Do not add repositories, plugins, profiles, modules, or dependencies merely
to make the candidate reach the verifier.

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── bcel/
                        └── util/
                            └── ByteSequence.java
```

The directory tree is intentionally small.
The package path must correspond to the import path in the API guide.
No CLI entry point is required for this library task.
No resource directory, service loader, shell script, or network configuration
is required.

## API Usage Guide

### `org.apache.bcel.util.ByteSequence`

Import the class with:

```java
import org.apache.bcel.util.ByteSequence;
```

The class is public and final.
It extends `java.io.DataInputStream`.
The underlying input is a byte-array cursor, not a file, socket, or text
reader.
The cursor starts at zero and is shared by all reads on the object.

#### Constructor: `ByteSequence(byte[] bytes)`

Full declaration:

```java
public ByteSequence(byte[] bytes)
```

`bytes` is the source byte array.
Every element is consumed as its eight-bit byte value.
The first element is read first, the second element second, and so on.
The constructor has no network, filesystem, or process side effect.
It does not decode the array as UTF-8, Latin-1, or any other character set.
The initial cursor index is zero, including for an empty array.

Normal example:

```java
ByteSequence sequence = new ByteSequence(
    new byte[] {0x01, 0x02, 0x03, (byte) 0xff});
int initial = sequence.getIndex(); // 0
```

Edge example:

```java
ByteSequence empty = new ByteSequence(new byte[0]);
int initial = empty.getIndex(); // 0
```

An empty array is valid and has no readable bytes.
A null array is invalid and is rejected by the underlying byte-array stream
construction with an unchecked null-related failure; it must not be treated
as an empty array.

#### Cursor inspection: `getIndex()`

Full declaration:

```java
public int getIndex()
```

The method returns the zero-based number of bytes consumed from the original
array.
Its return type is `int`.
It has no arguments and no external side effect.
It is deterministic for a given sequence of successful and attempted reads.
Immediately after construction it returns `0`.
After a successful one-byte read it returns `1`.
After a successful four-byte read it increases by `4`.
It must never report a position beyond the source array length.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {10, 20});
sequence.readUnsignedByte();
int position = sequence.getIndex(); // 1
```

Boundary example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {10});
sequence.readUnsignedByte();
int position = sequence.getIndex(); // 1
```

An unsuccessful read at end of input must not move the index past the end.

#### Inherited signed byte read: `readByte()`

Full declaration inherited from `DataInputStream`:

```java
public final byte readByte() throws IOException
```

Add `import java.io.IOException;` when handling the checked exception.
The method consumes exactly one byte and returns it as a signed Java `byte`.
For example, the byte value `0xFF` is returned as `-1`.
It advances the cursor by one only when a byte is available.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {(byte) 0xff});
byte value = sequence.readByte(); // -1
int position = sequence.getIndex(); // 1
```

Edge example:

```java
ByteSequence sequence = new ByteSequence(new byte[0]);
try {
    sequence.readByte();
    throw new AssertionError("expected EOF");
} catch (IOException expected) {
    // The index remains 0.
}
```

#### Inherited unsigned byte read: `readUnsignedByte()`

Full declaration inherited from `DataInputStream`:

```java
public final int readUnsignedByte() throws IOException
```

The method consumes exactly one byte and returns an `int` in the range
`0` through `255`.
The high bit is not interpreted as a sign bit.
It is deterministic and advances the cursor by one on success.
At EOF it throws `IOException` and does not fabricate a value.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {(byte) 0xff});
int value = sequence.readUnsignedByte(); // 255
```

Edge example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {7});
sequence.readUnsignedByte();
try {
    sequence.readUnsignedByte();
    throw new AssertionError("expected EOF");
} catch (IOException expected) {
    // The index remains 1.
}
```

#### Inherited unsigned short read: `readUnsignedShort()`

Full declaration inherited from `DataInputStream`:

```java
public final int readUnsignedShort() throws IOException
```

The method requires two bytes.
It interprets them in network order, which is Java `DataInputStream`
big-endian order: the first byte is the high eight bits.
The return type is `int` with a value from `0` through `65535`.
On success the cursor advances by two.
If fewer than two bytes remain, it throws `IOException` and must not claim a
successful two-byte value.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {0x01, 0x02});
int value = sequence.readUnsignedShort(); // 258 (0x0102)
int position = sequence.getIndex(); // 2
```

Edge example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {0x01});
try {
    sequence.readUnsignedShort();
    throw new AssertionError("expected EOF");
} catch (IOException expected) {
    // The request was not satisfied; do not invent the missing low byte.
}
```

#### Inherited signed integer read: `readInt()`

Full declaration inherited from `DataInputStream`:

```java
public final int readInt() throws IOException
```

The method requires four bytes and decodes them in big-endian order.
The returned value is a signed Java `int` using the standard two's-complement
interpretation.
On success the cursor advances by four.
It throws `IOException` when fewer than four bytes remain.
There is no rounding, text conversion, locale behavior, or byte swapping.

Normal example:

```java
ByteSequence sequence = new ByteSequence(
    new byte[] {0x01, 0x02, 0x03, 0x04});
int value = sequence.readInt(); // 0x01020304
int position = sequence.getIndex(); // 4
```

Edge example:

```java
ByteSequence sequence = new ByteSequence(
    new byte[] {(byte) 0xff, (byte) 0xff, (byte) 0xff});
try {
    sequence.readInt();
    throw new AssertionError("expected EOF");
} catch (IOException expected) {
    // A three-byte prefix is not an integer.
}
```

#### Inherited complete read: `readFully(byte[] b)`

Full declaration inherited from `DataInputStream`:

```java
public final void readFully(byte[] b) throws IOException
```

The destination array `b` receives exactly `b.length` bytes.
The method returns `void` and advances the source cursor by that length on a
successful call.
It does not append a terminator or stop at a zero byte.
If the source ends before the destination is full, it throws `IOException`.
The implementation must preserve the standard `DataInputStream` behavior for
the destination reference and the available byte count.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {1, 2, 3});
byte[] destination = new byte[2];
sequence.readFully(destination);
// destination is {1, 2}; sequence.getIndex() is 2.
```

Edge example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {1});
byte[] destination = new byte[2];
try {
    sequence.readFully(destination);
    throw new AssertionError("expected EOF");
} catch (IOException expected) {
    // The call reports a truncated complete-read request.
}
```

#### Inherited ranged complete read: `readFully(byte[], int, int)`

Full declaration inherited from `DataInputStream`:

```java
public final void readFully(byte[] b, int off, int len) throws IOException
```

The method fills `len` destination elements beginning at `off`.
`off` and `len` must describe a valid range in `b`.
The source cursor advances by `len` only for bytes successfully consumed.
An invalid destination range follows the standard unchecked argument/index
failure of the JDK method; a truncated source follows `IOException`.

Normal example:

```java
ByteSequence sequence = new ByteSequence(new byte[] {4, 5, 6});
byte[] destination = new byte[] {0, 0, 0, 0};
sequence.readFully(destination, 1, 2);
// destination is {0, 4, 5, 0}; index is 2.
```

Zero-length example:

```java
ByteSequence sequence = new ByteSequence(new byte[0]);
byte[] destination = new byte[2];
sequence.readFully(destination, 1, 0);
// No source byte is consumed and index remains 0.
```

### Not confidently bindable

The complete upstream BCEL source contains many additional public symbols.
This task's frozen solution and selected contract do not bind those symbols.
Do not invent or implement additional BCEL classes such as class-file
parsers, constant-pool entries, instruction visitors, or repository CLIs.
The only confidently bindable class is `ByteSequence`; all other upstream
public symbols are intentionally not confidently bindable for this task.

## Implementation Notes

Keep the implementation in one Maven module with the exact package path shown
above.
Use Java standard-library stream composition or an equivalent implementation
that preserves the documented `DataInputStream` contract.
The cursor must be derived from successful consumption of the backing byte
stream, not from a second counter that can diverge from the actual stream.

Do not mutate the byte values or reinterpret them according to the platform
endianness.
The observable multi-byte order is always big-endian.
Repeated calls on the same object continue from the current cursor.
Separate `ByteSequence` objects have independent cursor state.

A successful one-byte operation moves the cursor by one.
A successful unsigned-short operation moves it by two.
A successful integer operation moves it by four.
A successful complete read moves it by the requested length.
An EOF operation must never report bytes that were not present.

The implementation must remain deterministic for identical byte arrays and
identical method-call sequences.
It must not consult the clock, locale, default charset, environment, network,
filesystem, or random-number generator.

The POM must compile this source with Java 21.
It must not require a third-party runtime dependency.
Maven validation must work offline using the fixed environment.
Do not add a main method as a substitute for the library API.

Use small checks such as the following to verify the public behavior:

1. Construct `{1, 2}`, confirm index `0`, read one unsigned byte, and confirm
   the value is `1` and the index is `1`.
2. Construct `{0x01, 0x02}`, read an unsigned short, and confirm the value is
   `0x0102` and the index is `2`.
3. Construct `{0x01, 0x02, 0x03, 0x04}`, read an integer, and confirm the
   value is `0x01020304` and the index is `4`.
4. Construct an empty sequence, attempt `readByte()`, and confirm a checked
   `IOException` is observed without a fabricated byte.

Do not copy verifier-owned test identifiers or private assertion text into the
project.
Do not make the candidate write grading, reward, JUnit, or verifier reports.
Do not add network fallback behavior when Maven or a read operation fails.
