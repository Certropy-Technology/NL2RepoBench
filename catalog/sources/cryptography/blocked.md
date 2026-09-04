# cryptography task status

## Project Description

`cryptography` provides high-level cryptographic recipes and low-level primitives backed by
Rust and OpenSSL. The assigned source revision is frozen, licensed under Apache-2.0 or
BSD-3-Clause, and known to build a native Python wheel.

## Supports

The production task is currently blocked. Agent, candidate, verifier, Oracle, and all controls
must execute with `network_mode=no-network`; runtime GitHub, PyPI, DNS, and other external
service access is forbidden.

## API Usage Guide

A publishable task would need to specify and test the public recipes, hashing, MAC, KDF,
symmetric and asymmetric primitives, serialization, X.509, OCSP, PKCS, SSH, and backend
contracts. These APIs exchange live key, certificate, cipher-context, and OpenSSL-backed
objects rather than a bounded JSON-only value model.

## Implementation Notes

Before authoring can continue, a reviewed task scope must define a faithful stateful child-side
protocol for the native object lifecycle. The complete hash-locked Python, Rust, OpenSSL, and
vector test closure must then be frozen and replayed in a no-network verifier. Until those
conditions are met, there is no valid fixed denominator, Oracle result, or control result.
