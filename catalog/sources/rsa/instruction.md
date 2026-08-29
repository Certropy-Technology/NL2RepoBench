# Project Description

Create a complete installable Python project named `rsa` from an empty
workspace.  It is a pure-Python implementation of RSA key generation,
PKCS#1 v1.5 encryption/decryption, and signing/verification.  The package is
imported as `rsa`, targets Python 3.8 or newer, and reports version
`4.10-dev0`.

The implementation must be deterministic wherever the API accepts a random
source or fixed key material.  Operations that intentionally use secure
randomness, such as key generation and encryption padding, must use the
standard-library randomness source expected by the API.  Do not contact the
network or depend on external services.

# Supports

- Use a PEP 517 project with `pyproject.toml` and Poetry Core (or an equivalent
  backend) so `pip install .` works from the project root.
- Runtime dependency: `pyasn1>=0.1.3`; it is required for DER key
  serialization.  Development tooling may include pytest, pytest-cov, mypy,
  and compatible build tools, but the library itself must remain pure Python.
- Provide the `rsa/` package, `rsa/py.typed`, and the six console commands
  `pyrsa-priv2pub`, `pyrsa-keygen`, `pyrsa-encrypt`, `pyrsa-decrypt`,
  `pyrsa-sign`, and `pyrsa-verify`.
- The public modules are `rsa`, `rsa.asn1`, `rsa.cli`, `rsa.common`,
  `rsa.core`, `rsa.key`, `rsa.parallel`, `rsa.pem`, `rsa.pkcs1`,
  `rsa.pkcs1_v2`, `rsa.prime`, `rsa.randnum`, `rsa.transform`, and
  `rsa.util`.

# API Usage Guide

## Root exports

`rsa.__version__` is the string `"4.10-dev0"`.  The root module exports
`newkeys`, `encrypt`, `decrypt`, `sign`, `verify`, `PublicKey`, `PrivateKey`,
`DecryptionError`, `VerificationError`, `find_signature_hash`, `compute_hash`,
and `sign_hash` through `rsa.__all__`.

## Integer and byte primitives

In `rsa.transform`:

- `bytes2int(raw_bytes: bytes) -> int` interprets a big-endian byte string as
  a non-negative integer.  Empty bytes map to zero.
- `int2bytes(number: int, fill_size: int = 0) -> bytes` returns the minimal
  big-endian representation, or pads to at least `fill_size` bytes.  Negative
  or non-integer inputs raise the natural `ValueError` or `TypeError`; a
  requested size too small raises `OverflowError`.

In `rsa.common`:

- `byte_size(number: int) -> int` returns the byte length needed for a
  non-negative integer; zero has size one, matching the unsigned byte
  representation used by the package.
- `bit_size(number: int) -> int` returns the bit length; zero has size zero.
- `inverse(x: int, n: int) -> int` returns the modular inverse when it exists
  and raises `NotRelativePrimeError` for a non-coprime pair.

In `rsa.core`:

- `encrypt_int(message: int, e: int, n: int) -> int` computes modular RSA
  exponentiation and rejects a message outside `[0, n)`.
- `decrypt_int(encrypted: int, d: int, n: int) -> int` performs the matching
  modular operation.  The core operation uses Python modular exponentiation;
  the PKCS#1 layer is responsible for validating encoded ciphertext.
- The same integer operation is used with the public or private exponent;
  higher-level signing and verification are provided by `rsa.pkcs1`.

## Keys

In `rsa.key`:

- `PublicKey(n: int, e: int)` stores the public modulus and exponent.  Its
  `n` and `e` fields are readable, instances compare and hash by value, and
  `__repr__` identifies the key.  `PublicKey.load_pkcs1(keyfile: bytes,
  format: str = "PEM") -> PublicKey` loads PEM or DER.  `save_pkcs1(format:
  str = "PEM") -> bytes` performs the inverse operation.
- `PrivateKey(n: int, e: int, d: int, p: int, q: int, other_primes=None)`
  stores private key parameters.  It exposes `n`, `e`, `d`, `p`, `q`, `exp1`,
  `exp2`, `coef`, and for multiprime keys `exponents`, `coefficients`, `ds`,
  `ts`, and `other_primes` as applicable.  Its PEM/DER load and save methods
  mirror `PublicKey` and preserve valid multiprime material.
- `newkeys(nbits: int, poolsize: int = 1, exponent: int = 65537) ->
  tuple[PublicKey, PrivateKey]` generates a key pair of approximately the
  requested size.  `gen_keys(nbits, accurate=True, getprime_func=None,
  exponent=65537, nprimes=2)` is the lower-level generator and returns
  `(p, q, e, d)` for two primes or `(p, q, e, d, other_primes)` when
  `nprimes > 2`.  A supplied prime function is called with the requested bit
  size and makes tests deterministic.
- `PrivateKey.blind(encrypted: int) -> tuple[int, int]` returns a blinded
  ciphertext and the unblinding factor. `unblind(decrypted: int,
  blindfactor: int) -> int` reverses it.  Repeated blinding should use fresh
  factors and preserve the decrypted message.

## PKCS#1 operations

In `rsa.pkcs1`:

- `encrypt(message: bytes, pub_key: PublicKey) -> bytes` applies randomized
  PKCS#1 v1.5 encryption padding and returns one modulus-sized ciphertext.
  The message must fit; otherwise raise `OverflowError`.
- `decrypt(crypto: bytes, priv_key: PrivateKey) -> bytes` validates and removes
  encryption padding.  Invalid padding raises `DecryptionError`.
- `sign(message: bytes, priv_key: PrivateKey, hash_method: str) -> bytes`
  produces a PKCS#1 v1.5 signature. `verify(message: bytes, signature: bytes,
  pub_key: PublicKey) -> str` returns the hash algorithm name for a valid
  signature and raises `VerificationError` for a mismatch.
- `compute_hash(message: bytes, hash_method: str) -> bytes`,
  `sign_hash(hash_value: bytes, priv_key: PrivateKey, hash_method: str) ->
  bytes`, and `find_signature_hash(signature: bytes, pub_key: PublicKey) ->
  str` expose the digest and signature helpers.  Hash names are the hashlib
  names accepted by the project, including SHA-2 and SHA-3 names.
- `yield_fixedblocks(infile: BinaryIO, blocksize: int) -> Iterator[bytes]`
  yields consecutive blocks and includes a final short block when present.
  It rejects non-positive block sizes.
- `CryptoError`, `DecryptionError`, and `VerificationError` are the public
  exception hierarchy for cryptographic failures.

In `rsa.pkcs1_v2`, `mgf1(seed: bytes, length: int, hasher: str = "SHA-1") ->
bytes` implements the PKCS#1 mask generation function.  It rejects unknown
hashers and lengths that cannot be represented by the four-byte counter.

## Prime and random helpers

- `rsa.prime.is_prime(number: int) -> bool` performs a probable-prime test
  and handles small, even, negative, and known Mersenne values correctly.
  `get_primality_testing_rounds(input_size: int) -> int`
  returns the configured round count.
- `rsa.randnum.read_random_bits(nbits: int) -> bytes`,
  `read_random_int(nbits: int) -> int`, and `read_random_odd_int(nbits: int)
  -> int` return values with the requested bit constraints.  They reject
  negative sizes.
- `rsa.parallel.getprime(nbits: int) -> int` provides the multiprocessing
  prime-generation helper and returns a probable prime of the requested size.

## PEM and command line tools

`rsa.pem` provides `_markers`, `load_pem(contents: bytes, pem_marker: bytes)
-> bytes`, and `save_pem(contents: bytes, pem_marker: bytes) -> bytes` for
the project's PEM framing.  Marker names are preserved, base64 is wrapped at
the library's fixed line width, and malformed markers raise `ValueError`.

The console commands use files and standard streams:

- `pyrsa-keygen [--out FILE] [--pubout FILE] [--form PEM|DER] BITS` creates a
  private key and optionally its public key.
- `pyrsa-encrypt [-i FILE] [--out FILE] PUBLIC_KEY` encrypts bytes.
- `pyrsa-decrypt [-i FILE] PRIVATE_KEY` writes clear bytes to stdout.
- `pyrsa-sign [-i FILE] [--out FILE] PRIVATE_KEY HASH` writes a signature.
- `pyrsa-verify [-i FILE] PUBLIC_KEY SIGNATURE` exits successfully only for a
  valid signature.
- `pyrsa-priv2pub -i PRIVATE_KEY -o PUBLIC_KEY` converts a private key file.

The callable entry points are also available as `rsa.cli.keygen`,
`rsa.cli.encrypt`, `rsa.cli.decrypt`, `rsa.cli.sign`, `rsa.cli.verify`, and
`rsa.util.private_to_public`.  The four cryptographic CLI names are callable
operation objects rather than plain functions; they parse `sys.argv`, use
binary file data, and report usage errors with the established exit behavior.

# Implementation Notes

- Keep the package layout import-compatible with the modules named above and
  include type annotations and `py.typed`.
- Keep key serialization standards-compatible for PKCS#1 RSA public/private
  keys, including the multiprime representation used by the API.  PEM is a
  base64 wrapper around DER and must tolerate surrounding text while locating
  the requested marker.
- Keep random padding and prime generation separate from deterministic modular
  arithmetic.  Never replace cryptographic randomness with a fixed constant.
- The command-line tools must work after installation, but the evaluation
  uses a separate process boundary for candidate imports and calls.  Do not
  depend on hidden tests, a pre-existing checkout, or network access.
- Do not copy an upstream implementation or test suite into the workspace;
  implement the documented behavior as a fresh project.
