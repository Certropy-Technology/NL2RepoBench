# Build `PyNaCl`

Create an installable Python distribution named `PyNaCl` whose import package
is `nacl`. Reproduce the pinned 1.6.2 high-level cryptographic API described
below on CPython 3.12. Evaluation is local and deterministic. Do not fetch
source code or dependencies during the evaluation run.

## Project Description

PyNaCl provides Python objects over NaCl/libsodium primitives. Its high-level
surface covers byte encodings, authenticated symmetric encryption, public-key
boxes, sealed boxes, Ed25519 signatures, fixed and incremental hashes, and
password-based key derivation. Keys and cryptographic messages are bytes-like;
encoder classes provide explicit textual representations.

The package is expected to build a native CFFI/libsodium binding or provide a
behaviorally equivalent local implementation of this documented surface. The
preinstalled build closure includes CFFI and a C toolchain. Runtime operations
must not use the network, external services, subprocesses, or persistent user
state.

## Supports

- Provide distribution version `1.6.2`, Python requirement `>=3.8`, the
  `nacl` package, and a `nacl/py.typed` marker. `nacl.__all__` contains
  `__email__`, `__uri__`, and `__version__`.
- Provide `nacl.encoding`, `nacl.exceptions`, `nacl.utils`, `nacl.secret`,
  `nacl.public`, `nacl.signing`, `nacl.hash`, `nacl.hashlib`, and
  `nacl.pwhash` with the contracts below.
- Preserve bytes input/output, encoder behavior, deterministic results when a
  key, seed, nonce, salt, and parameters are supplied, and cryptographically
  random output from `generate()`, `random()`, or omitted nonces.
- Reject malformed key, seed, nonce, signature, digest, and salt sizes before
  producing a result. Authentication or signature failure raises the
  corresponding `nacl.exceptions` type rather than returning unauthenticated
  plaintext.
- Keep secret material available through `bytes(obj)` and `obj.encode(...)`
  where specified. Key equality compares key identity/content and keys remain
  hashable.
- Keep the high-level package independent of network access. No CLI or console
  entry point is required. Low-level `nacl.bindings` functions beyond what is
  necessary to implement this high-level surface are not part of this task.

## API Usage Guide

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

## Implementation Notes

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
