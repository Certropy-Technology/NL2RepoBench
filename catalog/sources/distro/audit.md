# `distro` Authoring Audit

Status: **controls-passed** for the bounded, deterministic Linux fixture and
CLI contract. No model Agent Run, blind review, pilot, or publication was
performed in this lane.

## Frozen Source

- Distribution/import package: `distro`.
- Upstream: `https://github.com/python-distro/distro`.
- Revision: `3fba7d3e19c84e5bb1f15c22b1a5a6db6e8f07c7`.
- Commit tree: `e6d4074546bcb2ad10d204d187bff023efe0fe05`.
- Parent: `1f02f414e655862e3efc0e12ecd06e89d3fbd503`.
- Subject: `Actions(deps): Bump actions/checkout from 5 to 7`.
- Unprefixed `git archive --format=tar REV` digest:
  `sha256:b4241c8e34dd1432b9870b56f9f1056eede939b3486d9f0434c7fc6a08c5c01f`.
- License: Apache-2.0, `LICENSE` SHA-256
  `sha256:cb5e8e7e5f4a3988e1063c142c60dc2df75605f4c46515e776e3aca6df976e14`.

The source contains `src/distro/distro.py`, package metadata, the module CLI,
and upstream tests/resources. The upstream pytest collection is 281 items.
The generated task intentionally uses a smaller fixed denominator because
many upstream tests execute against host-specific `/etc`, `uname`, and
`lsb_release` data. The Oracle solution removes only the upstream test tree
from the candidate workspace; it verifies the source archive before extraction
and pins metadata to `1.9.0` for source-only builds without `.git`.

## Inventory and Boundary

The stdlib AST inventory was written to `api-inventory.json` from the exact
detached checkout. It recorded 1,209 implementation non-comment LOC, 5
implementation Python files, 182 test definitions, 2 test files, 254 public
symbols, and 67 import edges. Its risk flags were `dynamic-execution` and
`external-service`; the production boundary excludes uncontrolled host data by
using `LinuxDistribution(root_dir=..., include_lsb=False,
include_uname=False, include_oslevel=False)` with evaluator-created fixtures.

The 15 private scenario leaves cover package exports and version metadata,
quoted `os-release` parsing, ID normalization, pretty and best versions,
version parts, release-file fallback, root/subprocess guards, global
accessors, deprecated compatibility wrappers, CLI text and JSON, source
accessors, missing data, deterministic projections, and local-only behavior.
The child adapter is executed as UID `candidate`; the trusted parent does not
import candidate code.

## Reproducibility and Commands

Runtime is CPython 3.12.14 on Debian 12 amd64 with base image digest
`sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`.
Candidate build requirements are the private hash-locked setuptools 80.9.0
and wheel 0.45.1 lock, digest
`sha256:53615811dc1d1f22b94617262702e9d02d56d5d8a0a180227344c700fcddae60`.
The task and verifier use `no-network`; the source host is not allowed in an
Agent run.

Commands and observed exits:

```text
uv run nl2repo task validate-source catalog/sources/distro: exit 0
uv run nl2repo task lint-network --tasks-root catalog/sources: exit 0, 0 task errors
uv run nl2repo author scan-source .nl2repo/authoring-work/upstream: exit 0
python -m py_compile verifier and bash -n solution/controls: exit 0
uv run nl2repo harbor compile ... --allow-private: exit 0
Harbor 0.21.0 Oracle: exit 0, 15/15, reward 1.0
Harbor 0.21.0 empty: exit 0, installation exception, reward 0.0
Harbor 0.21.0 stub: exit 0, 0/15, reward 0.0
Harbor 0.21.0 forgery: exit 0, 0/15, verifier-owned reward 0.0
Harbor 0.21.0 call-hang: exit 0, 0/15, bounded child timeouts
Harbor 0.21.0 install-hang: exit 0, installation timeout, reward 0.0
```

## Residual Risks

- The denominator is a 15-leaf deterministic subset, not full upstream pytest
  parity.
- Host-specific live `lsb_release`, `uname`, and `/etc` behavior is documented
  but not scored; fixture roots are the reproducibility boundary.
- Independent spec review and downstream model-agent pilot remain pending.
