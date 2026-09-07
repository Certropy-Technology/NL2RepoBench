# Rustc-hash Rust Library - Complete Documentation

## Introduction and Goals of the Rustc-hash Project

`rustc-hash` is a small Rust library that provides the fast, non-cryptographic
Fx hashing algorithm used by rustc. It exposes a `Hasher`, a deterministic
`BuildHasher`, aliases for standard `HashMap` and `HashSet`, and a seeded state
for callers that need reproducible hash values. Recreate the public library
from an empty Cargo workspace; do not copy upstream source or tests.

## Natural Language Instruction (Prompt)

Please create a complete Rust library package named `rustc-hash`. Implement the
following public behavior:

1. **Cargo package**: Create `Cargo.toml`, `Cargo.lock`, and `src/lib.rs` for a
   library crate named `rustc_hash`. The crate root must connect all internal
   modules and re-export the public types and aliases below.
2. **FxHasher**: Implement `FxHasher::default()`, `FxHasher::with_seed(usize)`,
   and the standard `core::hash::Hasher` methods for bytes, strings, signed and
   unsigned integer widths, and `finish()`. Wrapping arithmetic and the
   platform pointer width behavior are observable.
3. **BuildHasher and collections**: Implement `FxBuildHasher` as a
   deterministic `BuildHasher`, plus `FxHashMap<K, V>` and `FxHashSet<V>`
   aliases using it. Default maps and sets must insert, look up, remove, and
   iterate normal standard-library collections.
4. **Seeded state**: Implement `FxSeededState::with_seed(usize)` and its
   `BuildHasher` behavior. Equal seeds produce equal hash results; different
   seeds produce different results for the probe inputs. Expose
   `FxHashMapSeed` and `FxHashSetSeed` aliases when the `std` feature is on.
5. **Features**: The default `std` feature must compile the collection aliases.
   `default-features = false` must compile as a `no_std` library with `alloc`.
   The declared `backtrace`-independent feature surface must not fetch anything.
   The optional `rand` API is outside this task's fixed contract and need not
   be implemented.
6. **Offline checks**: First create the package skeleton and make it pass
   `cargo check --locked --offline`. Keep a compilable crate root while adding
   each API group. Before finishing run both default-feature and
   `cargo check --locked --offline --no-default-features` checks.

The evaluator imports the library through Cargo; disconnected module files are
not sufficient. Do not add binaries, network clients, build-time downloads,
absolute-path generated files, or hidden test files.

## Environment Configuration

```text
rustc 1.97.1
Cargo edition 2021
Cargo network mode: offline
Runtime dependencies: none
```

The implementation must work on Linux/amd64 with the locked stable toolchain.

## Project Architecture

```text
workspace/
├── Cargo.lock
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── seeded_state.rs       # optional internal module
    └── <other internal>.rs   # optional implementation modules
```

`src/lib.rs` is required and is the public crate root. Internal names and
module layout are otherwise your choice.

## API Usage Guide

Import the API with:

```rust
use rustc_hash::{FxBuildHasher, FxHashMap, FxHashSet, FxHasher, FxSeededState};
use std::hash::{BuildHasher, Hash, Hasher};
```

### `FxHasher`

```rust
pub struct FxHasher { /* opaque state */ }
impl FxHasher {
    pub const fn default() -> Self;
    pub const fn with_seed(seed: usize) -> Self;
}
impl Hasher for FxHasher {
    fn finish(&self) -> u64;
    fn write(&mut self, bytes: &[u8]);
    fn write_u8(&mut self, value: u8);
    fn write_u16(&mut self, value: u16);
    fn write_u32(&mut self, value: u32);
    fn write_u64(&mut self, value: u64);
    fn write_u128(&mut self, value: u128);
    fn write_usize(&mut self, value: usize);
    // standard Hasher defaults cover the signed integer methods
}
```

`write(&[u8])` and the typed integer methods are deterministic. A fresh
default hasher and a fresh hasher with the same seed produce the same result
for the same input. `finish()` returns the platform-specific Fx hash result;
do not replace it with a generic or randomized hash.

### `FxBuildHasher` and collection aliases

```rust
pub struct FxBuildHasher;
impl BuildHasher for FxBuildHasher { type Hasher = FxHasher; }
pub type FxHashMap<K, V> = std::collections::HashMap<K, V, FxBuildHasher>;
pub type FxHashSet<V> = std::collections::HashSet<V, FxBuildHasher>;
```

`FxBuildHasher::default().build_hasher()` must produce a default-seeded
`FxHasher`. The aliases retain ordinary `HashMap`/`HashSet` semantics.

### `FxSeededState`

```rust
#[derive(Clone)]
pub struct FxSeededState;
impl FxSeededState {
    pub const fn with_seed(seed: usize) -> Self;
}
impl BuildHasher for FxSeededState { type Hasher = FxHasher; }
pub type FxHashMapSeed<K, V> = std::collections::HashMap<K, V, FxSeededState>;
pub type FxHashSetSeed<V> = std::collections::HashSet<V, FxSeededState>;
```

The state retains the supplied seed. Cloning it preserves hash results, and
two states made with different seeds must not collapse to the same result for
the ordinary integer and byte probes.

## Implementation Notes

Use `core` for hashing traits and gate standard collection aliases behind
`std`. Preserve the public names, type aliases, const constructors, and
feature behavior. Test integer widths, byte slices, empty input, non-ASCII
bytes, seed changes, map/set mutation, and repeated deterministic hashing.
