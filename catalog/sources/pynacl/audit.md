# PyNaCl Authoring Audit

## Freeze

- Upstream: `https://github.com/pyca/pynacl`
- Revision: `fddb5f3a012baa28d5ead6497ab2ae72c4221246`
- Git tree: `871a1524d614a7feedc9165e624d52ef17ba26ec`
- Git archive: 38,676,480 bytes,
  `sha256:eec62a1ac27fd9cbe0452b5b7f12f2c1ca4f568c63b3b0b565a4ca0d3c7ac958`
- Package: PyNaCl 1.6.2, Python `>=3.8`
- License: Apache-2.0; `LICENSE` sha256
  `d3174ad63e721d4c9dccb8ad4320848992d314369bc46319720b5802c9153fe9`.
  Bundled libsodium license sha256
  `508a76d186356c0dd807a670ef510964f8724557024796a2c426c6c0e19ab683`.
- Submodules: none.

## Environment Remediation

The slim Python image lacks a compiler and make. The production environment
therefore pins Debian 13 `build-essential=12.12` and
`git=1:2.47.3-0+deb13u1`. The native build uses the source archive's bundled
libsodium and does not need a registry or system libsodium at run time.

The first offline baseline failed before candidate build because the initial
lock omitted PEP 517 build requirements. The corrected closure explicitly pins
setuptools and wheel in addition to CFFI and its transitive dependencies. This
is remediation evidence, not a source or model failure.

## Baseline

On `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
(Python 3.12.14, GCC 14.2.0, GNU Make 4.4.1), the frozen source built a native
`nacl/_sodium.abi3.so`. In a network-none container, pytest collected 4,671
tests and completed with 4,661 passed, 10 intentional skips, and zero failures.

The Git archive contains one relative symlink,
`licenses/LICENSE.libsodium.txt -> ../src/libsodium/LICENSE`. After verifying
the immutable archive digest, the Oracle replaces that link with a regular copy
of the same in-tree bytes (sha256 `508a76d1...ab683`) and asserts that no links
remain. This preserves package metadata while satisfying bounded workspace
ingestion.

## Verifier Boundary

The selected high-level API is exercised through 49 independent child-side
scenarios. Keys, boxes, native hash state, random generation, and password hash
objects never cross into trusted Python. The adapter emits only bounded JSON.
Each child has address-space, CPU, file, process, and descriptor limits; the
root runner enforces a 5-second per-call limit, a 60-second cumulative budget,
process-group termination, and UID cleanup. Expected vectors are frozen from
the reference implementation and are private.

Low-level bindings and secretstream state handles are deliberately excluded:
testing their CFFI pointers in trusted pytest would violate the verifier
boundary. Their core native functionality is still transitively exercised by
the documented high-level cryptographic objects.

## Network

Build-time pip access is limited to the compiler's fixed package index and
hash-locked closure. Agent and verifier run with no network. The model Agent
receives no source host. Only a trusted Oracle run may receive the exact
`github.com` source-host override, and its solution verifies both commit and
archive digest before restoring `/workspace`.
