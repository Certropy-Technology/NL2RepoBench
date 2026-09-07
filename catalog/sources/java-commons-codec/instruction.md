# Introduction and Goals of the Commons Codec Project

Apache Commons Codec is a Java library for encoding and decoding common text
and binary representations. This task focuses on a deterministic public slice
of the library: Base64 and hexadecimal conversion, UTF-8 text handling, and
the documented exception behavior. The result must be a normal single-module
Maven project with the requested public classes and methods.

## Natural Language Instruction (Prompt)

Please create a Java Maven project named Commons Codec that implements the
following public behavior:

1. Provide Base64 encoding and decoding for byte arrays and UTF-8 strings.
2. Provide hexadecimal encoding and decoding with deterministic lowercase
   output and clear malformed-input errors.
3. Preserve empty input, binary zero bytes, padding, and non-ASCII UTF-8 data.
4. Expose the public static APIs described below in the Apache Commons Codec
   packages.
5. Keep all implementation under `src/main/java` in a single-module Maven
   project and do not add external runtime dependencies.

## Environment Configuration

### Core Dependency Library Versions

```Plain
Temurin JDK 21.0.12+8       # Java runtime
Maven 3.9.11                # Offline project tooling
Linux amd64                 # Fixed platform
Runtime dependencies: none  # Java standard library only
Network access: unavailable # Agent and verifier are offline
```

## Commons Codec Project Architecture

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
                        └── codec
                            ├── binary
                            │   ├── Base64.java
                            │   └── Hex.java
                            └── DecoderException.java
```

The candidate POM is metadata only. Do not use Maven plugins, repositories,
dependencies, profiles, modules, or custom build extensions to control the
verifier.

## API Usage Guide

### Core APIs

#### 1. Module Import

```java
import java.nio.charset.StandardCharsets;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.binary.Hex;
```

#### 2. Base64 Encoding

```java
byte[] encoded = Base64.encodeBase64("hello".getBytes(StandardCharsets.UTF_8));
```

Signature:

```java
static byte[] encodeBase64(byte[] binaryData)
```

The output uses the standard Base64 alphabet and padding.

#### 3. Base64 Decoding

```java
byte[] decoded = Base64.decodeBase64(encoded);
```

Signature:

```java
static byte[] decodeBase64(byte[] base64Data)
```

Decoding returns the original bytes for valid input and follows the public
library contract for malformed input.

#### 4. Hexadecimal Encoding and Decoding

```java
String text = Hex.encodeHexString(new byte[] {0, 15, -1});
byte[] bytes = Hex.decodeHex("000fff");
```

Signatures:

```java
static char[] encodeHex(byte[] data)
static String encodeHexString(byte[] data)
static byte[] decodeHex(String data)
```

Hex output is deterministic lowercase. Odd-length or invalid hex input must
follow the documented decoder exception behavior.

### Actual Usage Modes

#### Basic Encoding

```java
String encoded = Base64.encodeBase64String(
    "hello".getBytes(StandardCharsets.UTF_8));
```

#### Binary Round Trip

```java
byte[] original = new byte[] {0, 1, 2, -1};
byte[] roundTrip = Base64.decodeBase64(Base64.encodeBase64(original));
```

#### Hex Round Trip

```java
String hex = Hex.encodeHexString(original);
byte[] roundTrip = Hex.decodeHex(hex);
```

### Supported Function Types

The supported function types are Base64 byte-array conversion, Base64 string
conversion where explicitly shown, hexadecimal conversion, and deterministic
exception handling. Do not implement unrelated codecs or invent alternate
public contracts.

### Error Handling

Null, empty, malformed, odd-length, and binary boundary inputs must not produce
silently corrupted output. Use the public exception types and return shapes
expected by the API.

## Detailed Implementation Nodes of Functions

### Node 1: Base64 Encoding

Encode arbitrary bytes using the standard alphabet and required padding.

### Node 2: Base64 Decoding

Decode valid padded and unpadded forms according to the public contract and
preserve every byte, including zero and negative byte values.

### Node 3: UTF-8 Text Handling

Treat caller-provided UTF-8 bytes as binary data and preserve non-ASCII text
through an encode/decode round trip.

### Node 4: Hexadecimal Encoding

Convert each byte to exactly two lowercase hexadecimal characters.

### Node 5: Hexadecimal Decoding

Parse valid pairs, reject invalid characters and odd-length values, and expose
the expected decoder exception.

### Node 6: Empty and Boundary Inputs

Handle empty arrays and empty strings deterministically without changing the
public return type or introducing sentinel text.

### Node 7: Maven Project Layout

Use the exact public packages and standard Java source layout. Compile with
Java 21 and no external runtime dependency.

### Node 8: Offline Build Behavior

Do not access the network or rely on candidate-controlled Maven configuration;
the implementation must work in the fixed offline verifier.
