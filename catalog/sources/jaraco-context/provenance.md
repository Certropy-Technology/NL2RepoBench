# Source Freeze And Remediation

## Frozen source

- Upstream: `https://github.com/jaraco/jaraco.context`
- Revision: `bfcb95c784e110521fa907e890b2eea34b0ef349`
- Commit: merge of the jaraco skeleton update, dated 2026-05-03T19:31:28-04:00.
- Commit tree: `d47521686d049a7aa36dbcbd42b4d594bf81b47a`
- Unprefixed `git archive --format=tar <revision>`: 61,440 bytes.
- Archive SHA-256: `e228a0721648643e4d7663fc71b03cfa533d60f508fa476fcd197d41a3804328`.
- Submodules: none.
- Implementation: one `jaraco/context/__init__.py`, 422 physical lines.

The revision is six commits after the signed `v6.1.2` tag and is reachable from
that tag. The Oracle bundle restores the exact archive and pins the distribution
version to `6.1.2` because an archive has no `.git` metadata for setuptools-scm.

## License and metadata

The frozen `pyproject.toml` declares MIT and the package has no separately named
license file at this revision. The SPDX value is therefore taken from the
explicit project metadata, not guessed from a classifier.

The build-system closure is `setuptools==84.0.0`,
`setuptools-scm==10.2.1`, `coherent-licensed==0.5.2`,
`vcs-versioning==2.3.1`, and `packaging==26.3`, all recorded with SHA-256
hashes in the private requirements artifact. On Python 3.12 the conditional
`backports.tarfile` runtime dependency is not selected.

## Test contract

The upstream `tests/test_safety.py` contains one parametrized test and depends
on optional `portend`/fixture support from the upstream conftest. A clean
collection probe failed with `ModuleNotFoundError: portend`; installing that
optional test stack would also test network fixtures outside this task's
runtime contract. The private verifier instead freezes 23 deterministic leaves:
API exports and signatures, directory and temporary context cleanup, composition,
exception capture/decorators, suppression and interrupt handling, tar path
stripping/safety/cleanup, and the repository clone command contract. Every leaf
imports the candidate only in a UID-isolated child process.

## Environment and security

The compiled agent image is based on
`python:3.12.14-slim-bookworm@sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579`.
Agent and verifier phases are `no-network` with empty static host allowlists.
The Oracle source host exception is run-scoped and is not task metadata or an
agent permission. The verifier owns collection, JUnit, grading, reward, and
network receipts; candidate code cannot write trusted reports.
