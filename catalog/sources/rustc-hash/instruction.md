## Project Description

Recreate the public Rust library `rustc-hash` from an empty workspace. The
package is a small, deterministic, non-cryptographic hashing library for Rust
programs that need a fast `Hasher`, a matching `BuildHasher`, or standard
library maps and sets configured with that hasher.

The package name in Cargo metadata is `rustc-hash`; the Rust import crate is
`rustc_hash`. The target users are library and application authors who already
use the `core::hash` traits and want a stable, explicit hashing policy for a
map, set, or bounded hash calculation.

The candidate must create a complete installable library package. It must
provide the public root exports listed in the API guide, connect the root to
any internal modules, and preserve the feature behavior described below. A
crate that only contains disconnected helper files is incomplete.

In scope are the `FxHasher` state and its `core::hash::Hasher` implementation,
the zero-seed `FxBuildHasher`, the explicitly seeded `FxSeededState`, and the
standard `HashMap`/`HashSet` aliases that use those states. Byte slices,
strings hashed through the standard `Hash` trait, every standard integer width,
empty input, repeated hashing, cloning of seeded state, and normal map/set
mutation are observable behavior.

The implementation is not a cryptographic hash and must not claim resistance
to deliberate collision attacks. It must not add a binary, a command-line
application, a network client, a build script that downloads data, or an
absolute-path dependency. Do not copy upstream source or tests into the
candidate package.

The fixed contract intentionally excludes the optional `rand` API and the
nightly-only `Hasher` extension methods. Those surfaces are not confidently
bindable for this task and should not be added as required behavior.

## Natural Language Instruction

Create a Rust library package named `rustc-hash` with a library target whose
crate import path is `rustc_hash`. Implement the following capabilities:

1. Export `FxHasher`, including its const constructors and the standard
   `Hasher` methods for bytes and integer values.
2. Export `FxBuildHasher`, whose `BuildHasher` implementation creates a fresh
   default-seeded `FxHasher` for each call.
3. Export `FxHashMap<K, V>` and `FxHashSet<V>` as standard collection aliases
   using `FxBuildHasher` when the `std` feature is enabled.
4. Export `FxSeededState`, retaining the caller's `usize` seed and creating
   hashers with that seed through `BuildHasher`.
5. Export `FxHashMapSeed<K, V>` and `FxHashSetSeed<V>` as seeded standard
   collection aliases when `std` is enabled.
6. Make both the default-feature and `--no-default-features` library builds
   pass the locked offline Cargo checks. The base crate is `no_std`; collection
   aliases are gated by the declared `std` feature.

Do not change the public names, package identity, feature names, or return
shapes. Keep all hashing state local to the hasher or builder object. A fresh
hasher must not inherit state from an earlier hasher, and two equal seeds must
produce equal observations for equal inputs.

## Supports

- Language: Rust, edition 2021.
- Runtime/toolchain: `rustc 1.97.1` on Linux amd64.
- Cargo package name: `rustc-hash`.
- Import crate name: `rustc_hash`.
- Runtime dependencies: none.
- Build dependencies: none.
- Cargo features declared by the frozen package: `default = ["std"]`, `std`,
  and `nightly`. The fixed task requires the default `std` behavior and the
  no-default-features library build. Nightly-only extensions are excluded from
  the public contract.
- Network policy: no network during candidate, verifier, Oracle, or controls
  execution. Do not contact GitHub, crates.io, a registry mirror, DNS, or any
  external service at runtime.
- Dependency policy: use only the standard/core library facilities already
  available to the Rust toolchain. Keep Cargo metadata and lockfile valid for
  `--locked --offline` operation.
- The harness runs Cargo from the project root. It provides the locked
  toolchain and invokes bounded Rust bridge operations in a separate process;
  the candidate does not write trusted reports or verifier output.

## Project Directory Structure

Create the following project rooted at `workspace/`:

```text
workspace/
├── Cargo.toml
├── Cargo.lock
└── src/
    ├── lib.rs
    └── seeded_state.rs
```

`Cargo.toml` is the install and feature entry point. It must identify the
package as `rustc-hash`, version `2.1.3`, and edition 2021, and point the
library target at `src/lib.rs`. It must declare the `std` feature and make it
the default feature without adding runtime packages.

`src/lib.rs` is the public crate root. It must define or re-export
`FxHasher`, `FxBuildHasher`, `FxSeededState`, `FxHashMap`, `FxHashSet`,
`FxHashMapSeed`, and `FxHashSetSeed` from the crate root. The root must compile
with and without its default feature.

`src/seeded_state.rs` may contain the seeded builder and seeded collection
aliases. Internal organization is otherwise an implementation choice, but
every module required by `lib.rs` must be present below `src/`.

There is no CLI and no executable entry point for this task. Do not create
`main.rs`, a `bin/` directory, a network service, or an installation script.

## API Usage Guide

### Crate Root Imports

Import the public types from the crate root:

```rust
use rustc_hash::{FxBuildHasher, FxHashMap, FxHashSet, FxHasher, FxSeededState};
use core::hash::{BuildHasher, Hash, Hasher};
```

With the default `std` feature, the two seeded aliases are also imported from
`rustc_hash`. With `default-features = false`, use the hasher and builder APIs
but do not assume that `std::collections` aliases are available.

### `rustc_hash::FxHasher`

`FxHasher` is a public opaque hasher state. It implements `Clone` and
`core::hash::Hasher`. Its state is local to one value; calling `finish` does
not consume it.

```rust
pub struct FxHasher { /* opaque state */ }
impl FxHasher {
    pub const fn default() -> Self;
    pub const fn with_seed(seed: usize) -> Self;
}
```

`default()` returns a fresh hasher with the library's default zero seed.
`with_seed(seed)` returns a fresh hasher initialized with the supplied
platform-sized unsigned seed. Neither constructor reads files, environment
variables, clocks, randomness, or global mutable state.

The ordinary example below hashes a byte string and reads the result:

```rust
use core::hash::{Hasher, Hash};
use rustc_hash::FxHasher;

let mut h = FxHasher::default();
"config".hash(&mut h);
let first: u64 = h.finish();
assert_eq!(first, h.finish());
```

The empty-input boundary is also valid. A fresh hasher may receive an empty
slice and must still return a deterministic `u64`:

```rust
use core::hash::Hasher;
use rustc_hash::FxHasher;

let mut h = FxHasher::default();
h.write(&[]);
let empty_hash = h.finish();
assert_eq!(empty_hash, h.finish());
```

### `Hasher::write` on `FxHasher`

The implemented trait method has the complete signature:

```rust
fn write(&mut self, bytes: &[u8]);
```

It accepts any byte slice, including an empty slice and bytes that are not
valid UTF-8. It updates only the receiver and returns unit. The result of
`finish()` after the same sequence of writes is deterministic for the same
target pointer width, input bytes, and initial seed. It does not sort, decode,
normalize, or otherwise reinterpret arbitrary bytes.

```rust
use core::hash::Hasher;
use rustc_hash::FxHasher;

let bytes = [0x00, 0xff, 0x10];
let mut h = FxHasher::default();
h.write(&bytes);
let value = h.finish();
assert_eq!(value, h.finish());
```

Repeated `write` calls update the same state in order. A fresh hasher that is
never given the first call must not be treated as equivalent to a hasher after
that call. Do not expose or depend on the private representation of the state.

### Typed `Hasher` Methods on `FxHasher`

`FxHasher` provides these typed trait methods with their standard signatures:

```rust
fn write_u8(&mut self, value: u8);
fn write_u16(&mut self, value: u16);
fn write_u32(&mut self, value: u32);
fn write_u64(&mut self, value: u64);
fn write_u128(&mut self, value: u128);
fn write_usize(&mut self, value: usize);
```

Each accepts the full domain of its corresponding unsigned type, updates only
the receiver, and returns unit. The standard `Hasher` defaults provide the
signed integer methods through the trait contract, so signed values must be
hashable as well. Preserve width distinctions and the platform-dependent
`usize` behavior rather than converting all values through a textual format.

For an ordinary typed call:

```rust
use core::hash::Hasher;
use rustc_hash::FxHasher;

let mut h = FxHasher::default();
h.write_u32(42);
let result = h.finish();
```

Boundary calls are valid and must not panic merely because a value is at its
minimum or maximum:

```rust
use core::hash::Hasher;
use rustc_hash::FxHasher;

let mut h = FxHasher::default();
h.write_u8(u8::MAX);
h.write_u128(u128::MAX);
h.write_usize(usize::MAX);
let result = h.finish();
```

### `Hasher::finish` on `FxHasher`

The implemented method has signature `fn finish(&self) -> u64`. It observes
the current state without resetting it. Calling it twice without another write
returns the same value. Different input sequences or initial seeds are allowed
to produce different values; callers must not assume cryptographic collision
resistance or a particular value when compiling for a different pointer
width.

### `rustc_hash::FxBuildHasher`

`FxBuildHasher` is a public zero-sized builder implementing
`core::hash::BuildHasher` with `FxHasher` as its associated hasher:

```rust
pub struct FxBuildHasher;
impl BuildHasher for FxBuildHasher {
    type Hasher = FxHasher;
    fn build_hasher(&self) -> FxHasher;
}
```

It is copyable and has the ordinary default value. `build_hasher` takes `&self`,
returns a new independent default-seeded `FxHasher`, and has no external side
effects. Repeated calls on the same builder must not share mutable hash state.

```rust
use core::hash::{BuildHasher, Hasher};
use rustc_hash::FxBuildHasher;

let builder = FxBuildHasher::default();
let mut h = builder.build_hasher();
h.write_u64(7);
let value = h.finish();
```

### `rustc_hash::FxHashMap<K, V>`

With the `std` feature, the root export is exactly the following alias shape:

```rust
pub type FxHashMap<K, V> =
    std::collections::HashMap<K, V, FxBuildHasher>;
```

It has ordinary `HashMap` key/value behavior, including the key bounds and
mutation methods supplied by the standard collection. Use it for insertion,
replacement, lookup, removal, length, and iteration; the alias itself does not
add serialization, ordering, or persistence.

```rust
use rustc_hash::FxHashMap;

let mut map: FxHashMap<&str, u32> = FxHashMap::default();
map.insert("retries", 2);
assert_eq!(map.get("retries"), Some(&2));
map.insert("retries", 3);
assert_eq!(map.remove("retries"), Some(3));
```

An absent key returns the standard `None` result and does not mutate the map:

```rust
use rustc_hash::FxHashMap;

let map: FxHashMap<u8, u8> = FxHashMap::default();
assert_eq!(map.get(&99), None);
assert_eq!(map.len(), 0);
```

Iteration uses standard `HashMap` semantics and is not a sorted-order API.
Do not promise insertion order. The same map contents and hasher state should
remain repeatable under the same build and target, but callers must not treat
iteration order as a cross-platform serialization format.

### `rustc_hash::FxHashSet<V>`

With the `std` feature, the root export is exactly:

```rust
pub type FxHashSet<V> = std::collections::HashSet<V, FxBuildHasher>;
```

It retains ordinary `HashSet` semantics for insertion, membership, removal,
length, and iteration. Values must satisfy the standard collection's `Eq` and
`Hash` requirements. Duplicate insertion does not create a second logical
entry.

```rust
use rustc_hash::FxHashSet;

let mut seen: FxHashSet<&str> = FxHashSet::default();
assert!(seen.insert("ready"));
assert!(!seen.insert("ready"));
assert!(seen.contains("ready"));
assert!(seen.remove("ready"));
```

An empty set has length zero and membership checks return false. Iteration is
not a sorted-order contract and must not be used to infer insertion order.

### `rustc_hash::FxSeededState`

`FxSeededState` is a public clonable builder with a private `usize` seed:

```rust
#[derive(Clone)]
pub struct FxSeededState { /* opaque seed */ }
impl FxSeededState {
    pub const fn with_seed(seed: usize) -> Self;
}
impl BuildHasher for FxSeededState {
    type Hasher = FxHasher;
    fn build_hasher(&self) -> FxHasher;
}
```

`with_seed` accepts every `usize`, including zero and `usize::MAX`. It returns
an independent state and has no external side effects. `build_hasher` creates
a fresh `FxHasher` initialized from the retained seed. Cloning a state
preserves its future hash behavior; equal seeds produce equal hash observations
for equal input sequences.

```rust
use core::hash::{BuildHasher, Hasher};
use rustc_hash::FxSeededState;

let state = FxSeededState::with_seed(17);
let mut h = state.build_hasher();
h.write(b"stable");
let value = h.finish();
```

The edge case of a maximum seed is still a valid constructor input:

```rust
use core::hash::BuildHasher;
use rustc_hash::FxSeededState;

let state = FxSeededState::with_seed(usize::MAX);
let _hasher = state.build_hasher();
```

### Seeded Collection Aliases

When `std` is enabled, export these exact aliases:

```rust
pub type FxHashMapSeed<K, V> =
    std::collections::HashMap<K, V, FxSeededState>;
pub type FxHashSetSeed<V> =
    std::collections::HashSet<V, FxSeededState>;
```

They have the standard map and set operations, but callers can choose the
builder explicitly with `with_hasher`:

```rust
use rustc_hash::{FxHashMapSeed, FxSeededState};

let mut map = FxHashMapSeed::with_hasher(FxSeededState::with_seed(9));
map.insert("mode", "offline");
assert_eq!(map.get("mode"), Some(&"offline"));
```

An empty seeded collection is valid, and two collections constructed with
equal states have equal hashing behavior for equal keys. These aliases do not
promise a sorted iteration order or an order-independent serialized format.

## Implementation Notes

Use `core::hash::{Hasher, BuildHasher}` for the trait implementations so the
base library remains usable without `std`. Apply `#[cfg(feature = "std")]`
only to the standard collection aliases and the `extern crate std` bridge that
they need. The default feature must enable those aliases; disabling default
features must still compile the hasher, builder, and seeded-state APIs as a
library.

Keep the public crate root discoverable. `lib.rs` must connect
`seeded_state.rs` and re-export the seeded state and aliases from
`rustc_hash`, rather than requiring callers to import a private module.

Hashing must be deterministic for a fixed target pointer width, initial seed,
input sequence, and toolchain. Preserve wrapping behavior for arithmetic and
the platform-sized nature of `usize`; do not replace the behavior with a
randomized standard hasher, a text encoding, or a cryptographic digest.

Hasher state is mutable only through `&mut self` trait methods. `finish` is a
read-only observation and must not reset or mutate state. `BuildHasher` methods
must return independent hasher values so a map or set cannot accidentally
share state between operations.

The ordinary standard collection contract remains in force: map keys and set
values are hashed and compared according to their standard trait bounds,
duplicate map keys replace their values, duplicate set values remain one
logical entry, absent lookups return `None`, and removal reports whether an
entry existed.

Run these small checks while implementing, without embedding their expected
hash constants into public documentation:

```rust
let mut a = rustc_hash::FxHasher::default();
let mut b = rustc_hash::FxHasher::default();
use core::hash::Hasher;
a.write(b"same");
b.write(b"same");
assert_eq!(a.finish(), b.finish());
```

```rust
use core::hash::{BuildHasher, Hasher};
let x = rustc_hash::FxSeededState::with_seed(1).build_hasher();
let y = rustc_hash::FxSeededState::with_seed(1).build_hasher();
assert_eq!(x.finish(), y.finish());
```

```rust
use rustc_hash::{FxHashMap, FxHashSet};
let mut map = FxHashMap::default();
map.insert("key", 1);
assert_eq!(map.get("key"), Some(&1));
let mut set = FxHashSet::default();
assert!(set.insert("key"));
assert!(set.contains("key"));
```

```rust
use core::hash::Hasher;
let mut h = rustc_hash::FxHasher::with_seed(0);
h.write(&[]);
let _ = h.finish();
```

Before completion, run `cargo check --locked --offline` with default features,
run `cargo check --locked --offline --no-default-features`, and run the library
tests if available. Both checks must work without fetching a registry package.
Do not add private tests, hidden-checker references, verifier paths, artifact
identifiers, or implementation source copied from the upstream project.

Not confidently bindable for this task: the optional `rand` feature and its
random-state exports, nightly-only `Hasher` extension methods, any command
line interface, and any internal helper function not exported from the crate
root. They should remain outside the required implementation surface.
