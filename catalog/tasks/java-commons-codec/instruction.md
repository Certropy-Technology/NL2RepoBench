# Project Description

Implement the selected serializable binary encoding behavior of Apache Commons
Codec as a single Maven Java library. The evaluator uses JDK 21, an offline
empty Maven repository, and a verifier-owned contract harness.

# Supports

Implement the public classes in `org.apache.commons.codec.binary` needed for
these operations:

- `Base64.encodeBase64String(byte[])` returns standard padded Base64 text.
- `Base64.decodeBase64(String)` decodes standard Base64 text to bytes.
- `Hex.encodeHexString(byte[])` returns lowercase hexadecimal text.

Inputs and outputs are UTF-8 strings in the evaluator contract. Preserve
deterministic ordering and the library's ordinary empty-input behavior.

# API Usage Guide

```java
import java.nio.charset.StandardCharsets;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.binary.Hex;

String encoded = Base64.encodeBase64String("hello".getBytes(StandardCharsets.UTF_8));
byte[] decoded = Base64.decodeBase64(encoded);
String hexadecimal = Hex.encodeHexString(decoded);
```

The static methods are deterministic and do not access the network or
filesystem. `decodeBase64` accepts standard padded Base64 input and returns the
decoded bytes. `encodeBase64String` and `encodeHexString` return lowercase-safe
text representations.

# Implementation Notes

Use the standard Maven layout with Java sources under `src/main/java`. The
verifier compiles candidate sources with `--release 21` and uses a fixed
separate JVM contract harness. Do not execute or copy the upstream Maven build,
profiles, plugins, tests, or repository configuration.
