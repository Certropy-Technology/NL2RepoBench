# rust-uuid provenance and scope

- Task id: `rust-uuid`. The bare `uuid` id belongs to an existing Python task and is
  untouched; this Rust lane follows the `go-semver`/`rust-semver` language-prefix
  convention instead of redefining an existing identity.
- Upstream: <https://github.com/uuid-rs/uuid>
- Frozen revision: `cdc96a87bddc38d0eb8f894c764e151d2299b4b3` (lightweight tag
  `v1.26.0`; `refs/tags/v1.26.0^{}` returns no peeled object, so the tag names this
  commit directly and the crate manifest declares version `1.26.0`)
- License: `Apache-2.0 OR MIT` exactly as the frozen manifest declares it.
  `LICENSE-MIT` (1157 bytes, `sha256:436bc5a105d8e57dcd8778730f3754f7bf39c14d2f530e4cde4bd2d17a83ec3d`),
  `LICENSE-APACHE` (10847 bytes, `sha256:a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`)
  and `COPYRIGHT` (432 bytes, `sha256:b4b2c0de2a05de3372d5c828128413ce82bb7dba2272487b7729f09cc3d3519d`)
  are installed beside the sources by the Oracle.
- Source archive: `git archive --format=tar --prefix=uuid/ FETCH_HEAD` after
  `git fetch --depth 1 origin <revision>` and `test "$(git rev-parse FETCH_HEAD)" = <revision>`
- Source digest: `sha256:38fe6ae37eee2f679a0490224c2bf413703dc7877ce35cc0bf11f2999d412590`
  (450560 bytes; recomputed from an independent second archive and identical)
- Public instruction digest: `sha256:cd563ffecc28561b97e22997f969967a29fac23ed42d5bc62da939cfc34bb429`
- Generated projection: `catalog/tasks/rust-uuid`, mode `production`, 97 inventoried files, bundle manifest `sha256:d4a929d93b0a0d140b23f410706174d1d59204a14c052d1c55a34da625e556cd`, canonical manifest `sha256:ef7e8337c01e70d57def5ea435276db955294cf00c26417d004b28bad80cd922`, toolchain lock `sha256:88aa3aefd7770ec0a4c16cf9d43a386f5dc5e1fb1343d8ba97879b972b77717a` (Rust/Cargo 1.97.1)
- Build script: none. The frozen package publishes `include = ["src", README, licences]`
  and has neither `build.rs` nor `[build-dependencies]`; `rng/`, `tests/`, `examples/`
  and `fuzz/` in the archive are separate workspace crates that the Oracle never installs,
  so there is no build-script execution surface to gate and the `build-script-*` controls
  do not apply to this task.

## Runtime closure

The candidate, the Oracle workspace and the verifier all resolve exactly one registry
crate, `sha1_smol 1.0.0`, from a private digest-bound Cargo closure holding `Cargo.lock`
(version 4, two packages), `vendor/sha1_smol` with `.cargo-checksum.json`, and the
checksum-matched `registry/cache/sha1_smol-1.0.0.crate`. `CargoPackageManager`
`validate_offline_store` passes against Rust/Cargo 1.97.1: 17 inventoried files, vendor
bytes equal to the published crate archive byte for byte.

`sha1_smol` is `dep:sha1_smol`-optional behind the `sha1`/`v5` features, so the
`--no-default-features` profile needs no dependency at all and stays `#![no_std]`.

Upstream's own manifest is **not** installed. It additionally declares the optional
`serde_core`, `slog`, `arbitrary`, `bytemuck`, `zerocopy`, `borsh`, `wasm-bindgen`,
`js-sys`, `getrandom`, `rand`, `md-5`, `atomic` and `uuid-rng-internal-lib` entries plus a
dev-dependency tree (`serde`, `serde_derive`, `serde_json`, `serde_test`, `trybuild`,
`rustversion`, `gungraun`, `wasm-bindgen-test`). None of those are part of this contract or
present in the offline closure, and the RNG/dev entries exist only for the excluded
ambient-random surface. The contract manifest keeps the package/lib names, edition,
`rust-version`, license, description, and the `std`/`v5`/`sha1` feature shape that the
instruction publishes; it drops `macro-diagnostics` (a documented no-op) and the
docs.rs/playground/badge metadata. This is the documented packaging relaxation, not a
behaviour change.

Bundles (deterministic uncompressed-membership gzip ustar archives, sorted regular files,
root uid/gid, fixed 2020-01-01 mtime, mode 0644 / 0755 for `solve.sh`):

| bundle | digest | bytes |
| --- | --- | --- |
| cargo | `sha256:76c98313887b5ab5bbe8e73ed0b77ccdf6469efe70ad9fd65b8479000f61d48e` | 22490 |
| verifier | `sha256:7e7b14e02cbf68f1d61f26dce6203eae81f752d684a5a39abb639e3385ea1f38` | 15502 |
| oracle | `sha256:ce781fb478987cd7521141ebeac1c12b47edd5d8613d92df76f1f760bd928067` | 1560 |

A rebuild of the same inputs into two different store roots reproduced all three digests.

## Scope decisions

The contract covers RFC 9562 identity handling that is a pure function of its inputs:

* the four accepted string shapes, the four rendered shapes, both hex cases, the buffer
  encoders, the `T::LENGTH` constants and the `From`/`Into`/`AsRef`/`Borrow`/`FromStr`
  conversions on the format objects;
* the exact rejection messages, including zero-based group indices and character offsets;
* big-endian and little-endian byte, `u128`, `(u64, u64)` and field-tuple layouts;
* `get_variant` (mask semantics over all 16 nibbles), `get_version_num`, and the
  `get_version` table including the nil/max-only values;
* `Builder`: every constructor, the variant/version masks, `as_uuid`/`into_uuid`, and the
  `from_random_bytes`/`from_md5_bytes`/`from_sha1_bytes`/`from_custom_bytes` classifications;
* deterministic name-based version 5 over the four RFC 9562 namespaces;
* the explicit-input version 1, 6, and 7 layouts, the 48-bit millisecond truncation, and
  `get_timestamp`/`get_node_id` decoding;
* `Timestamp` construction/decoding against `NoContext`, `NonNilUuid`, the `uuid!` macro,
  the `Error` trait surface, ordering/hashing/equality, and the `no_std` profile.

Deliberately excluded, recorded in `test-inventory.json` and published in
`instruction.md`, because the observation is either nondeterministic or needs bytes that
are not in the offline closure:

* **Ambient randomness and wall-clock state:** `Uuid::new_v4`, `Uuid::now_v7`,
  `Uuid::new_v7`, `Timestamp::now`, `ContextV1`/`ContextV7`/`Context`/
  `ThreadLocalContext`, and the `rng`/`fast-rng`/`v4`/`v7`/`atomic`/`js` feature surface
  (`getrandom`, `rand`, `atomic`). A frozen expectation cannot be placed on an entropy or
  clock source, and the contracted explicit-input builders keep the version 1/6/7 bit
  layouts fully testable without them.
* **Version 3 (MD5) generation:** `md-5` (and its `digest`/`block-buffer`/`crypto-common`
  tree) is outside the two-package closure. The `Version::Md5` enum value and the
  `Builder::from_md5_bytes` bit layout stay contracted because they need no hashing.
* **Optional integrations:** `serde`, `borsh`, `slog`, `arbitrary`, `bytemuck`,
  `zerocopy`, `wasm-bindgen`/`js`, `uuid-rng-internal-lib`, and the deprecated
  `macro-diagnostics` no-op.
* **`Timestamp::to_unix_nanos`:** at this revision it is a deprecated stub that *panics*, so
  it is published as out of contract instead of being asserted or silently reimplemented.
* **Deprecated aliases** `Builder::from_rfc4122_timestamp` and
  `Builder::from_sorted_rfc4122_timestamp`, and the `Error`/`ErrorKind` `Debug`
  representation: its newtype output prints internal variant names, which are not a public
  guarantee, so the contract asserts `Display` and `std::error::Error` instead.
* **Upstream's own `#[cfg(test)]` suites, benches, examples, `rng/` crate and fuzz targets**,
  which need the dev-dependency tree and the excluded features.

No expectation is derived from upstream test text: all 29 adapter observations were captured
by replaying the candidate-linked adapter against the digest-verified frozen archive, and
the checker stores them hex-encoded in the private verifier bundle only. `instruction.md`,
`api-inventory.json`, `test-inventory.json` and this file contain no expected observation,
fixture identifier, or absolute private path.
