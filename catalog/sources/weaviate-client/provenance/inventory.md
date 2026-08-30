# Frozen Source Inventory

- Upstream: `https://github.com/weaviate/weaviate-python-client`
- Revision: `9f59a367f09a433826fbb045065bfcc958ff69a5`
- Git description: `v4.23.0-26-g9f59a367`
- Package version from setuptools-scm: `4.23.1.dev26+g9f59a367f`
- Archive SHA-256: `4f8ef5b9b30a22a4503895fea6cc77fa7280d4fcf2378a92650abb0d75315152`
- Archive command: `git archive --format=tar --prefix=weaviate-client/ 9f59a367f09a433826fbb045065bfcc958ff69a5`
- Archive size: 5,539,840 bytes; tracked files: 701; submodules: none.
- License: BSD-3-Clause; `LICENSE` SHA-256:
  `02bd288ff6ef7ff7f970fa9c6ce56f253d71ecf4a713110e20200fa5f58c0680`.
- Build backend: `setuptools.build_meta`; build requirements are
  setuptools, setuptools-scm, and wheel.
- Runtime requirements: HTTPX, validators, Authlib, Pydantic, gRPC,
  Protobuf, and packaging within the ranges declared in `setup.cfg`.

The frozen `weaviate/` tree contains 376 Python files, 782 top-level class
definitions, 139 top-level synchronous functions, one top-level async
function, and 347 public-named class/function definitions across 51 modules.
The primary public namespaces are root connection helpers, authentication,
configuration, collections, query/filter builders, data/result models, RBAC,
users, backup, cluster, tokenization, and utilities.

The source-only `test/` unit tree collected 418 leaves across 24 files under
Python 3.12.13. With the declared pytest, pytest-asyncio, pytest-xdist, NumPy,
Pandas, and Polars development dependencies, the bounded baseline completed
with exit code 0 and reported `418 passed, 1 skipped, 30 warnings in 37.55s`.
The three timeout-supervisor tests fail only when the source-declared xdist
plugin is omitted and pass when it is installed.

Live `integration/`, `integration_embedded/`, `mock_tests/`, journey,
profiling, Docker-compose, cloud credential, and embedded binary download
surfaces are not part of the production denominator. The production verifier
uses a focused 94-leaf deterministic client-side contract and never starts or
contacts Weaviate.
