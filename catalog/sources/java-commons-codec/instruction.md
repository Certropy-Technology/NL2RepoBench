## Project Description

Create a small, single-module Maven project that recreates the bounded public
contract of the Apache Commons Codec task. The implementation is a Java 21
library, not a command-line application. Keep candidate source files under
`workspace/src/main/java` and use the exact package names described below.

The required behavior is deterministic byte-oriented encoding and decoding.
The contract covers standard Base64 conversion, hexadecimal conversion, empty
values, binary zero bytes, negative Java byte values, UTF-8 data supplied as
bytes, and the documented malformed-hex exception. The verifier invokes the
public static methods from a separate Java harness, so class names, method
visibility, parameter types, return types, and package names are part of the
contract.

Do not implement a different library design, a command-line interface, a
network service, or unrelated codecs. Do not copy an upstream implementation.
Use the public behavior in this instruction as the implementation target.

The project must compile without downloading anything. The candidate `pom.xml`
is metadata for the Maven task; the tested library behavior must be provided by
your own classes and the Java standard library only.

### Natural Language Instruction (Prompt)

Implement the bounded Commons Codec behavior described by this document. Build
the Maven project in the `workspace/` directory, provide the named public
classes and static methods, and preserve the stated return shapes, ordering,
boundary behavior, and exception contract. The result must work offline on
Temurin JDK 21 without an external runtime dependency.

## Supports

The project supports Java source layout and Maven metadata as follows:

### Project Directory Structure

```text
workspace/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── org/
                └── apache/
                    └── commons/
                        └── codec/
                            ├── DecoderException.java
                            └── binary/
                                ├── Base64.java
                                └── Hex.java
```

The required public types are:

* `org.apache.commons.codec.binary.Base64`
* `org.apache.commons.codec.binary.Hex`
* `org.apache.commons.codec.DecoderException`

`Base64` and `Hex` expose the static methods documented in the API Usage
Guide. The task does not require constructors, stateful codec instances,
streaming codecs, digest codecs, language codecs, or CLI entry points.

Use JDK 21 language and library facilities. The fixed environment is Temurin
JDK `21.0.12+8`, Maven `3.9.11`, Linux `amd64`, and `glibc`. Runtime network
access is disabled. Declare no runtime dependency and do not rely on a Maven
repository, plugin, profile, module, custom extension, or runtime download.

Input bytes are arbitrary Java `byte` values. A byte with value `-1` is a
normal binary value and must be preserved by a round trip; it is not an error.
UTF-8 text is represented by the caller as `byte[]`, normally using
`StandardCharsets.UTF_8`. Do not apply a platform-default charset inside the
codec methods.

Output is deterministic. Base64 uses the standard alphabet and conventional
padding. Hexadecimal output uses two lowercase hexadecimal characters for
each input byte. Empty input returns an empty value of the method's declared
return type rather than a sentinel string.

There is no task CLI to implement. The documented command for local checking
is the offline Maven validation command:

```bash
mvn --offline validate
```

This command validates project metadata only; the public contract is checked
by a verifier-owned Java harness compiled with `javac --release 21`.

## API Usage Guide

The examples below use these imports:

```java
import java.nio.charset.StandardCharsets;
import org.apache.commons.codec.DecoderException;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.binary.Hex;
```

### `org.apache.commons.codec.binary.Base64.encodeBase64`

Import path:

```java
import org.apache.commons.codec.binary.Base64;
```

Signature:

```java
public static byte[] encodeBase64(byte[] binaryData)
```

The input domain is any byte array, including an empty array and bytes with
the high bit set. The returned `byte[]` contains ASCII bytes from the standard
Base64 alphabet (`A-Z`, `a-z`, `0-9`, `+`, and `/`) and `=` padding when the
input length is not divisible by three. Output order follows input order and
is deterministic; the method has no external side effect and does not mutate
the caller's array.

Normal example:

```java
byte[] encoded = Base64.encodeBase64(
    "hello".getBytes(StandardCharsets.UTF_8));
String text = new String(encoded, StandardCharsets.US_ASCII);
// text is "aGVsbG8="
```

Edge example:

```java
byte[] encoded = Base64.encodeBase64(new byte[] {0, 1, 2, -1});
byte[] empty = Base64.encodeBase64(new byte[0]);
// encoded is non-empty and empty.length == 0
```

For this bounded contract, null input is not a meaningful data value. Do not
invent a sentinel output for null. The trusted public contract does not bind
additional overloads or configurable line-wrapping options for this method.

### `org.apache.commons.codec.binary.Base64.encodeBase64String`

Import path:

```java
import org.apache.commons.codec.binary.Base64;
```

Signature:

```java
public static String encodeBase64String(byte[] binaryData)
```

The input domain is any byte array accepted by the byte-array encoder,
including empty input and arbitrary binary values. The return value is the
standard padded Base64 representation as an ASCII-compatible `String`; it is
not a hexadecimal string and must not contain line separators. The operation
is deterministic, has no external side effect, and preserves the order of all
input bytes.

Normal example:

```java
String encoded = Base64.encodeBase64String(
    "hello".getBytes(StandardCharsets.UTF_8));
// encoded is "aGVsbG8="
```

Edge example:

```java
String encoded = Base64.encodeBase64String(new byte[] {(byte) 0xff});
// encoded is the padded Base64 form for one byte, "/w=="
```

The task does not bind a CLI or an instance method for string encoding. Do
not add a platform-default charset conversion around the public method.

### `org.apache.commons.codec.binary.Base64.decodeBase64`

Import path:

```java
import org.apache.commons.codec.binary.Base64;
```

Signature:

```java
public static byte[] decodeBase64(byte[] base64Data)
```

The input domain is a byte array containing a valid standard Base64 value,
including conventional `=` padding and the empty value. The return type is a
new byte array containing the decoded bytes in their original order. A valid
encode/decode round trip preserves every byte, including zero and negative
Java byte values. The operation is deterministic and does not mutate the
input array or perform I/O.

Normal example:

```java
byte[] decoded = Base64.decodeBase64("aGVsbG8=".getBytes(
    StandardCharsets.US_ASCII));
String text = new String(decoded, StandardCharsets.UTF_8);
// text is "hello"
```

Edge example:

```java
byte[] original = new byte[] {0, 1, 2, (byte) 0xff};
byte[] decoded = Base64.decodeBase64(Base64.encodeBase64(original));
// decoded has the same four byte values and the same order as original
```

Malformed or incomplete data must not be silently transformed into a
different valid application value. Preserve the established Base64 decoder
contract for invalid input and do not replace it with a custom exception or a
text fallback. No checked exception is part of this bound signature. No other
Base64 overload is confidently bindable from the task inventory.

### `org.apache.commons.codec.binary.Hex.encodeHexString`

Import path:

```java
import org.apache.commons.codec.binary.Hex;
```

Signature:

```java
public static String encodeHexString(byte[] data)
```

The input domain is any byte array, including an empty array and bytes whose
signed Java values are negative. The method returns a `String` with exactly
two lowercase hexadecimal characters per input byte. Characters are emitted
in input order, so the result length is exactly `data.length * 2`. The method
has no external side effect and does not change the caller's array.

Normal example:

```java
String encoded = Hex.encodeHexString(new byte[] {0, 15, (byte) 0xff});
// encoded is "000fff"
```

Edge example:

```java
String encoded = Hex.encodeHexString(new byte[0]);
// encoded is the empty string, not null and not a space-filled value
```

The lowercase requirement is observable: use `a` through `f`, not uppercase
`A` through `F`. The task inventory confidently binds this string-returning
method; no additional `encodeHex` overload is confidently bindable for this
task's verifier contract.

### `org.apache.commons.codec.binary.Hex.decodeHex`

Import path:

```java
import org.apache.commons.codec.DecoderException;
import org.apache.commons.codec.binary.Hex;
```

Signature:

```java
public static byte[] decodeHex(String data) throws DecoderException
```

The input is a hexadecimal `String` with an even number of characters. Each
pair represents one byte, and both lowercase and uppercase hexadecimal input
digits are accepted as equivalent representations. The returned `byte[]`
contains bytes in pair order. Empty input returns an empty byte array.

Normal example:

```java
byte[] decoded = Hex.decodeHex("000Fff");
// decoded contains {0, 15, -1}
```

Edge example:

```java
byte[] empty = Hex.decodeHex("");
// empty.length == 0
```

An odd-length string is invalid and must throw the checked
`org.apache.commons.codec.DecoderException`. A string containing a character
outside hexadecimal digits is also invalid and must throw
`DecoderException`; do not truncate it, substitute zero, or return a partial
array. The method is deterministic, has no external side effect, and does not
perform I/O. Null is not a valid hexadecimal value; do not invent a null
sentinel contract.

### `org.apache.commons.codec.DecoderException`

Import path:

```java
import org.apache.commons.codec.DecoderException;
```

The task binds this checked exception as the error type reported by
`Hex.decodeHex(String)` for malformed hexadecimal input. It is part of the
public package contract and must be available for callers to catch. Do not
replace it with `IllegalArgumentException`, an unchecked custom exception, a
printed message, or a process exit.

No public CLI entry point, streaming entry point, digest codec, language
codec, or additional class method is confidently bindable from the selected
task inventory. Implementing those unrelated APIs is unnecessary.

### Error and state contract

All methods in this task are static utility operations. They do not maintain
mutable global state, access the filesystem, access the network, read locale
settings, or depend on wall-clock time. Repeated calls with equal byte or
string values produce equal results. The methods must not mutate caller-owned
arrays. Checked exception behavior is limited to `DecoderException` from
malformed hexadecimal decoding as documented above.

## Implementation Notes

Keep the implementation in one ordinary Maven project. The package tree must
match the imports exactly; a class in the default package or a similarly named
package is not interchangeable. `Base64` belongs under
`org.apache.commons.codec.binary`, `Hex` belongs under the same `binary`
package, and `DecoderException` belongs directly under
`org.apache.commons.codec`.

The candidate POM is metadata only. Use `mvn --offline validate` when checking
metadata, but do not make correctness depend on Maven plugins or a downloaded
Commons Codec artifact. The verifier compiles the candidate with Java 21 and
uses an isolated harness, so the public classes must be discoverable from
`src/main/java` without a generated source step.

Preserve byte values rather than converting through signed decimal text. For
example, a byte array containing `{0, (byte) 0xff}` must encode and decode
back to the same two values. Likewise, UTF-8 bytes for non-ASCII text must be
treated as bytes; the codec must not decode them using the host default
charset.

Small verifiable examples include:

1. Encoding UTF-8 bytes for `hello` through Base64 yields `aGVsbG8=`.
2. Decoding `aGVsbG8=` yields the five UTF-8 bytes for `hello`.
3. Hex encoding `{0, 15, (byte) 0xff}` yields lowercase `000fff`.
4. Hex decoding `000fff` yields `{0, 15, (byte) 0xff}` and decoding an odd
   or non-hex string raises `DecoderException`.

Empty values are meaningful test cases. Base64 encoding and decoding an empty
byte array must return an empty byte array, while hexadecimal encoding an empty
byte array must return an empty string. Do not return null, whitespace, or a
sentinel marker for empty input.

Use standard Base64 padding and preserve deterministic ordering. Do not add
line wrapping, random salts, timestamps, logging output, filesystem writes,
network requests, or process-global caches. Such behavior would change the
observable contract and is not needed for this task.

The task has four verifier contract leaves covering Base64 encode, Base64
decode, hexadecimal behavior, and empty input. Implement all documented
boundary behavior rather than optimizing only for the normal examples. Do not
copy private tests, verifier code, an Oracle implementation, or an upstream
algorithm body into the project.

The original upstream project contains many codecs and build modules that are
outside this bounded exercise. Do not add streaming codecs, digest or language
codecs, Maven publishing configuration, release profiles, or a command-line
entry point. APIs outside the methods documented above are not confidently
bindable and are intentionally out of scope.
