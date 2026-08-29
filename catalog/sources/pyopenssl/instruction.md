# Build `pyOpenSSL`

Create a complete, installable Python distribution named `pyOpenSSL` from an
empty workspace. Its import package is `OpenSSL`. The implementation is a
compatible wrapper over the installed `cryptography` package and platform
OpenSSL library. Do not copy upstream source or tests. Evaluation is local and
deterministic; do not download code, certificates, or dependencies at runtime.

## Project Description

`pyOpenSSL` exposes the traditional `OpenSSL` Python API for inspecting and
serializing keys and X.509 certificates, creating TLS contexts, and using
memory-backed TLS connections. Use public `cryptography` APIs for conversion
where appropriate, while preserving the observable classes, constants, return
shapes, and exception families below.

The distribution and runtime version is `26.4.0`. The package must import as
`OpenSSL`, and `OpenSSL.__version__` must be the same string.

## Supports

- Support CPython `>=3.9`; provide a normal `pyproject.toml` or `setup.py`
  that works with `pip install .` and editable installation.
- Declare `cryptography>=49.0.0,<51` and, where needed,
  `typing-extensions>=4.9` as dependencies. Do not vendor wheels or copy an
  installed `OpenSSL` package into the project.
- Provide `OpenSSL`, `OpenSSL.crypto`, `OpenSSL.SSL`, `OpenSSL.rand`,
  `OpenSSL.debug`, and `OpenSSL.version`.
- Runtime operations are local. Do not use network sockets, subprocesses,
  environment-dependent certificate stores, temporary files, or current-time
  assertions in the implementation.
- Preserve the metadata exports `__author__`, `__copyright__`, `__email__`,
  `__license__`, `__summary__`, `__title__`, `__uri__`, and `__version__` from
  `OpenSSL.version` and the package root. `OpenSSL.__all__` includes the two
  submodules and those metadata names.

## API Usage Guide

### `OpenSSL.crypto`

Export `FILETYPE_PEM = 1`, `FILETYPE_ASN1 = 2`, `FILETYPE_TEXT = 65535`,
`TYPE_RSA`, `TYPE_DSA`, `Error`, `PKey`, `X509Name`, `X509`, `X509Store`,
`X509StoreContext`, `X509StoreContextError`, `X509StoreFlags`, and the
functions `load_certificate`, `dump_certificate`, `load_privatekey`,
`dump_privatekey`, `load_publickey`, `dump_publickey`,
`get_elliptic_curve`, and `get_elliptic_curves`.

`PKey()` starts uninitialized. `generate_key(type, bits)` accepts
`TYPE_RSA` or `TYPE_DSA`, returns `None`, and creates a key of the requested
size. `type()` and `bits()` report the OpenSSL key type and size; an empty key
reports zero for both. `check()` returns `True` for a consistent RSA private
key and raises `TypeError` for a public-only or unsupported key. Invalid key
types raise `OpenSSL.crypto.Error`. `PKey.from_cryptography_key(key)` accepts
cryptography private or public asymmetric key objects and
`to_cryptography_key()` returns the corresponding cryptography key.

`X509()` creates an empty certificate. `set_version(int)`, `get_version()`,
`set_serial_number(int)`, `get_serial_number()`, `set_pubkey(PKey)`,
`get_pubkey()`, `set_subject(X509Name)`, `get_subject()`, `set_issuer(X509Name)`,
and `get_issuer()` preserve normal return values and reject incompatible
arguments. `sign(PKey, digest_name)` signs and returns `None`.
`gmtime_adj_notBefore` and `gmtime_adj_notAfter` accept integer seconds.
`dump_certificate(FILETYPE_PEM, cert)` and
`dump_certificate(FILETYPE_ASN1, cert)` encode a signed certificate;
`load_certificate` reconstructs it.

`X509Name` comes from `get_subject()` or `get_issuer()`. Assigning supported
attributes such as `CN`, `O`, and `C` replaces that component. Long aliases
`commonName`, `organizationName`, and `countryName` are readable. Missing
components return `None`; unknown attributes raise `AttributeError`.
`get_components()` returns an ordered list of `(name: bytes, value: bytes)`;
`der()` returns non-empty DER bytes; equality compares names; `hash()` returns
an integer; and `repr()` identifies the name.

`dump_privatekey`/`load_privatekey` and `dump_publickey`/`load_publickey` use
PEM or ASN.1 according to the file type and preserve key size and public vs
private form. Invalid encoded data raises `OpenSSL.crypto.Error`. The
certificate and key bridge functions accept `cryptography` objects and
preserve their DER representation.

`X509Store.add_cert(cert)` adds a certificate. Constructing
`X509StoreContext(store, cert)` and calling `verify_certificate()` validates a
certificate trusted by the store; `get_verified_chain()` returns the verified
chain as `X509` objects. `get_elliptic_curve("prime256v1")` returns an object
with that `name`, repr `<Curve 'prime256v1'>`, and membership in
`get_elliptic_curves()`.

### `OpenSSL.SSL`

Export `TLS_METHOD`, `TLS_CLIENT_METHOD`, `TLS_SERVER_METHOD`,
`SSLv23_METHOD`, `VERIFY_NONE`, `VERIFY_PEER`, `MODE_RELEASE_BUFFERS`,
`OP_NO_SSLv2`, `SENT_SHUTDOWN`, `OPENSSL_VERSION`,
`OPENSSL_VERSION_NUMBER`, `SSLEAY_VERSION`, `Error`, `WantReadError`,
`WantWriteError`, `ZeroReturnError`, `SysCallError`, `Session`, `Context`,
`Connection`, and `OpenSSL_version`.

`Context(method)` accepts documented TLS method constants and rejects a
non-integer with `TypeError` and an unknown integer with `ValueError`.
`set_verify(mode, callback)` stores the verification mode (callbacks are
outside this task), `get_verify_mode()` reads it, and
`set_verify_depth(int)`/`get_verify_depth()` round-trip the depth.
`set_app_data(value)` and `get_app_data()` round-trip local values.
`set_cipher_list(bytes_or_str)` accepts a cipher expression and rejects other
types. `set_options(int)` and `set_mode(int)` return the resulting non-zero
bit mask. `set_min_proto_version` and `set_max_proto_version` accept integer
protocol values before a connection is created.

`Connection(context, None)` creates a memory-backed connection and marks the
context in use. `get_context()` returns its context;
`set_tlsext_host_name` accepts non-NUL bytes and `get_servername()` returns
them. `pending()` initially returns zero. `get_cipher_list()` reflects a
configured cipher. `set_connect_state()` followed by `do_handshake()` without
a peer raises `WantReadError`, after which `want_read()` is true.
`set_options`, `set_app_data`, `get_app_data`, `set_shutdown`, and
`get_shutdown` operate locally. The contract does not require a live socket,
peer, host certificate store, DTLS, or callback invocation.

`OpenSSL_version` returns bytes, and version-number constants are integers;
host-specific values are not fixed beyond those types.

## Implementation Notes

Keep candidate imports isolated to `OpenSSL` and use public `cryptography`
APIs for conversions and serialization. Preserve insertion order in X.509
names and avoid relying on dictionary ordering for representations. Native
OpenSSL values may vary by the pinned runtime, so test stable semantic
properties rather than host-specific version strings. The verifier runs each
scenario in a fresh unprivileged child process; do not add a test-only entry
point or write reward files from the candidate package.
