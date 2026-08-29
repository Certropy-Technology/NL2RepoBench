# `importlib-metadata` Authoring Audit

Status: **controls-passed; awaiting integrator review and model Agent Run**.

## Frozen Source

- distribution: `importlib_metadata`
- import package: `importlib_metadata`
- upstream: `https://github.com/python/importlib_metadata`
- revision: `9757b400ee412ddb1d685f139ed3300f607c059a`
- commit tree: `f8ae23f8f977a1cac10eb0c421ec1c2057fcb91f`
- commit date: `2026-07-15T21:36:07-04:00`
- commit subject: `Add a benchmark for import time of importlib_metadata.`
- source archive: unprefixed `git archive --format=tar HEAD`
- archive bytes: 225,280
- archive members: 71
- archive SHA-256:
  `921c3509959fd9a207da52966da0d4fb2da167e51a9b7a4abb8eff4f46abbf39`
- submodules: none
- license: Apache-2.0 as declared by `pyproject.toml`

The revision is 28 commits after `v8.9.0`; setuptools-scm 10.2.1 computes
`8.9.1.dev28+g9757b400e`. The direct git archive excludes Git metadata, so the
task sets the equivalent documented setuptools-scm pretend-version environment
for candidate builds and verifies the resulting distribution version.

## Runtime Inventory

The runtime has 12 Python modules, 2,081 physical lines, 1,636 nonblank lines,
and 1,600 nonblank noncomment lines. It is pure Python and declares one runtime
dependency, `zipp>=3.20`.

The public root exports 15 names covering distribution discovery, metadata,
entry points, file records, requirements, package-to-distribution mapping, and
the `PackageMetadata` and `SimplePath` provider protocols. The behavior is
filesystem-backed and includes ordinary directories, `.egg` layouts, and zip
archives. No runtime network or subprocess operation was found.

## Upstream Tests

The upstream suite contains doctests plus tests for modern and legacy metadata,
discovery, entry points, zip paths, cache invalidation, file records, and
integration with Python finders. The host and the pinned slim image omit the
stdlib `test` package, so initial collection failed in seven modules before any
test ran. This was remediated for authoring only with `Lib/test` from exact
CPython tag `v3.12.11`, commit
`55fee9cf216abe4ec0d1139f94b1930fbd0c7644`.

With that authoring-only support path and the source's test dependencies:

```text
CPython:             3.12.11
pytest:              9.1.1
collected:           126
passed:              126
unittest subtests:   41 passed
exit code:           0
duration:            52.94 seconds
node-list SHA-256:   aad7756ed89b2f349e212c8f5ffa23ee3e27473c02f59992b0ffeb6360226d73
```

The production verifier does not ship upstream tests or CPython test-support
bytes. It uses an independently authored 30-leaf public-behavior scenario
contract under the mandatory unprivileged candidate subprocess boundary.

## Environment and Dependency Closure

The task uses the Python toolchain's digest-pinned CPython 3.12 slim image:

```text
python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a
linux/amd64 image ID:
sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a
```

The candidate build/runtime closure is a private hash-locked requirements
artifact with six packages:

```text
coherent-licensed==0.5.2
packaging==26.3
setuptools==84.0.0
setuptools-scm==10.2.1
vcs-versioning==2.3.1
zipp==4.1.0
```

The lock has 12 SHA-256 hashes, is 1,628 bytes, and has digest
`4ba29e58b3d26914ccd51cd4449fadd1a0d114b3392860bc6328f09155d0b3cf`.
A clean CPython 3.12 environment installed this closure with hash checking,
then built and installed the verified git archive under `PIP_NO_INDEX=1`,
`--no-deps`, and `--no-build-isolation`. The smoke result reported the frozen
version and `zipp 4.1.0` with exit code zero. No wheelhouse is used.

The first Harbor Oracle exposed one additional offline build requirement:
`coherent-licensed` normally downloads license text while preparing metadata.
Its pinned implementation has no offline mode but skips resolution when a
license file already exists. The trusted Oracle bundle therefore includes the
canonical SPDX Apache-2.0 text (10,280 bytes, SHA-256
`074e6e32c86a4c0ef8b3ed25b721ca23aca83df277cd88106ef7177c354615ff`).
Only after the upstream archive digest is verified does `solve.sh` verify and
install that license into the workspace. The model receives neither the Oracle
bundle nor any source-host authorization; an implementation must provide its
own declared license file or otherwise use an offline-capable build layout.

## Verifier Boundary and Traceability

The private `custom-json-v1` entrypoint calls
`nl2repobench.verification.candidate_client.execute_script`. Each scenario runs
as UID 10001 in a fresh bounded child process; only that child imports candidate
code. Trusted collection, JUnit, grading, reward, and network reports remain
root-owned.

The 30 leaves trace to the public specification as follows:

| Contract group | Leaves | Public behavior |
| --- | ---: | --- |
| package and errors | 2 | exports, frozen version, runtime requirement, missing-package error |
| entry points | 7 | parsing, invalid values, load, value semantics, selection, matching, global filtering |
| metadata | 7 | core fields, JSON projection, requirements, entry-point files, file records, origin, absent metadata |
| discovery | 7 | normalized names, exact matching, context, versionless egg-info, string paths, invalidation, abstract provider |
| package mapping | 2 | declared and inferred top-level package ownership |
| legacy requirements | 1 | extras and environment-marker conversion |
| zip discovery | 2 | zip metadata/files and case-insensitive normalized lookup |
| provider contract | 2 | context behavior and distribution construction |

Every hidden behavior is stated in `instruction.md`. Every core instruction
group is exercised by at least one leaf. The scenario adapter was run directly
against the frozen reference build before bundling: 30/30 matched.

## Network and Oracle

Agent and verifier execution are `no-network`. The model agent receives no
source or registry host. Only the trusted Oracle receives the exact
`github.com` source-host override; its uploaded solution fetches the full
revision, checks the resolved commit, recreates the unprefixed archive, and
strictly verifies the frozen SHA-256 before restoring `/workspace`.

## Final Gate Results

The final production compile used the source after all traceability and control
files were added. Its bundle is schema `1.0`, mode `production`, with 61
manifest files, bundle manifest SHA-256
`99f9cc1ee1056b7db861ce112f39ee4aa4d406e727989b46c6715bb3baeca2ac`, and
canonical manifest digest
`sha256:7bd7d7f45dc946cfabf8b7df8f45a91a61f08595c6e21c2922ab3c774b025761`.
Independent per-file verification found zero integrity errors.

Harbor `0.21.0` final2 Oracle passed 30/30 with reward `1.0`, valid `true`,
and no collection errors. Empty, stub, forgery, install timeout, workspace
symlink rejection, and call timeout controls all exited zero with valid
verifier-owned zero-score results. The forgery control collected all 30 leaves
and remained at reward `0.0` despite attempting to write trusted reports.
The explicit Docker `--network none` verifier replay exited zero and recorded
both `pypi.org:443` and `1.1.1.1:443` as unavailable.

Canonical receipts and hashes are recorded in `production-evidence.json`.
Review, publication, and model Agent Run are outside this worker's authority.
