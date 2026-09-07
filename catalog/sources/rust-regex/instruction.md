# Regex Rust Pattern-Matching Library - Complete Documentation

> Status: this task is recorded as `blocked` in `task.toml`. The public
> contract below is preserved as authoring truth so that, once the shared
> Rust/Cargo runtime gains a reference-only closure (so the upstream engine is
> never handed to the candidate) and a candidate-safe way to supply generated
> Unicode tables, this instruction can be frozen, compiled and gated. Until then
> no Harbor runtime exists and no production validity is claimed.

## Introduction and Goals of the Regex Project

Regex is Rust's standard regular-expression library. It compiles a pattern into
a matcher and exposes searching, capture groups, iterators over successive
matches, and replacement. Matching is guaranteed linear time (Thompson NFA /
DFA), so pathological backtracking is not observable through the public API, and
Unicode-aware classes are deterministic for a fixed data version. The `Regex`
type is immutable and `Sync`, so it can be shared across threads after
compilation.

## Natural Language Instruction (Prompt)

Please create a Rust library package named `regex` from an empty workspace.
Implement the public pattern-matching API described here:

1. Create a complete Cargo library with `Cargo.toml`, `Cargo.lock`, and
   `src/lib.rs`; the crate root must connect the implementation and re-export
   `Regex`, `RegexBuilder`, `Captures`, `CaptureMatches`, `Matches`,
   `RegexSet`, and `Error`.
2. Implement `Regex::new` and `Regex::is_match`, `find`, `find_iter`,
   `captures`, `captures_iter`, `replace`, `replace_all`, `split`, and
   `captures_name`/`name` accessors for the documented syntax subset.
3. Implement the capture-group contract: `Captures::get`, indexing by number and
   name, `Captures::extract`, `Match::start`/`end`/`as_str`/`range`, and the
   leftmost-first match semantics that reproduce `PCRE`/Perl-like greedy and lazy
   repetition, alternation, anchors, character classes and repetitions.
4. Implement `RegexBuilder` toggles for `case_insensitive`, `multi_line`,
   `dot_matches_new_line`, `crlf`, `swap_greed`, `unicode`, and `size_limit`,
   matching the observable behaviour of the corresponding `(?flags)` constructs.
5. Implement `Regex::replace`/`replace_all` with `$name` and `${name}` group
   references, `$$` escapes, and expansion of a closure returning `Replacer`.
6. Support the default `std` feature and the documented `perf`, `unicode`, and
   `pattern` feature flags without runtime network access. The library must
   compile with `cargo check --locked --offline`.

Before the real engine, create the minimal crate skeleton and make
`cargo check --locked --offline` pass. Keep it compiling while adding the
`Regex`, capture, iterator, builder, set, and replacement API groups. Do not
copy upstream source or tests, add network clients, or expose hidden assertions.

## Environment Configuration

```text
rustc 1.97.1
Cargo edition 2021
Cargo runtime mode: --locked --offline
```

`std` is the default. The `unicode` feature enables Unicode-aware classes.
Matching must remain deterministic: no reliance on HashMap iteration order, wall
clock, randomised hash seed, or network at build/run time.

## Core File Requirements

```text
workspace/
├── Cargo.lock
├── Cargo.toml
└── src/
    └── lib.rs
```

`src/lib.rs` is the crate root: it declares the modules and re-exports every
public item above.

## Project Architecture

```text
src/
├── lib.rs        # crate root, re-exports, feature gates
├── regex.rs      # Regex + Regex::new, is_match, find, captures, replace, split
├── builder.rs    # RegexBuilder flag toggles
├── capture.rs    # Captures, CaptureMatches, Match, named groups
├── find_iter.rs  # Matches iterator
├── onepass.rs    # one-pass (no-capture) fast path
├── replace.rs    # Replacer, Cow-backing, $name expansion
└── set.rs        # RegexSet
```

## API Usage Guide

```rust
use regex::Regex;

let re = Regex::new(r"(?<x>\d+)-(?<y>\w+)").unwrap();
assert!(re.is_match("42-foo"));

let caps = re.captures("42-foo").unwrap();
assert_eq!(&caps["x"], "42");
assert_eq!(&caps["y"], "foo");

assert_eq!(re.replace("42-foo", "${y}-${x}"), "foo-42");
```

`Regex::new` returns `Result<Regex, Error>`; a parse failure yields a text-based
`Display` error. All byte offsets are on `char` boundaries; `find`/`captures`
return `Option<Match>`/`Option<Captures>`; iterators yield matches in leftmost
order. Out-of-range or non-existent capture indices return `None` rather than
panicking (indexing a missing group by name panics, matching upstream).

## Excluded From Scope

The `regex!` compile-time macro (proc-macro behaviour, not safely representable
offline), the unstable `__nonstandard`/`Internal` surface, and
`Regex::with_size_limit` internals are out of scope.
