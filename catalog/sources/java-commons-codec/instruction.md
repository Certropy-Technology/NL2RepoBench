# Project Description

Implement the selected serializable binary encoding behavior of Apache Commons
Codec as a single Maven Java library. The project must provide standard padded
Base64 encoding/decoding and lowercase hexadecimal encoding through the public
classes in `org.apache.commons.codec.binary`.

## Introduction and Goals

The library converts byte arrays to stable text representations and converts
standard Base64 text back to bytes. The evaluator uses a separate offline
verifier, an empty private Maven repository, and a fixed JDK 21/Maven
environment. Do not copy or execute the upstream build, tests, plugins,
profiles, or repository configuration.

## Natural Language Instruction (Prompt)

Please create a Java Maven project that provides the following public behavior:

1. `Base64.encodeBase64String(byte[])` returns standard padded Base64 text.
2. `Base64.decodeBase64(String)` decodes standard Base64 text into the original
   bytes.
3. `Hex.encodeHexString(byte[])` returns lowercase hexadecimal text.
4. Preserve ordinary empty-input behavior, deterministic output, byte order,
   and UTF-8 usage in examples.
5. Keep Java sources under `src/main/java` in a normal single-module Maven
   project with no external runtime dependencies.

## Environment Configuration

- Java runtime: Temurin JDK `21.0.12+8`
- Maven: `3.9.11`
- Platform: Linux `amd64`
- Build and verification: offline, verifier-owned Maven/Javac harness
- Candidate compilation: `javac --release 21`
- Runtime dependencies: none
- Network access: unavailable to the agent and verifier

## Project Architecture

Use the standard Maven layout:

```text
project/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/apache/commons/codec/binary/
                ├── Base64.java
                └── Hex.java
```

The required public classes are `org.apache.commons.codec.binary.Base64` and
`org.apache.commons.codec.binary.Hex`. Keep the implementation self-contained.

## API Usage Guide

```java
import java.nio.charset.StandardCharsets;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.binary.Hex;

byte[] input = "hello".getBytes(StandardCharsets.UTF_8);
String encoded = Base64.encodeBase64String(input);
byte[] decoded = Base64.decodeBase64(encoded);
String hexadecimal = Hex.encodeHexString(decoded);
```

The required public signatures are:

```java
String Base64.encodeBase64String(byte[] data)
byte[] Base64.decodeBase64(String encoded)
String Hex.encodeHexString(byte[] data)
```

The methods are static, deterministic, and do not access the network or
filesystem. `encodeBase64String` uses standard padded Base64. `decodeBase64`
returns bytes in their original order. `encodeHexString` uses lowercase
hexadecimal digits.

## Examples and Boundary Conditions

```java
Base64.encodeBase64String("hello".getBytes(StandardCharsets.UTF_8)); // aGVsbG8=
Hex.encodeHexString(new byte[] {0, 15, -1});                         // 000fff
Base64.decodeBase64("");                                             // empty bytes
```

Preserve empty input, UTF-8 byte values, padding, lowercase hexadecimal
output, and deterministic behavior. Do not add external dependencies or rely
on Maven Central during verification.

## Implementation Notes

The verifier compiles candidate sources directly and calls only the selected
public methods through a separate candidate JVM. The candidate `pom.xml` is
checked as safe metadata; upstream plugins, profiles, repositories, tests,
modules, and release configuration are outside the task contract.
