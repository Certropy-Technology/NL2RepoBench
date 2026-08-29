# `httptools` Authoring Audit

Status: **controls-passed for the Linux/amd64 production lane; review, pilot,
and publication remain pending**.

## Source Freeze

- Upstream: `https://github.com/MagicStack/httptools`
- Revision: `cf10ce6f0dae56e61817e67b9bb073dd39d0191a`
- Commit: `httptools 0.8.0`, 2026-05-25
- License: MIT, root `LICENSE`, 1,093 bytes, SHA-256
  `f4573e7cb7676745fb5b8d36fa548aa93e391cfb6872ddacd65130c45ea6a92d`
- Parent tree archive SHA-256: `88f141fd4aef5561143a7dd84828a639567e3bb67530ee5736b983fe20693cd1`
- Materialized submodules: `vendor/http-parser@2343fd6b5214b2ded2cdcf76de2bf60903bb90cd`
  and `vendor/llhttp@751e5b44dc07a9932d244cb06210cfdcae951115`.
- Recursive deterministic source snapshot used by the Oracle: 778,240 bytes,
  SHA-256 `cdeeab4b17c4352fc12ea4a907295688c2ce887f4a87c14ff1e4ec020df0f0c9`.
  It contains the parent tree and both exact submodule trees under `src/`.

The source tree has 29 parent tracked entries plus the materialized submodule
files. The package has two Cython extensions, no runtime PyPI dependency, and
uses setuptools with a Cython build requirement. `build-essential` is frozen
as the Linux build system package.

## Baseline and Test Inventory

The exact checkout was installed with uv 0.11.32 on CPython 3.12.11 using the
hash-locked build closure. The upstream test module contains 41 unittest test
methods and all 41 passed after the two submodules were initialized. The
retained baseline log is
`.nl2repo/authoring-work/python-author-wave2-20260828/httptools/logs/upstream-tests-installed.log`
(SHA-256 `a4d3d439564c6e1899895650d18f0b5bf4a456f9152eb900c21ee51ec9109e54`).
The upstream tests exercise request and response parsing, chunked data,
upgrades, callback failures, fragmented input, and URL parsing.

Production uses a separate-verifier `custom-json-v1` adapter with a frozen
20-leaf denominator. The adapter imports candidate code only in a UID-10001
child process and communicates JSON. The leaves cover package exports,
version, native extension loading, ordinary and fragmented requests, chunking,
input buffer types, request errors and callback wrapping, keep-alive state,
ordinary and upgrade responses, response errors and callback wrapping, URL
components/relative paths/input types/invalid inputs, and URL immutability.
This is a reviewed bounded contract rather than a claim of transparent full
upstream unittest parity. `traceability.md` maps every leaf to the public
contract and upstream behavior family.

## Environment and Dependency Contract

The candidate and verifier run on `python:3.12-slim@sha256:2c941e...63c4a`
for `linux/amd64`. Candidate build dependencies are installed during image
build from a private, hash-locked pip requirements artifact containing
`Cython==3.1.4`, `setuptools==80.9.0`, and `wheel==0.45.1`. No wheelhouse is
vendored and no runtime phase installs dependencies. Harbor Agent and verifier
network modes are `no-network`; the model Agent has no static allowed hosts.
Only the trusted Oracle receives a run-scoped authorization for the frozen
upstream host, though this task's Oracle uses a local digest-verified snapshot.
