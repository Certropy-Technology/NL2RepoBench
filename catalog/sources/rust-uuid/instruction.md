# Anywhere UUID Library — Complete Documentation

## Introduction and Goals of the uuid Project

`uuid` is a Rust library for the Universally Unique Identifier (UUID) types
defined by RFC 9562 (formerly RFC 4122). It gives a program one owned,
`Copy`-able 128-bit value together with the string formats, byte and integer
layouts, variant/version decoding, name-based (SHA-1) generation, explicit
timestamp layout construction, and the parsing error type that applications need
when identifiers arrive from configuration files, databases, URLs, or the
network.

The goal of this task is a complete, offline-buildable Cargo library — not a
collection of modules and not a lookup table of expected strings. A caller must
be able to add the crate as a dependency, `use uuid::{Uuid, Builder, ...}`, and
compile it without network access, without upstream sources, and without any
test or verifier files being present in the workspace.

## Natural Language Instruction (Prompt)

Please create a Rust library package named `uuid` from an empty workspace that
implements the public behaviour described below. The project should include:

1. **Cargo package and crate root.** A normal library package whose package name
   and library name are both `uuid`, whose crate root is `src/lib.rs`, and whose
   dependency set is exactly the single crate offered by the offline closure.
   `Cargo.toml`, `Cargo.lock` and `src/lib.rs` must exist before anything else,
   and the empty skeleton must pass `cargo check --locked --offline`.
2. **Parsing and formatting.** Accept and reject the four input shapes with the
   exact error text, and render the four output formats in both cases through
   `Display`, the format accessors, and the in-place buffer encoders.
3. **Byte, integer, and field layouts.** Big-endian and little-endian byte,
   `u128`, `(u64, u64)` and RFC 9562 field tuple conversions that round-trip
   exactly.
4. **Variant and version decoding.** `Uuid::get_variant`, `Uuid::get_version`,
   and `Uuid::get_version_num` over every nibble value, including the nil and
   max UUIDs.
5. **`Builder` construction and classification.** Every `Builder` constructor,
   the mutator/inspector pair, and the version/variant bit-setting
   classifications (`from_random_bytes`, `from_md5_bytes`, `from_sha1_bytes`,
   `from_custom_bytes`, gregorian and Unix-timestamp layouts).
6. **Deterministic name-based version 5.** `Uuid::new_v5` for the four RFC 9562
   namespace constants, using SHA-1 over the namespace bytes followed by the
   name.
7. **Explicit-input timestamp layouts.** `Timestamp` construction and decoding
   helpers, and the version 1, 6, and 7 layout builders, all driven only by
   caller-supplied values.
8. **Auxiliary public API.** `NonNilUuid`, the `uuid!` macro, the `Error` type
   and its traits, the standard trait surface (`Copy`, `Clone`, `Eq`, `Ord`,
   `Hash`, `Debug`, `Display`, `LowerHex`, `UpperHex`, `Default`, `AsRef`,
   `Borrow`, `From`/`TryFrom`), and the `no_std` profile.

Do not copy upstream source files or tests, do not use the network, and do not
add build scripts, binaries, examples, benchmarks, or fuzz targets. The frozen
upstream revision is the behaviour reference; the contracts written below are
the implementation target.

## Environment Configuration

### Rust Version and Build Mode

```text
rustc 1.97.1
cargo 1.97.1
Cargo edition 2021, rust-version 1.85.0
Cargo network mode: offline
Runtime dependencies: sha1_smol 1.0.0 (default-features = false) only
```

### Core File Requirements

The initial package must contain this working shape before internal modules are
added:

```text
workspace/
├── Cargo.lock
├── Cargo.toml
└── src/
    ├── lib.rs
    └── <internal>.rs      # optional additional modules
```

`Cargo.toml` must declare:

```toml
[package]
name = "uuid"
edition = "2021"

[lib]
name = "uuid"
path = "src/lib.rs"

[features]
default = ["std"]
std = []
v5 = ["sha1"]
sha1 = ["dep:sha1_smol"]

[dependencies]
sha1_smol = { version = "1.0.0", default-features = false, optional = true }
```

`Uuid::new_v5` is only required when the `v5` feature is enabled; the verifier
builds the library with `--features v5`. Everything else in this document is
available with the default features.

Generate `Cargo.lock`, then make the package pass these offline gates before
adding implementation detail, and keep them passing:

```bash
cargo check --locked --offline
cargo check --locked --offline --features v5
cargo check --locked --offline --no-default-features
```

`cargo check --locked --offline --no-default-features` must build a `no_std`
crate: with default features disabled the library may not reference `std` and
must still expose the core parsing, formatting, byte, field, variant, version,
`Builder`, and `Timestamp` API through `core` only.

A `#![no_std]` consumer that depends on this package with
`default-features = false` must also resolve and check offline, for example:

```rust
#![no_std]
use uuid::Uuid;
pub const NIL: Uuid = match Uuid::try_parse("00000000-0000-0000-0000-000000000000") {
    Ok(v) => v,
    Err(_) => Uuid::nil(),
};
pub fn first_byte(input: &str) -> Option<u8> {
    Uuid::try_parse(input).ok().map(|v| v.as_bytes()[0])
}
```

The evaluation imports the package through its library target. A `Cargo.toml`
that points at a missing `src/lib.rs`, or a crate root that does not connect the
implemented modules, is an incomplete submission even when individual module
files contain useful code.

### Offline Dependency Closure

The build environment provides exactly one registry crate, `sha1_smol` 1.0.0,
in a digest-bound read-only Cargo vendor store that is configured through
`CARGO_HOME` (`source.crates-io.replace-with = "vendored-sources"`). Nothing
else can be resolved: declaring any other dependency, a `[patch]` section, or a
`registry` URL makes resolution fail offline and scores as an unbuildable
submission. `sha1_smol` must be declared exactly as above: `optional = true`
and `default-features = false`, so the `no_std` profile never needs it.

## Project Architecture

Internal file names are your choice, but the public boundary must look like
this:

```text
workspace/
├── Cargo.lock
├── Cargo.toml
└── src/
    ├── lib.rs            # required crate root: types, constants, re-exports
    └── <internal>.rs     # optional parsing, formatting, builder, timestamp modules
```

The library target is imported as `uuid` and must export, at the crate root:
`Uuid`, `Bytes`, `Version`, `Variant`, `Builder`, `Error`, `NonNilUuid`,
`Timestamp`, `NoContext`, `ClockSequence`, the `uuid!` macro, and the public
`fmt` and `timestamp` modules.

## API Usage Guide

### `Uuid` representation and layouts

`pub type Bytes = [u8; 16]`. `Uuid` is a 128-bit identifier whose canonical byte
order is big-endian: byte 0 is the first byte of the first RFC 9562 field.

```rust
pub const fn from_bytes(bytes: Bytes) -> Uuid;
pub const fn into_bytes(self) -> Bytes;
pub fn as_bytes(&self) -> &Bytes;
pub const fn from_bytes_le(b: Bytes) -> Uuid;
pub const fn to_bytes_le(&self) -> Bytes;
pub fn as_fields(&self) -> (u32, u16, u16, [u8; 8]);
pub fn to_fields_le(&self) -> (u32, u16, u16, [u8; 8]);
pub const fn from_fields(d1: u32, d2: u16, d3: u16, d4: &[u8; 8]) -> Uuid;
pub const fn from_fields_le(d1: u32, d2: u16, d3: u16, d4: &[u8; 8]) -> Uuid;
pub const fn as_u128(&self) -> u128;
pub const fn to_u128_le(&self) -> u128;
pub const fn from_u128(v: u128) -> Uuid;
pub const fn from_u128_le(v: u128) -> Uuid;
pub const fn as_u64_pair(&self) -> (u64, u64);
pub const fn from_u64_pair(high_bits: u64, low_bits: u64) -> Uuid;
```

* `from_bytes`/`into_bytes`/`as_bytes` preserve the bytes exactly.
* The `_le` variants reverse the order of each of the three integer fields and
  leave the last 64 bits as-is, so `to_bytes_le`/`from_bytes_le` and
  `to_u128_le`/`from_u128_le` are mutually inverse, and
  `Uuid::from_u128(u) == Uuid::from_u128_le(u.to_u128_le())`.
* `as_fields` gives big-endian field values; `to_fields_le` byte-reverses the
  first three fields only.
* `as_u128` equals `u128::from_be_bytes(bytes)`; `as_u64_pair` equals
  `(u64::from_be_bytes(first 8 bytes), u64::from_be_bytes(last 8 bytes))`.
* `pub fn from_slice(b: &[u8]) -> Result<Uuid, Error>` accepts exactly 16 bytes.
* `pub fn from_slice_le(b: &[u8]) -> Result<Uuid, Error>` reverses as
  `from_bytes_le` does.
* `pub fn from_bytes_ref(bytes: &Bytes) -> &Uuid` reborrows without copying.
* `impl TryFrom<&[u8]> for Uuid`, `impl From<Uuid> for Vec<u8>` and
  `impl TryFrom<Vec<u8>> for Uuid` behave like the slice conversions and are
  only available with `std`.

### Parsing strings

```rust
pub fn parse_str(input: &str) -> Result<Uuid, Error>;
pub const fn try_parse(input: &str) -> Result<Uuid, Error>;
pub const fn try_parse_ascii(input: &[u8]) -> Result<Uuid, Error>;
impl FromStr for Uuid;           // Error = Error
impl TryFrom<&str> for Uuid;     // T = Error
impl TryFrom<String> for Uuid;   // T = Error
```

All four input shapes are accepted, case-insensitively, and denote the same
value:

| shape | example |
| --- | --- |
| hyphenated (36 chars) | `a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8` |
| simple (32 chars) | `a1a2a3a4b1b2c1c2d1d2d3d4d5d6d7d8` |
| URN (45 chars) | `urn:uuid:a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8` |
| braced (38 chars) | `{a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8}` |

A hyphenated input must have exactly five groups of lengths `8, 4, 4, 4, 12`.
Any other length, group count, group length, non-hex character, or misplaced
hyphen is an error, reported through `Error`:

| input | `Error`'s `Display` text |
| --- | --- |
| `""` | `invalid length: found 0` |
| `a1a2` | `invalid length: found 4` |
| `a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d` | `invalid group length in group 4: expected 12, found 11` |
| `a1a2a3a4-b1b2-c1c2-d1d2-d3d4-d5d6-d7d8-x` | `invalid group count: expected 5, found 6` |
| `a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7dz` | `invalid character: found `z` at 35` |
| `a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8x` | `invalid character: found `x` at 36` |
| 15-byte slice | `invalid length: expected 16 bytes, found 15` |

Rules for those messages:

* Group indices in `invalid group length in group N` are **zero-based**.
* Character indices in `invalid character: found C at N` are **zero-based**
  indices into the original input, and the reported character is the first
  offending one.
* A `simple`-shaped input of the wrong total length reports
  `invalid length: found N`; an input that looks group-shaped but has a bad
  group reports the group-length form.
* Input that is not valid UTF-8 (only reachable through `try_parse_ascii`)
  reports `non-UTF8 input`.
* `Error` implements `core::fmt::Display`, `Debug`, and
  `std::error::Error` (with `source()` returning `None`). The internal error
  representation is not part of the contract, so `Debug` output is unconstrained.
* `try_parse` is usable in `const` position; `parse_str` need not be.
* `uuid!("...")` is a `macro_rules!` macro usable in `const` items that expands
  to `Uuid::try_parse(...)` and panics at compile time for an invalid literal.

### Formatting strings

`Uuid` implements `Display` (hyphenated lowercase), `Debug` (the same hyphenated
lowercase text), `LowerHex` (32 lowercase hex digits, no hyphens) and
`UpperHex` (32 uppercase hex digits, no hyphens).

```rust
pub const fn hyphenated(&self) -> fmt::Hyphenated;
pub fn as_hyphenated(&self) -> &fmt::Hyphenated;
pub const fn simple(&self) -> fmt::Simple;
pub fn as_simple(&self) -> &fmt::Simple;
pub const fn urn(&self) -> fmt::Urn;
pub fn as_urn(&self) -> &fmt::Urn;
pub const fn braced(&self) -> fmt::Braced;
pub fn as_braced(&self) -> &fmt::Braced;
pub const fn encode_buffer() -> [u8; 45];
```

Each format type `T` in `{Hyphenated, Simple, Urn, Braced}` provides:

```rust
pub const LENGTH: usize;                                  // 36, 32, 45, 38
pub fn from_uuid(uuid: Uuid) -> T;
pub const fn as_uuid(&self) -> &Uuid;
pub const fn into_uuid(self) -> Uuid;
pub fn encode_lower<'a>(&'a self, dst: &'a mut [u8]) -> &'a str;
pub fn encode_upper<'a>(&'a self, dst: &'a mut [u8]) -> &'a str;
impl Display for T;      // lowercase rendering
impl FromStr for T;
impl From<Uuid> for T;  impl From<T> for Uuid;
impl AsRef<Uuid> for T;  impl Borrow<Uuid> for T;
```

Renderings, with `u = a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8`:

| method | text |
| --- | --- |
| `u.hyphenated()` / `u` / `u.as_hyphenated()` | `a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8` |
| `u.hyphenated().encode_upper(&mut buf)` | `A1A2A3A4-B1B2-C1C2-D1D2-D3D4D5D6D7D8` |
| `u.simple()` | `a1a2a3a4b1b2c1c2d1d2d3d4d5d6d7d8` |
| `u.simple().encode_upper(&mut buf)` | `A1A2A3A4B1B2C1C2D1D2D3D4D5D6D7D8` |
| `u.urn()` | `urn:uuid:a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8` |
| `u.braced()` | `{a1a2a3a4-b1b2-c1c2-d1d2-d3d4d5d6d7d8}` |
| `u.braced().encode_upper(&mut buf)` | `{A1A2A3A4-B1B2-C1C2-D1D2-D3D4D5D6D7D8}` |
| `String::from(u)` | the hyphenated lowercase text |

`encode_lower`/`encode_upper` write into the caller's buffer and return a borrow
of it; the buffer must be at least `T::LENGTH` bytes, and the returned text is
not NUL-terminated. `Uuid::encode_buffer()` returns a zeroed `[u8; 45]`, large
enough for every format. `impl From<Uuid> for String` allocates the hyphenated
form.

### Variant and version decoding

```rust
#[repr(u8)] #[non_exhaustive]
pub enum Variant { NCS = 0, RFC4122, Microsoft, Future }
impl core::fmt::Display for Variant;  // "NCS", "RFC4122", "Microsoft", "Future"

#[repr(u8)] #[non_exhaustive]
pub enum Version { Nil = 0, Mac, Dce, Md5, Random, Sha1, SortMac, SortRand, Custom, Max = 0x0f }

pub fn get_variant(&self) -> Variant;
pub const fn get_version_num(&self) -> usize;
pub const fn get_version(&self) -> Option<Version>;
```

The variant is the top bits of byte 8 and behaves as a mask:

| nibble in bits 60..64 | `get_variant()` |
| --- | --- |
| `0`–`7` | `Variant::NCS` |
| `8`–`b` | `Variant::RFC4122` |
| `c`, `d` | `Variant::Microsoft` |
| `e`, `f` | `Variant::Future` |

The version is the high nibble of byte 6. `get_version_num` returns that nibble
as a `usize` and is never an error; `get_version` maps it as follows, with two
value-dependent cases:

| `get_version_num()` | `get_version()` |
| --- | --- |
| `0`, only when every byte is zero (`is_nil()`) | `Some(Version::Nil)` |
| `1`…`8` | `Some(Mac/Dce/Md5/Random/Sha1/SortMac/SortRand/Custom)` respectively |
| `0xf`, only when every byte is `0xff` (`is_max()`) | `Some(Version::Max)` |
| anything else, including `0` and `0xf` on other values | `None` |

`Uuid::nil()` is the all-zeroes UUID, `Uuid::max()` the all-ones UUID, both
usable in `const` context; `is_nil()`/`is_max()` report those two cases,
`Default::default()` equals `Uuid::nil()`.

### `Builder`

```rust
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Builder(Uuid);

pub const fn nil() -> Builder;
pub fn set_variant(&mut self, v: Variant) -> &mut Self;
pub const fn with_variant(self, v: Variant) -> Self;
pub fn set_version(&mut self, v: Version) -> &mut Self;
pub const fn with_version(self, v: Version) -> Self;
pub const fn as_uuid(&self) -> &Uuid;
pub const fn into_uuid(self) -> Uuid;
```

Constructors (all associated functions of `Builder`):

```rust
pub const fn from_bytes(b: Bytes) -> Builder;
pub const fn from_bytes_le(b: Bytes) -> Builder;
pub fn from_slice(b: &[u8]) -> Result<Builder, Error>;
pub fn from_slice_le(b: &[u8]) -> Result<Builder, Error>;
pub const fn from_fields(d1: u32, d2: u16, d3: u16, d4: &[u8; 8]) -> Builder;
pub const fn from_fields_le(d1: u32, d2: u16, d3: u16, d4: &[u8; 8]) -> Builder;
pub const fn from_u128(v: u128) -> Builder;
pub const fn from_u128_le(v: u128) -> Builder;
pub const fn from_gregorian_timestamp(ticks: u64, counter: u16, node_id: &[u8; 6]) -> Builder;
pub const fn from_sorted_gregorian_timestamp(ticks: u64, counter: u16, node_id: &[u8; 6]) -> Builder;
pub const fn from_unix_timestamp_millis(millis: u64, counter_random_bytes: &[u8; 10]) -> Builder;
pub const fn from_md5_bytes(md5_bytes: Bytes) -> Builder;
pub const fn from_sha1_bytes(sha1_bytes: Bytes) -> Builder;
pub const fn from_random_bytes(random_bytes: Bytes) -> Builder;
pub const fn from_custom_bytes(custom_bytes: Bytes) -> Builder;
```

`into_uuid`/`as_uuid` return the bytes untouched, so a plain `from_bytes`
builder round-trips exactly. `with_version`/`set_version` overwrite only the high
nibble of byte 6 (`b6 = (b6 & 0x0F) | (version as u8) << 4`), and
`with_variant`/`set_variant` rewrite only byte 8:

| requested variant | byte 8 after the write |
| --- | --- |
| `Variant::NCS` | `b8 & 0x7F` |
| `Variant::RFC4122` | `(b8 & 0x3F) \| 0x80` |
| `Variant::Microsoft` | `(b8 & 0x1F) \| 0xC0` |
| `Variant::Future` | `b8 \| 0xE0` |

All other bytes are preserved. The four "classification" constructors set version and
variant for a caller-supplied 16-byte block, without interpreting anything else
about it:

| constructor | version nibble | variant |
| --- | --- | --- |
| `from_random_bytes` | `4` (`Version::Random`) | `RFC4122` |
| `from_md5_bytes` | `3` (`Version::Md5`) | `RFC4122` |
| `from_sha1_bytes` | `5` (`Version::Sha1`) | `RFC4122` |
| `from_custom_bytes` | `8` (`Version::Custom`) | `RFC4122` |

Each classification keeps every input bit except the four version bits of byte 6
and the variant bits of byte 8, which are overwritten as in the table above.

### Name-based version 5 (SHA-1)

```rust
pub fn new_v5(namespace: &Uuid, name: &[u8]) -> Uuid;   // feature "v5"
pub const NAMESPACE_DNS: Uuid;   // 6ba7b810-9dad-11d1-80b4-00c04fd430c8
pub const NAMESPACE_URL: Uuid;   // 6ba7b811-9dad-11d1-80b4-00c04fd430c8
pub const NAMESPACE_OID: Uuid;   // 6ba7b812-9dad-11d1-80b4-00c04fd430c8
pub const NAMESPACE_X500: Uuid;  // 6ba7b814-9dad-11d1-80b4-00c04fd430c8
```

`new_v5` hashes `namespace.as_bytes()` immediately followed by `name` with
SHA-1, takes the **first 16 bytes** of the 20-byte digest, then applies the
`from_sha1_bytes` classification (version nibble `5`, variant `RFC4122`) and
returns that UUID. It is a pure function: the same namespace and name always
produce the same identifier, `get_version()` is `Some(Version::Sha1)`, an empty
name and a 4096-byte name are both valid, and non-ASCII names are hashed by
their raw bytes. The four namespace constants are exactly the RFC 9562 values
listed above (`get_version_num() == 1`, `get_variant() == RFC4122`).

### Explicit-input timestamps: versions 1, 6, and 7

```rust
pub const fn from_unix_timestamp_millis(millis: u64, counter_random_bytes: &[u8; 10]) -> Builder;
pub const fn from_gregorian_timestamp(ticks: u64, counter: u16, node_id: &[u8; 6]) -> Builder;
pub const fn from_sorted_gregorian_timestamp(ticks: u64, counter: u16, node_id: &[u8; 6]) -> Builder;
pub fn get_timestamp(&self) -> Option<Timestamp>;
pub const fn get_node_id(&self) -> Option<[u8; 6]>;
```

Version 7 layout from `from_unix_timestamp_millis(millis, c)`, where `c` is the
10-byte counter/random block (`c0` first):

* field 1 (32 bits) = bits 16..48 of `millis`, i.e. `(millis >> 16) & 0xFFFF_FFFF`
* field 2 (16 bits) = the low 16 bits of `millis`
* field 3 (16 bits) = `(u16::from_be_bytes([c0, c1]) & 0x0FFF) | (7 << 12)`
* bytes 8..16 = `c[2] & 0x3F | 0x80`, then `c[3..10]` verbatim

So only the low **48 bits** of `millis` are stored: two millisecond values that
agree modulo `2^48` produce the same identifier (including `0` versus
`1 << 48`, and `u64::MAX` versus `2^48 - 1`), and `get_timestamp()` decodes the
stored field back to seconds plus sub-second nanoseconds at millisecond
precision. Ordering follows the stored 48-bit field, so increasing `millis`
within 48 bits yields increasing UUIDs. The version nibble is `7`, the variant
is `RFC4122`, and only 12 bits of `c[0..2]` and 6 bits of `c[2]` survive.

Version 1 (`from_gregorian_timestamp(ticks, counter, node)`), where `ticks` are
100-nanosecond intervals since 1582-10-15 00:00:00:

* field 1 (32 bits) = the low 32 bits of `ticks`
* field 2 (16 bits) = bits 32..48 of `ticks`
* field 3 (16 bits) = `((ticks >> 48) & 0x0FFF) | (1 << 12)` (version nibble `1`)
* byte 8 = `((counter & 0x3F00) >> 8) | 0x80`, byte 9 = `counter & 0xFF`
  (so the counter keeps 14 bits and byte 8 carries the RFC 4122 variant)
* bytes 10..16 = `node` verbatim

Version 6 (`from_sorted_gregorian_timestamp`) uses the same `ticks`/`counter`
inputs but stores them in sortable order with version nibble `6`.

`get_node_id()` returns `Some(node)` only for versions `Mac` and `SortMac`.
`get_timestamp()` returns `Some` only for versions `Mac`, `SortMac`, and
`SortRand`; the counter is decoded as 14 bits for versions 1/6 and is truncated
to millisecond precision for version 7, so these decoders do not generally
round-trip the exact input.

The `Timestamp` API is:

```rust
pub const fn from_gregorian(ticks: u64, counter: u16) -> Timestamp;   // alias of from_gregorian_time
pub const fn from_gregorian_time(ticks: u64, counter: u16) -> Timestamp;
pub const fn from_unix_time(seconds: u64, subsec_nanos: u32, counter: u128, usable_counter_bits: u8) -> Timestamp;
pub fn from_unix(context: impl ClockSequence<Output = impl Into<u128>>, seconds: u64, subsec_nanos: u32) -> Timestamp;
pub const fn to_gregorian(&self) -> (u64, u16);
pub const fn to_unix(&self) -> (u64, u32);
pub const fn from_rfc4122(ticks: u64, counter: u16) -> Timestamp;    // alias, same values
pub const fn to_rfc4122(&self) -> (u64, u16);
pub trait ClockSequence {
    type Output;
    fn generate_sequence(&self, seconds: u64, subsec_nanos: u32) -> Self::Output;
    fn usable_bits(&self) -> usize;
}
pub struct NoContext;   // Output = u16, always 0, usable_bits() == 0
```

Gregorian↔Unix conversion is exact at 100 ns resolution: the 1582 epoch offset
is `122192928000000000` ticks, so `Timestamp::from_gregorian(60_000_000_000_000_000, 7)`
has `to_gregorian() == (60_000_000_000_000_000, 7)` and
`to_unix() == (1_838_455_114_570, 955_161_600)`, and
`Timestamp::from_unix(&NoContext, 1_700_000_123, 456_000_000).to_unix()`
returns that same `(seconds, subsec_nanos)` pair because `NoContext` contributes
no counter. `Timestamp::now` is **not** part of the contract and must not be
used by the verifier's assertions.

### `NonNilUuid`

```rust
pub struct NonNilUuid(/* nonzero 128-bit value */);
pub const fn new(uuid: Uuid) -> Option<NonNilUuid>;
pub const fn get(&self) -> &Uuid;
impl TryFrom<Uuid> for NonNilUuid;      // Error = Error, text "the UUID is nil"
impl From<NonNilUuid> for Uuid;
impl PartialEq<Uuid> for NonNilUuid;    impl PartialEq<NonNilUuid> for Uuid;
impl PartialOrd<Uuid> for NonNilUuid;   impl PartialOrd<NonNilUuid> for Uuid;
impl Display for NonNilUuid;  impl Debug for NonNilUuid;
```

`new` returns `None` for `Uuid::nil()` and `Some` for every other value
including `Uuid::max()`. `Display`/`Debug` render the underlying hyphenated
text, comparison with `Uuid` compares the identifiers, and ordering follows the
same rule as `Uuid`'s.

### Ordering, hashing, and equality

`Uuid` derives `Clone`, `Copy`, `Debug`, `Eq`, `PartialEq`, `Ord`, `PartialOrd`
and implements `Hash`. Comparison and hashing are over the **big-endian byte
order of the identifier**: sorting a set of identifiers ascending yields
`00000000-…-000`, `00000000-…-001`, `015cb15a-…`, `a1a2a3a4-…`,
`ffffffff-ffff-ffff-ffff-ffffffffffff`. `Hash` must agree with `Eq`, so
inserting an equal value into a `HashMap`/`HashSet` never grows it.
`AsRef<Uuid>`, `AsRef<[u8]>`, `Borrow<Uuid>` and `Hash` are implemented on
`Uuid` itself.

## Implementation Notes

* Work in public-API order: crate root and `Uuid` byte layout first, then
  parsing/formatting, then `Variant`/`Version` decoding, then `Builder`,
  then the name-based and timestamp layouts, then `NonNilUuid`, the `uuid!`
  macro, and the `Error`/trait surface. Keep a compiling crate root throughout
  rather than postponing it.
* Determinism is required. Any use of a random source or of the current clock
  inside the contracted API is a defect: `new_v5` depends only on its arguments,
  and every timestamp layout takes its time value as an explicit input.
* Exact text matters. Hyphenation, lowercase versus uppercase, the group
  indices and character offsets in `Error`'s `Display` text, the
  `urn:uuid:`/`{}` wrappers, and `Variant`'s four `Display` names are all part
  of the contract.
* SHA-1 must be the standard FIPS 180-1 algorithm over the concatenated
  namespace and name bytes. Either use the provided `sha1_smol` crate or
  implement SHA-1 yourself; only its digest bytes are observable.
* Keep the crate free of `build.rs`, binaries, examples, benchmarks, and fuzz
  targets, and do not add `[patch]` or `[replace]` sections. Internal module
  names are unconstrained; only the exported paths above are observable.
* The verifier runs the candidate through a separate bridge process. Hidden
  scenarios, expected observations, and verifier code are not part of the
  candidate workspace, and any `reward.json`, `junit.xml`, or report file the
  candidate writes is ignored: grading is produced by the verifier alone.

### Deliberately excluded scope

These upstream behaviours are out of contract, are never asserted, and must not
be added as extra requirements:

* **Ambient randomness and clocks:** `Uuid::new_v4`, `Uuid::now_v7`,
  `Uuid::new_v7`, `Timestamp::now`, `ContextV1`, `ContextV7`,
  `ThreadLocalContext`, `Context`, `Builder::new_random`-style RNG contexts, and
  the `rng`/`fast-rng`/`v4`/`v7`/`atomic`/`js` features. They need OS entropy or
  wall-clock state that a deterministic black-box bridge cannot pin down. Only
  the explicit-input layouts above are contracted.
* **Version 1/6 automatic construction** (`uuid::v1` module, `context` module):
  same reason; the manual `Builder` layouts remain contracted.
* **Version 3 (MD5)** and `md5`/`sha1`-external hashing choices other than
  SHA-1: the offline closure provides only `sha1_smol`, so `Md5`-based
  generation is not asserted (the `Version::Md5` enum value and the
  `from_md5_bytes` bit layout are still contracted).
* **Optional integrations:** `serde`, `borsh`, `slog`, `arbitrary`, `bytemuck`,
  `zerocopy`, `wasm-bindgen`/`js`, the `macro-diagnostics` no-op, and the
  `uuid-rng-internal` workaround crate.
* **Non-contract formatting extras:** `Timestamp::to_unix_nanos` (it panics at
  this revision as a deprecated stub), `Builder::from_rfc4122_timestamp` and
  `Builder::from_sorted_rfc4122_timestamp` (deprecated aliases of the gregorian
  builders), `NonNilUuid::new_unchecked` and `Uuid::from_bytes_ref` beyond the
  documented signature, `Uuid::get_hyphenated`-style legacy names, and the
  `Error`/`ErrorKind` `Debug` representation, whose internal variant names are
  not a public guarantee.
* **Upstream's own test suites, benchmarks, docs, and fuzz targets**, which
  need dev-dependencies outside the offline closure.
