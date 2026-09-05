# pynacl

## Project Description

Build an installable `pynacl` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pynacl`; public import package begins at `nacl`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Encoders and encodable objects`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Utility byte objects and randomness`: preserve the documented object or module behavior, including state and side effects.
3. `Symmetric authenticated encryption`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Public-key boxes`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `pynacl`; public import package begins at `nacl`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `cffi==2.1.1`, `packaging==26.3`, `pycparser==3.0`, `setuptools==84.0.0`, `wheel==0.48.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── package/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### Encoders and encodable objects

Import from `nacl.encoding`:

- `RawEncoder.encode(data: bytes) -> bytes` and
  `RawEncoder.decode(data: bytes) -> bytes` return the input bytes unchanged.
- `HexEncoder`, `Base16Encoder`, `Base32Encoder`, `Base64Encoder`, and
  `URLSafeBase64Encoder` each expose the same static `encode(data: bytes) ->
  bytes` and `decode(data: bytes) -> bytes` interface. Hex output is lowercase;
  Base16 output is uppercase. Invalid encoded input raises the standard
  decoding exception produced by the underlying codec.
- `Encodable.encode(self, encoder: Encoder = RawEncoder) -> bytes` applies the
  selected encoder to `bytes(self)`.

Encoder arguments are encoder classes, not instances.

### Utility byte objects and randomness

Import from `nacl.utils`:

- `random(size: int = 32) -> bytes` returns `size` cryptographically random
  bytes.
- `randombytes_deterministic(size: int, seed: bytes, encoder: Encoder =
  RawEncoder) -> bytes` deterministically expands an exactly 32-byte seed and
  encodes the result. An invalid seed length raises `nacl.exceptions.ValueError`.
- `EncryptedMessage` is a `bytes` subclass. Its full byte value is
  `nonce + ciphertext`; read-only `nonce: bytes` and `ciphertext: bytes`
  properties expose those parts in the same encoding selected by `encrypt()`.
- `bytes_as_string(bytes_in: bytes) -> str` decodes bytes as ASCII. Objects
  using `StringFixer` render `str(obj)` as the string form of `bytes(obj)`.

### Symmetric authenticated encryption

Import `SecretBox` and `Aead` from `nacl.secret`.

`SecretBox` uses a 32-byte key, a 24-byte nonce, and a 16-byte authenticator.
It exposes `KEY_SIZE`, `NONCE_SIZE`, `MACBYTES`, and `MESSAGEBYTES_MAX`.

```python
SecretBox(key: bytes, encoder: Encoder = RawEncoder)
SecretBox.encrypt(
    plaintext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
SecretBox.decrypt(
    ciphertext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
```

The constructor decodes and validates the key. `bytes(box)` returns the raw
key. `encrypt()` generates a random nonce when omitted. When `decrypt()` gets
no nonce, it splits the nonce from the beginning of the combined ciphertext;
with an explicit nonce, `ciphertext` is only the authenticated ciphertext part.
Wrong keys, modified ciphertexts, or invalid authenticators raise
`nacl.exceptions.CryptoError`. Invalid key or nonce lengths raise
`nacl.exceptions.ValueError`; a decoded non-bytes key raises
`nacl.exceptions.TypeError`.

`Aead` has the same key, nonce, authenticator, bytes conversion, and combined
message conventions, and exposes the same four size constants. It adds
authenticated additional data:

```python
Aead(key: bytes, encoder: Encoder = RawEncoder)
Aead.encrypt(
    plaintext: bytes,
    aad: bytes = b"",
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
Aead.decrypt(
    ciphertext: bytes,
    aad: bytes = b"",
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
```

The same `aad` bytes must be supplied for decryption. Incorrect AAD is an
authentication failure.

### Public-key boxes

Import from `nacl.public`:

```python
PublicKey(public_key: bytes, encoder: Encoder = RawEncoder)
PrivateKey(private_key: bytes, encoder: Encoder = RawEncoder)
PrivateKey.from_seed(seed: bytes, encoder: Encoder = RawEncoder) -> PrivateKey
PrivateKey.generate() -> PrivateKey
```

`PublicKey.SIZE`, `PrivateKey.SIZE`, and `PrivateKey.SEED_SIZE` are 32.
`PrivateKey.public_key` is the corresponding `PublicKey`. `bytes(key)` returns
raw key bytes; `encode()` applies an encoder. Public and private keys compare
equal only to the same key class and matching key identity, are hashable, and
compare unequal to raw bytes. `from_seed()` is deterministic. `generate()` is
random. Invalid public key lengths raise `nacl.exceptions.ValueError`; invalid
private key or seed type/length raises `nacl.exceptions.TypeError`.

```python
Box(private_key: PrivateKey, public_key: PublicKey)
Box.decode(encoded: bytes, encoder: Encoder = RawEncoder) -> Box
Box.encrypt(
    plaintext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
Box.decrypt(
    ciphertext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
Box.shared_key() -> bytes
```

`Box.NONCE_SIZE` is 24. A box created from Alice's private key and Bob's public
key has the same 32-byte shared key as the reverse pairing. `bytes(box)` and
`shared_key()` return that key; `Box.decode()` restores a box from an encoded
shared key. Encryption follows the same combined/detached nonce convention as
`SecretBox`. Constructor type errors raise `nacl.exceptions.TypeError`, nonce
length errors raise `nacl.exceptions.ValueError`, and authentication failures
raise `nacl.exceptions.CryptoError`.

```python
SealedBox(recipient_key: PublicKey | PrivateKey)
SealedBox.encrypt(plaintext: bytes, encoder: Encoder = RawEncoder) -> bytes
SealedBox.decrypt(ciphertext: bytes, encoder: Encoder = RawEncoder) -> bytes
```

A sealed box created from a public key can encrypt but cannot decrypt. Each
encryption uses a fresh ephemeral key, so repeated encryption of the same
plaintext differs. A box created from the matching private key decrypts the
message. `bytes(sealed_box)` is the recipient public key. Attempting decryption
with a public-only box raises built-in `TypeError`; modified ciphertext raises
`nacl.exceptions.CryptoError`.

### Signing and verification

Import from `nacl.signing`:

```python
SigningKey(seed: bytes, encoder: Encoder = RawEncoder)
SigningKey.generate() -> SigningKey
SigningKey.sign(message: bytes, encoder: Encoder = RawEncoder) -> SignedMessage
SigningKey.to_curve25519_private_key() -> nacl.public.PrivateKey

VerifyKey(key: bytes, encoder: Encoder = RawEncoder)
VerifyKey.verify(
    smessage: bytes,
    signature: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
VerifyKey.to_curve25519_public_key() -> nacl.public.PublicKey
```

A signing seed and verify key are each 32 bytes. `SigningKey.verify_key` is the
matching `VerifyKey`. Key generation is random; construction from a seed and
signing are deterministic. `bytes(SigningKey)` returns its seed and
`bytes(VerifyKey)` returns its public key. Both key classes support encoding,
content equality, and hashing.

`SignedMessage` is a `bytes` subclass containing `signature + message`; its
`signature` property is 64 bytes before optional encoding and its `message`
property is the original message in the selected encoding. `verify()` accepts
either a combined signed message or an unsigned message plus a detached raw
64-byte signature, returning the original message. For detached verification,
signature type and length are checked before the encoder is applied; textual
encoding is therefore supported for the combined form, while a detached
signature must already be raw 64-byte data. Tampering raises
`nacl.exceptions.BadSignatureError`; invalid key, seed, or signature sizes
raise `nacl.exceptions.ValueError` (with the documented constructor type checks).

Curve25519 conversion of a matching signing/verify pair yields a private/public
pair whose public keys match.

### Fixed hashes

Import from `nacl.hash`:

```python
sha256(message: bytes, encoder: Encoder = HexEncoder) -> bytes
sha512(message: bytes, encoder: Encoder = HexEncoder) -> bytes
blake2b(
    data: bytes,
    digest_size: int = BLAKE2B_BYTES,
    key: bytes = b"",
    salt: bytes = b"",
    person: bytes = b"",
    encoder: Encoder = HexEncoder,
) -> bytes
siphash24(
    message: bytes,
    key: bytes = b"",
    encoder: Encoder = HexEncoder,
) -> bytes
siphashx24(
    message: bytes,
    key: bytes = b"",
    encoder: Encoder = HexEncoder,
) -> bytes
```

Default output is lowercase hexadecimal bytes; `RawEncoder` returns digest
bytes. Preserve the published BLAKE2b and SipHash size constants and
`SIPHASHX_AVAILABLE`. BLAKE2b accepts supported digest sizes and bounded key,
salt, and personalization values. SipHash keys must have the corresponding
exact key size. Invalid sizes raise `nacl.exceptions.ValueError`.

### Incremental BLAKE2b

`nacl.hashlib.blake2b` is a hashlib-compatible object:

```python
blake2b(
    data: bytes = b"",
    digest_size: int = BYTES,
    key: bytes = b"",
    salt: bytes = b"",
    person: bytes = b"",
)
blake2b.update(data: bytes) -> None
blake2b.digest() -> bytes
blake2b.hexdigest() -> str
blake2b.copy() -> blake2b
```

Expose `digest_size`, `block_size == 128`, and `name == "blake2b"` properties,
plus the module and class maximum-size constants. `digest()` and `hexdigest()`
do not consume the state. `copy()` creates an independent state. Pickling or
calling `__reduce__()` raises built-in `TypeError`, as does the standard
hashlib behavior for this object.

### Password hashing and KDF

The primary password API is `nacl.pwhash.argon2id`; `nacl.pwhash` re-exports
the default Argon2id parameters and generic verification.

```python
argon2id.kdf(
    size: int,
    password: bytes,
    salt: bytes,
    opslimit: int = OPSLIMIT_SENSITIVE,
    memlimit: int = MEMLIMIT_SENSITIVE,
    encoder: Encoder = RawEncoder,
) -> bytes
argon2id.str(
    password: bytes,
    opslimit: int = OPSLIMIT_INTERACTIVE,
    memlimit: int = MEMLIMIT_INTERACTIVE,
) -> bytes
argon2id.verify(password_hash: bytes, password: bytes) -> bool
pwhash.verify(password_hash: bytes, password: bytes) -> bool
```

The salt is exactly `argon2id.SALTBYTES` (16 bytes). `kdf()` is deterministic
for fixed inputs and parameters and applies the requested encoder. Output size,
password, salt, operation, and memory limits are validated against the exposed
`BYTES_*`, `PASSWD_*`, `OPSLIMIT_*`, and `MEMLIMIT_*` constants. `str()` creates
a random modular-crypt byte string beginning with `STRPREFIX`; it is not
deterministic. Verification returns `True` on success, raises
`nacl.exceptions.InvalidkeyError` for a wrong password, and generic
`pwhash.verify()` raises `nacl.exceptions.CryptPrefixError` for an unsupported
hash prefix.

### Exceptions

`nacl.exceptions` provides `CryptoError`, `BadSignatureError`, `RuntimeError`,
`AssertionError`, `TypeError`, `ValueError`, `InvalidkeyError`,
`CryptPrefixError`, and `UnavailableError`. The names corresponding to built-in
exceptions subclass those built-ins; `BadSignatureError` subclasses
`CryptoError`.

`ensure(cond: bool, *args: object, **kwds: type[Exception]) -> None` returns
`None` when `cond` is true and otherwise raises `nacl.exceptions.AssertionError`
using the supplied arguments.


Use byte-preserving APIs throughout. Do not silently coerce `str` into key or
message bytes. Apply an encoder at the documented API boundary, then validate
decoded lengths. Keep combined encrypted and signed messages as real `bytes`
subclasses with stable part properties. Authentication and verification must
complete before plaintext is returned.

Use the provided C build toolchain and preinstalled CFFI closure if implementing
the native binding. The frozen upstream package builds its bundled libsodium,
so no runtime system libsodium service or download is required. Do not weaken
nonce/key/signature checks, replace authenticated encryption with reversible
encoding, or use deterministic output for APIs that promise fresh randomness.

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
SecretBox(key: bytes, encoder: Encoder = RawEncoder)
SecretBox.encrypt(
    plaintext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
SecretBox.decrypt(
    ciphertext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
```

### Example 2: ordinary usage
```text
Aead(key: bytes, encoder: Encoder = RawEncoder)
Aead.encrypt(
    plaintext: bytes,
    aad: bytes = b"",
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
Aead.decrypt(
    ciphertext: bytes,
    aad: bytes = b"",
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
```

### Example 3: boundary or error behavior
```text
PublicKey(public_key: bytes, encoder: Encoder = RawEncoder)
PrivateKey(private_key: bytes, encoder: Encoder = RawEncoder)
PrivateKey.from_seed(seed: bytes, encoder: Encoder = RawEncoder) -> PrivateKey
PrivateKey.generate() -> PrivateKey
```

### Example 4: boundary or error behavior
```text
Box(private_key: PrivateKey, public_key: PublicKey)
Box.decode(encoded: bytes, encoder: Encoder = RawEncoder) -> Box
Box.encrypt(
    plaintext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> EncryptedMessage
Box.decrypt(
    ciphertext: bytes,
    nonce: bytes | None = None,
    encoder: Encoder = RawEncoder,
) -> bytes
Box.shared_key() -> bytes
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
