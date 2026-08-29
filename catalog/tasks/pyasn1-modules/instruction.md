# Build `pyasn1-modules`

Create a complete, installable Python distribution named `pyasn1-modules` from
an empty workspace. The distribution must expose the `pyasn1_modules` package
and reproduce the frozen ASN.1 protocol modules and PEM helpers below without
downloading the reference implementation at runtime.

## Project Description

`pyasn1-modules` is a collection of ASN.1 data structures expressed as
`pyasn1` schema classes for protocols from SNMP, PKCS, CMS, X.509, OCSP,
S/MIME, RPKI, TLS, and related RFCs. Callers construct schema objects,
populate components, and use the `pyasn1` DER codecs for encoding and
decoding. The reference release reports version `0.4.2`.

## Supports

- Provide an installable project with a `pyproject.toml` using setuptools and
  the import package `pyasn1_modules`.
- Support Python 3.8 and newer CPython versions and declare exactly one runtime
  dependency, `pyasn1` in the compatible `0.6.x` range. Runtime operation is
  offline and must not use subprocesses, network connections, or files outside
  normal Python imports.
- Make all `pyasn1_modules.rfcNNNN` modules in the frozen public collection
  importable. Preserve their public ASN.1 classes, OID/value constants,
  component maps, and open-type maps so schemas can be composed across modules.
  The hidden collection exercises the full 282-leaf protocol suite.
- Include `pyasn1_modules.pem` and its four public helpers. The upstream
  `tools/` programs are not part of this task's runtime contract.
- Keep schema construction deterministic. DER encoding and decoding must be
  delegated to `pyasn1.codec.der.encoder` and `pyasn1.codec.der.decoder`; do
  not replace ASN.1 values with plain dictionaries or JSON representations.

## API Usage Guide

The package root exposes `__version__ == "0.4.2"`. Every RFC module exports
the schema classes and constants defined by that RFC module. Classes are
ordinary `pyasn1.type.univ`, `namedtype`, `constraint`, `tag`, and related
subclasses or compatible derived types. Their component names, tags,
constraints, defaults, optionality, OIDs, and cross-module open-type maps must
match the protocol definitions and support normal `pyasn1` operations such as
`clone()`, `setComponentByName`, `getComponentByName`, `isValue`, and
`prettyPrint()`.

The following helpers are public and must retain these signatures and return
shapes:

```python
readPemBlocksFromFile(fileObj, *markers) -> tuple[int, bytes]
readPemFromFile(fileObj, startMarker="-----BEGIN CERTIFICATE-----",
                endMarker="-----END CERTIFICATE-----") -> bytes
readBase64fromText(text) -> bytes
readBase64FromFile(fileObj) -> bytes
```

`readPemBlocksFromFile` scans a text file-like object for the first matching
`(start_marker, end_marker)` pair, returns its zero-based marker index and
base64-decoded bytes, and returns `(-1, b"")` when no block is found.
`readPemFromFile` is the certificate-marker compatibility wrapper. The two
base64 helpers decode supplied text or file contents using standard base64
semantics and return bytes; malformed input raises the underlying decoding
exception.

Typical protocol use is:

```python
from pyasn1.codec.der import decoder, encoder
from pyasn1_modules import rfc5280

certificate = rfc5280.Certificate()
encoded = encoder.encode(certificate)
decoded, remainder = decoder.decode(encoded, asn1Spec=certificate)
assert not remainder
```

Decoders must accept the exact DER fixtures used by the supported RFC modules,
including open types where the module defines them. Encoding a value decoded
from a fixture must preserve the expected DER bytes. Invalid tags, malformed
DER, missing required components, and constraint violations should continue to
raise the relevant `pyasn1` exception rather than being silently accepted.

## Implementation Notes

Recreate the package layout and public module names from the frozen protocol
collection. Generated-looking ASN.1 declarations are expected; preserve
module-level identity and avoid network or runtime code generation. Keep
`LICENSE.txt`, package metadata, and a concise README in the project. The
project must install with `pip install .` using the preinstalled, hash-locked
dependency set, and all supplied tests must run without network access.

Do not copy hidden tests or use a preinstalled `pyasn1-modules` distribution to
answer imports. The verifier installs the submitted project into an isolated
candidate site and executes the frozen protocol tests from a separate process.
