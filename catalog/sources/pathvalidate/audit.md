# pathvalidate Authoring Audit

## Frozen source

- Upstream: `https://github.com/thombashi/pathvalidate`
- Revision: `1ca0a50fce51d5b5bd633457a72abf74dbe3112d`
- Tree: `e10122e6e9d9b1f265bd46315a87cfb91db5b50b`
- Commit time: `2026-05-10T19:35:32+09:00`
- Commit subject: `Update tips.rst to clarify handling of dot directory entries: #68`
- Source form: `git archive --format=tar --prefix=pathvalidate/ HEAD`
- Archive bytes: `389120`
- Archive SHA-256: `4c83bac3feec196a0a9925d5be61bbe9581310cff4f09b6372e203ba13b81918`
- Submodules: none
- License: MIT, `LICENSE` SHA-256
  `130a35b917df1951aefbf366120491d5124045a87ded123f20ded21521f4e3a2`
- Public module version: `3.3.1`

The source-freeze acquisition ran only through the task-local Oracle solution
path. It initialized an empty repository, fetched the exact 40-character SHA,
asserted `HEAD`, and generated the archive used by both evidence and the final
Oracle digest check.

## Upstream baseline

Runtime: CPython 3.12.11, Linux x86_64, glibc 2.43. Authoring environment
resolved `pytest==9.1.1`, `allpairspy==2.5.1`, `click==8.5.0`,
`Faker==40.37.0`, and `pytest-md-report==0.8.0` with their transitive test
dependencies.

```text
pytest --collect-only -q: 4184 collected, exit 0
pytest -q -p no:md_report: 4170 passed, 14 skipped, exit 0
```

The 14 skipped cases are upstream platform-dependent cases. The Harbor contract
does not reuse this raw collection as its denominator. It projects documented,
JSON-safe behavior into 54 fixed leaves so every candidate call is made through
the UID-separated child boundary.

Upstream test modules and principal coverage:

| Module | Test functions | Coverage |
| --- | ---: | --- |
| `test_argparse.py` | 8 | argparse validate/sanitize adapters |
| `test_click.py` | 4 | Click callbacks and `BadParameter` |
| `test_common.py` | 3 | platform and common character helpers |
| `test_error.py` | 3 | reason codes, strings, structured logging |
| `test_filename.py` | 37 | platform rules, lengths, reserved names, handlers |
| `test_filepath.py` | 46 | absolute paths, components, normalization, lengths |
| `test_handler.py` | 6 | null and reserved-name handlers |
| `test_ltsv.py` | 5 | LTSV label validation/sanitization |
| `test_symbol.py` | 10 | symbol replacement and validation |

## API inventory

The top-level package exports metadata, abstract validator/sanitizer bases,
`Platform`, character constants/common helpers, filename and filepath classes
and convenience functions, LTSV/symbol helpers, `ErrorReason`, and the public
validation error hierarchy. `pathvalidate.handler`, `pathvalidate.argparse`,
and `pathvalidate.click` add handlers and framework adapters. Exact signatures,
input domains, return categories, exceptions, ordering, platform determinism,
and examples are recorded in `instruction.md`.

Excluded from the scored surface:

- private helpers and undocumented private constants;
- filesystem existence, permissions, normalization beyond lexical behavior, or
  OS-specific maximum discovery;
- the wall-clock value returned by the timestamp handler;
- docs, release commands, examples, static typing, and upstream plugin output;
- performance, concurrency, and cross-version behavior.

## Dependency and environment closure

The package has no mandatory third-party runtime dependency. The hash-locked
build/optional-adapter closure contains exactly:

```text
click==8.5.0
packaging==26.3
setuptools==84.0.0
setuptools-scm==10.2.1
vcs-versioning==2.3.1
wheel==0.48.0
```

Every requirement has SHA-256 hashes. The lock is installed from PyPI only at
Docker build time. Agent and verifier phases are no-network. No wheelhouse,
vendored wheel, `--no-index`, or runtime package installation is used.

The upstream build derives distribution metadata from Git. The verifier passes
`SETUPTOOLS_SCM_PRETEND_VERSION=3.3.1` into the bounded candidate build so the
frozen shallow Oracle checkout and from-scratch candidate implementations have
the same deterministic version contract.

Environment identity:

- CPython: 3.12.14 in the digest-pinned `python:3.12-slim` verifier image
- OS: Debian 12, `linux/amd64`
- Base digest: `sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
- System packages: `git`, `ca-certificates`
- Candidate install: `pip --target --no-deps --no-build-isolation`
- Agent policy: no-network, no static allowed hosts
- Separate verifier policy: `network_mode: none` plus active public and numeric
  IP probes

## Verifier boundary and traceability

Protocol: `custom-json-v1`. The private entrypoint defines 54 unique leaves.
Each leaf sends a trusted scenario to
`nl2repobench.verification.candidate_client.execute_script`, which starts a
fresh process as UID/GID 10001. Only that process appends the candidate site and
imports candidate code. The root entrypoint receives bounded JSON observations
and emits only `passed`/`failed` leaf records.

Traceability groups:

| Public contract | Leaf IDs |
| --- | --- |
| Export/metadata/signatures | `api-surface`, `module-metadata`, `core-signatures` |
| Platform/common helpers | `platform-enum` through `path-type-validation` |
| Filename sanitization | `sanitize-filename-universal` through `sanitize-filename-null-handlers` |
| Filename validation/classes | `validate-filename-valid` through `filename-sanitizer-properties` |
| Filepath sanitization | `sanitize-filepath-universal` through `sanitize-filepath-null` |
| Filepath validation/classes | `validate-filepath-valid` through `filepath-sanitizer-properties` |
| LTSV/symbol helpers | `ltsv-labels` through `validate-symbol` |
| Errors/handlers | `error-reason-metadata` through `reserved-name-handlers` |
| Framework adapters | `argparse-adapters-success` through `click-adapters-errors` |
| Deprecated compatibility | `deprecated-check-reserved-flag` |

The reverse mapping appears in `instruction.md`: every leaf ID belongs to a
documented signature and behavior section. No leaf requires an undocumented
private function.

## Controls

Compiler-generated control bundles use source-local scripts:

- `stub`: installable package with metadata and shallow identity behavior;
- `forgery`: the same shallow behavior plus attempts to overwrite verifier
  reward, grading, and private entrypoint paths;
- `install-hang`: bounded sleeping PEP 517 backend;
- `call-hang`: import-time sleep in candidate code;
- `workspace-invalid`: symlink to `/etc/passwd` for ingestion rejection.

Empty workspace and offline behavior use the canonical bundle directly. Final
Harbor receipt paths, hashes, scores, validity, and network outcomes are written
to `production-evidence.json` only after the runs complete.
