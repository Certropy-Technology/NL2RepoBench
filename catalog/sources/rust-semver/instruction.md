# Semantic Versioning Library - Complete Documentation

## Introduction and Goals of the Semver Project

`semver` is a Rust library implementing Cargo's interpretation of Semantic
Versioning. It parses and displays versions, compares release and pre-release
identifiers, and evaluates version requirements such as `^1.2` or
`>=1.0.0, <2.0.0`. The goal is a complete, deterministic library package, not a
command-line imitation or a collection of hard-coded examples.

## Natural Language Instruction (Prompt)

Please create a Rust library package named `semver` from an empty workspace.
Implement the following public behaviour:

1. **Package and crate root**: provide `Cargo.toml`, `Cargo.lock`, and
   `src/lib.rs`; the crate root must declare internal modules and re-export the
   documented types, functions and traits.
2. **Version values**: implement `Version` with public `major`, `minor`, `patch`,
   `pre` and `build` fields, strict parsing, canonical `Display`, `Ord`,
   `PartialOrd`, `Eq`, `Hash`, `Clone`, `Debug`, `FromStr`, the const
   `Version::new`, and `Version::cmp_precedence`.
3. **Requirements**: implement `VersionReq` with a public `comparators` field,
   `VersionReq::parse`, `VersionReq::matches`, the `VersionReq::STAR`
   constant, and a `Default` equal to `STAR`.
4. **Comparators**: implement `Comparator` with public `op`, `major`, `minor`,
   `patch` and `pre` fields, `Comparator::parse`, `Comparator::matches` and
   `Display`, plus the `Op` enum.
5. **Identifiers**: implement `Prerelease` and `BuildMetadata` with `EMPTY`,
   `new`, `as_str`, `is_empty`, `Display`, ordering and validation.
6. **Errors**: implement a single `Error` type whose `Display` text matches the
   catalogue below.
7. **Offline completion**: first create a compilable crate skeleton, keep
   `cargo check --locked --offline` passing after each API group, and before
   finishing run it with default features and with `--no-default-features`.

Do not copy upstream source or tests. Do not add network clients, binaries,
build-time downloads, or generated files that depend on absolute paths. There
are no runtime dependencies.

## Environment Configuration

### Rust Version and Build Mode

```text
rustc 1.97.1
Cargo edition 2018
Cargo network mode: offline
Runtime dependencies: none
```

### Core File Requirements

Start from this working package shape:

```text
workspace/
├── Cargo.lock
├── Cargo.toml
└── src/
    └── lib.rs
```

`src/lib.rs` is the library crate root. A directory of disconnected parser or
module files without a crate root is incomplete. Run:

```bash
cargo check --locked --offline
cargo check --locked --offline --no-default-features
```

## Semver Project Architecture

Internal module names are your choice. The public boundary is a normal Cargo
library imported as `use semver::{...}`. The `std` feature is on by default;
with `--no-default-features` the crate must still compile as `no_std`. No
verifier file belongs in the candidate workspace.

## API Usage Guide

### Module Import

```rust
use semver::{BuildMetadata, Comparator, Error, Op, Prerelease, Version, VersionReq};
```

### Version

```rust
#[derive(Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub struct Version {
    pub major: u64,
    pub minor: u64,
    pub patch: u64,
    pub pre: Prerelease,
    pub build: BuildMetadata,
}

impl Version {
    pub const fn new(major: u64, minor: u64, patch: u64) -> Version;
    pub fn parse(text: &str) -> Result<Version, Error>;
    pub fn cmp_precedence(&self, other: &Version) -> core::cmp::Ordering;
}
```

`parse` accepts `major.minor.patch` with optional `-pre` and `+build`. All three
numeric parts are required, must be plain `u64` decimal with no leading zero, and
may not contain whitespace anywhere. Display always re-renders as
`major.minor.patch` plus `-pre` and `+build` when present.

`Version::parse("18446744073709551615.0.1")` succeeds; a larger major fails with
the overflow message below.

**Ordering.** `Ord` compares `major`, `minor`, `patch`, then `pre`, then `build`,
so build metadata **does** affect `Ord` and `Eq`. `cmp_precedence` implements the
SemVer precedence rule and **ignores** build metadata. Therefore:

```text
Version::parse("1.0.0").cmp(Version::parse("1.0.0+build"))        -> Less
Version::parse("1.0.0").cmp_precedence(Version::parse("1.0.0+build")) -> Equal
```

Precedence orders pre-releases before their release, compares dot-separated
segments, compares all-numeric segments numerically and other segments by ASCII
order, treats a shorter prefix as smaller, and always ranks a numeric segment
below a non-numeric one. The canonical chain is:
`1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta < 1.0.0-beta.2
< 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0`.

**Debug** renders exactly:

```text
Version { major: 1, minor: 2, patch: 3, pre: Prerelease("a"), build: BuildMetadata("b") }
```

### Version Requirements

```rust
#[derive(Clone, Eq, PartialEq, Hash, Debug)]
pub struct VersionReq { pub comparators: Vec<Comparator> }

impl VersionReq {
    pub const STAR: VersionReq;
    pub fn parse(text: &str) -> Result<VersionReq, Error>;
    pub fn matches(&self, version: &Version) -> bool;
}
```

`VersionReq::default()` equals `STAR`, and both `STAR` and `default()` contain an
**empty** `comparators` vector while still matching every stable version.

**Normalisation.** Requirement text is parsed into comparators, and `Display`
re-renders the normalised form. These mappings are contractual:

```text
"*"            -> "*"            (no comparators)
"1.2"          -> "^1.2"         (a bare partial version is a caret)
"1.2.3"        -> "^1.2.3"       (a bare full version is a caret)
"1.x" / "1.*"  -> "1.*"          (Op::Wildcard, minor and patch None)
"^1.2.3"       -> "^1.2.3"
"~1.2.3"       -> "~1.2.3"
">=1.0.0, <2.0.0" -> ">=1.0.0, <2.0.0"
"=1.2.3"       -> "=1.2.3"
">= 1.2.3"     -> ">=1.2.3"      (whitespace after the operator is dropped)
">=1.2.3+bld"  -> ">=1.2.3"      (build metadata is parsed then discarded)
```

`Comparator` exposes `op`, `major`, `minor: Option<u64>`, `patch: Option<u64>`
and `pre`. After normalisation the projection `op:major:minor:patch:pre` for the
inputs above is:

```text
"*"                 -> (no comparators, empty vector)
"1.2"               -> Caret:1:Some(2):None:
"1.x"               -> Wildcard:1:None:None:
"^1.2.3"            -> Caret:1:Some(2):Some(3):
"~1.2.3"            -> Tilde:1:Some(2):Some(3):
">=1.0.0, <2.0.0"   -> GreaterEq:1:Some(0):Some(0):,Less:2:Some(0):Some(0):
"=1.2.3"            -> Exact:1:Some(2):Some(3):
"1.2.3"             -> Caret:1:Some(2):Some(3):
```

`Op` is `#[non_exhaustive]`, derives `Copy, Clone, Eq, PartialEq, Hash, Debug`
and has the variants `Exact`, `Greater`, `GreaterEq`, `Less`, `LessEq`, `Tilde`,
`Caret`, `Wildcard`.

**Matching.** Operators behave as follows (`~1.2` accepts `1.9.9` but not
`2.0.0`; `~1` accepts `1.9.9` but not `2.0.0`):

```text
"^1.2.3"  accepts 1.2.3, 1.9.0; rejects 1.2.2, 2.0.0
"^0.2.3"  accepts 0.2.9; rejects 0.3.0
"^0.0.3"  rejects 0.0.4
"~1.2.3"  accepts 1.2.3, 1.2.9; rejects 1.3.0
"*"       accepts 0.0.0 and 99.0.0
"1.x"     accepts 1.9.9; rejects 2.0.0
"1.2.x"   accepts 1.2.9; rejects 1.3.0
"=1.2.3"  accepts 1.2.3; rejects 1.2.4
">1.2.3"  accepts 1.2.4; rejects 1.2.3
">=1.2.3" accepts 1.2.3
"<1.2.3"  accepts 1.2.2; rejects 1.2.3
"<=1.2.3" accepts 1.2.3
">=1.0.0, <2.0.0" accepts 1.5.0; rejects 2.0.0
">=1.0.0, <1.0.0" rejects 1.0.0        (intersection is empty)
```

**Pre-release rule.** A version carrying a pre-release tag matches a requirement
only when at least one comparator has the same `major.minor.patch` **and** a
non-empty pre-release:

```text
"^1.2.3"           rejects 1.2.3-alpha        (comparator has no pre-release)
"^1.2.3-alpha"     accepts  1.2.3-beta       (same triple, pre-release present)
"^1.2.3-alpha"     accepts  1.2.4            (stable version needs no gate)
">=1.0.0"          rejects 1.0.1-alpha
">=1.0.0-alpha"    rejects 1.0.1-beta        (different triple)
"*"                rejects 1.0.0-alpha
```

Build metadata never affects matching: `^1.2.3` accepts `1.2.3+build` and
`=1.2.3` accepts `1.2.3+meta`.

`Comparator::parse(text)?.matches(&version)` applies the same rules to a single
comparator, independently of `VersionReq`:

```text
">=1.2.3" accepts 1.2.4 and 1.2.3; "^1.2.3" rejects 1.2.3-alpha;
"^1.2.3-alpha" accepts 1.2.3-beta; "=1.2.3" accepts 1.2.3+meta;
"1.x" accepts 1.9.9 and rejects 2.0.0
```

### Prerelease and BuildMetadata

```rust
#[derive(Default, Clone, Eq, PartialEq, Hash, PartialOrd, Ord)]
pub struct Prerelease { /* opaque */ }

#[derive(Default, Clone, Eq, PartialEq, Hash, PartialOrd)]
pub struct BuildMetadata { /* opaque */ }

impl Prerelease {
    pub const EMPTY: Prerelease;
    pub fn new(text: &str) -> Result<Prerelease, Error>;
    pub fn as_str(&self) -> &str;
    pub fn is_empty(&self) -> bool;
}

impl BuildMetadata {
    pub const EMPTY: BuildMetadata;
    pub fn new(text: &str) -> Result<BuildMetadata, Error>;
    pub fn as_str(&self) -> &str;
    pub fn is_empty(&self) -> bool;
}
```

Both are dot-separated ASCII alphanumeric-or-hyphen identifiers, never an empty
segment. `Display` prints the stored text with no leading `-` or `+`, so both
`Prerelease::EMPTY` and `BuildMetadata::EMPTY` display as the empty string and
`is_empty()` is `true` only for them. `Prerelease` is totally ordered and
follows the same segment rule as versions; `BuildMetadata` is only partially
ordered and does not implement `Ord`.

**Leading zeros are asymmetric.** `Prerelease::new("00")` fails, while
`BuildMetadata::new("00")` succeeds and `1.0.0+build.007` parses: a numeric
pre-release segment may not have a leading zero, but a build-metadata segment
may. `1.0.0-00` is therefore rejected while `1.0.0-0` and `1.0.0-0a` are
accepted.

### Error Contract

`Error` implements `Debug`, `Display`, and — with the `std` feature —
`std::error::Error`. It is **not** `Clone`, `Eq` or `Hash`. `Debug` always wraps
the `Display` text, so `format!("{:?}", err)` equals
`format!("Error(\"{}\")", err)` for every error.

`Display` produces exactly one of these messages for the inputs shown:

```text
empty string, expected a semver version                 ("")
invalid leading zero in major version number            ("01.2.3")
invalid leading zero in minor version number            ("1.02.3")
invalid leading zero in patch version number            ("1.2.03")
invalid leading zero in pre-release identifier          ("1.0.0-00")
value of major version number exceeds u64::MAX          ("18446744073709551616.0.0")
unexpected end of input while parsing major version number  ("^")
unexpected end of input while parsing minor version number  ("1.2")
unexpected character 'v' while parsing major version number ("v1.2.3")
unexpected character ' ' while parsing major version number (" 1.2.3")
unexpected character 'x' while parsing minor version number ("1.x.3")
unexpected character ' ' while parsing minor version number ("1. 2.3")
unexpected character 'z' while parsing patch version number ("1.2.z")
unexpected character ' ' after patch version number     ("1.2.3 ")
unexpected character '.' after patch version number     ("1.2.3.4")
unexpected character '_' after pre-release identifier   ("1.2.3-al_pha")
unexpected character '_' after build metadata           ("1.0.0+build-1_x")
unexpected character in pre-release identifier          (Prerelease::new("bad_char"))
unexpected character in build metadata                  (BuildMetadata::new("bad_char"))
empty identifier segment in pre-release identifier      ("1.2.3-", "1.2.3-alpha..1")
empty identifier segment in build metadata              ("1.2.3+")
expected comma after patch version number, found '.'    ("1.2.3.4" as a requirement)
unexpected character after wildcard in version req      ("**")
```

Position-bearing messages name the component that failed. A requirement whose
operator is unknown, such as `=>1.2.3`, reports the character after the leading
`=`: `unexpected character '>' while parsing major version number`.

## Implementation Notes

Implement in stages: crate skeleton and public types first; strict version and
identifier parsing next; ordering and formatting next; then requirement parsing
and matching; finally the error catalogue and feature checks. Keep every input
path bounded and deterministic; reject malformed input rather than coercing it.

The verifier calls the candidate through a separate Rust adapter and keeps all
expected values in a distinct root-only checker, so hidden assertions are not
part of the candidate workspace. Do not add a candidate-side test server, do not
read verifier files, and do not attempt to influence grading output.
