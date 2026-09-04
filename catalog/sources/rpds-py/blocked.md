# Build `rpds-py`

This candidate is recorded as blocked pending a production Rust/PyO3 Harbor lane.
The assigned upstream revision is a native extension and has no Python fallback.
No candidate, verifier, Oracle, or control runtime is claimed for this source.

## Project Description

`rpds-py` provides Python bindings to Rust persistent data structures. The public
module exposes immutable `HashTrieMap`, `HashTrieSet`, `List`, `Stack`, and `Queue`
objects with structural sharing and Python iteration, comparison, hashing, pickle,
and mapping/sequence behavior.

## Supports

The intended task would target CPython 3.12 and an installable distribution named
`rpds-py` from the assigned commit. It requires a Rust toolchain, maturin, PyO3,
the frozen Cargo registry closure, and a separate child-process verifier. Runtime
and evaluation must use `network_mode=no-network` with all source, dependency,
test, verifier, and Oracle payloads injected before execution.

## API Usage Guide

The intended public imports are `from rpds import HashTrieMap, HashTrieSet, List,
Stack, Queue`. `HashTrieMap` accepts a mapping or iterable of key/value pairs and
returns new maps from `insert`, `remove`, `discard`, `update`, `convert`, and
`fromkeys`; it supports mapping access, iteration, views, equality, hashing, and
set-like key/item view operations. `HashTrieSet` accepts an iterable and returns
new sets from `insert`, `remove`, `discard`, `update`, `union`, `intersection`,
`difference`, and `symmetric_difference`.

`List` is an immutable iterable constructed from one iterable or positional
elements. Its `first`, `rest`, `push_front`, and `drop_first` operations return
persistent values and raise `IndexError` where the source contract requires it.
`Stack` is LIFO with `peek`, `pop`, and `push`; `Queue` is FIFO with `peek`,
`dequeue`, `enqueue`, and `is_empty`. All persistent operations preserve the
original value and produce deterministic equality, iteration, representation,
hashing, and pickle behavior.

## Implementation Notes

This source remains blocked until the compiler can inject a private, digest-bound
Cargo vendor closure and native Oracle payload without placing native wheels in
the public Python projection. The evidence directory records the immutable source,
license, exact Cargo graph, native build, and upstream test results. Do not weaken
the contract to a standard-library imitation or claim Harbor receipts from the
authoring probe.
