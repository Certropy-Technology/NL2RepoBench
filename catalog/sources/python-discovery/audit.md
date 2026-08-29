# python-discovery authoring audit

## Freeze

- Upstream: `https://github.com/tox-dev/python-discovery`
- Revision: `0ef757b00a6f859529193eec31667f0ccc8b833b`
- License: MIT, from the upstream `LICENSE` bytes
- Raw `git archive --format=tar` SHA-256: `6feb569ab3927bf2a958b4b02a667916e577b7e8565a609d9472c93072edb272`
- CPython 3.12.11, uv 0.11.32, Linux amd64/glibc

## Inventory and scope

The frozen tree contains 60 tracked files, 2,985 lines in the Python package,
14 Python test files, 305 named test functions, and 577 collected upstream
tests on the Linux baseline. The baseline completed with 562 passed and 15
skipped. Windows registry tests and platform-specific mock branches are not a
portable model-run denominator.

The production verifier uses 32 deterministic custom-json-v1 leaves. It covers
root/module exports, ISA normalization, version ordering and parsing, operators
and sets, PythonSpec parsing/matching, PythonInfo collection and round trips,
disk and no-op caches, cache key and lock semantics, PATH enumeration,
executable filename matching, explicit discovery, ordered fallback, predicates,
and deduplication. All candidate code
is imported only in UID 10001 child processes through the verifier runtime.

## Remediation

The upstream revision has no committed `uv.lock` and uses a VCS-derived dynamic
version. A task-local hash lock was generated for the complete Hatchling,
hatch-vcs, setuptools-scm, filelock, packaging, pathspec, pluggy,
trove-classifiers, and vcs-versioning closure. The Oracle uses a fixed commit,
asserts the resolved commit, verifies the raw archive digest, and only then
extracts the source into `/workspace`. Candidate and verifier runs use
`no-network`; build-time dependency installation is the only package-index
access.

Windows registry integration, mutable uv installations, and live remote
discovery were excluded because they cannot be made deterministic in the
Linux no-network Agent run without changing the package's core contract.
