# pyasn1-modules

## Project Description

Build an installable `pyasn1-modules` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pyasn1-modules`; public import package begins at `pyasn1_modules`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `pyasn1-modules`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `root exports`: preserve the documented object or module behavior, including state and side effects.
3. `core classes`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `core functions`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.11 on the pinned Linux image.
- Distribution identity: `pyasn1-modules`; public import package begins at `pyasn1_modules`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `pyasn1==0.6.1`, `setuptools==80.9.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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


Recreate the package layout and public module names from the frozen protocol
collection. Generated-looking ASN.1 declarations are expected; preserve
module-level identity and avoid network or runtime code generation. Keep
`LICENSE.txt`, package metadata, and a concise README in the project. The
project must install with `pip install .` using the preinstalled, hash-locked
dependency set, and all supplied tests must run without network access.

Do not copy evaluation tests or use a preinstalled `pyasn1-modules` distribution to
answer imports. The verifier installs the submitted project into an isolated
installed package path and executes the frozen protocol tests from a separate process.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
readPemBlocksFromFile(fileObj, *markers) -> tuple[int, bytes]
readPemFromFile(fileObj, startMarker="-----BEGIN CERTIFICATE-----",
                endMarker="-----END CERTIFICATE-----") -> bytes
readBase64fromText(text) -> bytes
readBase64FromFile(fileObj) -> bytes
```

### Example 2: ordinary usage
```text
from pyasn1.codec.der import decoder, encoder
from pyasn1_modules import rfc5280

certificate = rfc5280.Certificate()
encoded = encoder.encode(certificate)
decoded, remainder = decoder.decode(encoded, asn1Spec=certificate)
assert not remainder
```

### Example 3: boundary or error behavior
```text
readPemBlocksFromFile(fileObj, *markers) -> tuple[int, bytes]
readPemFromFile(fileObj, startMarker="-----BEGIN CERTIFICATE-----",
                endMarker="-----END CERTIFICATE-----") -> bytes
readBase64fromText(text) -> bytes
readBase64FromFile(fileObj) -> bytes
```

### Example 4: boundary or error behavior
```text
from pyasn1.codec.der import decoder, encoder
from pyasn1_modules import rfc5280

certificate = rfc5280.Certificate()
encoded = encoder.encode(certificate)
decoded, remainder = decoder.decode(encoded, asn1Spec=certificate)
assert not remainder
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
