# Regex Authoring Audit

Status: `controls-passed`; handoff status: `awaiting-agent-run`.

This task targets the exact upstream revision below. The source checkout and
all build probes were kept under the task-local authoring work directory; no
upstream source or private verifier bytes are copied into the public task
instruction.

## Source Freeze

- Upstream: `https://github.com/mrabarnett/mrab-regex`
- Revision: `1760a20647f1c2ddcc025128407fe6f7edb905a1`
- Commit tree: `cec04ae844e4f836186c59b8329a3c62d69bd436`
- Commit subject: `Support Python 3.15.`
- Git submodules: none
- Source archive: `git archive --format=tar <revision>` without a prefix
- Archive size: `3563520` bytes
- Archive SHA-256: `380b288264f32f0ea2d5da32cf06277c5dca37681c308b97433ddf22cb882434`
- License: `Apache-2.0 AND CNRI-Python`
- `LICENSE.txt`: 11584 bytes, SHA-256
  `bff55ef4cdcc8c14ce259f8e8ab60e264418440d6335f4dc138273fbd506144d`

The archive digest was repeated three times from the detached checkout. A
prefixed archive has a different digest and is not the value recorded in
`task.toml`.

## Package And Environment

- Distribution/import name: `regex`
- Upstream package version: `2026.8.12`
- Python requirement: `>=3.10`
- Runtime: CPython `3.12.14`, Linux `amd64`, Debian 12 slim
- Base image: `python:3.12.14-slim-bookworm@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
- System build dependency: `build-essential`
- Build backend: `setuptools.build_meta`, exact build dependency
  `setuptools==80.9.0`
- Runtime dependencies: none
- Run network policy: `no-network`; agent and verifier allowed-host lists are
  empty; reference source fetch is forbidden for model runs.

The package has 18 source-controlled files in the frozen archive. Its scored
surface exercises the Python parser/core and native `regex._regex` extension.
The source-only build completed with the expected compiler warning in the
upstream fuzzy-match path and no build error.

## API And Test Inventory

The public contract covers root exports and their `_main`/`_regex_core`
re-exports, compilation, match/search/fullmatch/prefixmatch, pattern and match
projections, replacement and split iterators, bytes/text separation, flags,
Unicode properties and graphemes, fuzzy matching, VERSION1 nested sets,
overlapped and reverse matching, partial matches, repeated captures,
branch-reset groups, named lists, caching, escaping, and error behavior.

The upstream source test module is `regex/tests/test_regex.py`; it contains a
`unittest.TestCase` suite with 101 collected tests. A clean source copy was
built and run under the task Python interpreter. The run reported
`Ran 101 tests` and `OK`; an earlier independent source-only run produced the
same result.

The production verifier uses a task-specific child-side adapter rather than
trusted pytest importing the candidate. It freezes 37 JSON-safe behavioral
leaves across packaging/exports, core matching, replacement/iteration,
Unicode and fuzzy features, bytes behavior, and error boundaries. Match
objects and callbacks are projected or reconstructed inside the untrusted
candidate process, so the verifier never shares candidate modules or trusted
report paths with the candidate.

## Build And Harbor Evidence

- `uv run nl2repo task validate-source catalog/sources/regex`: exit 0
- `uv run nl2repo task lint-network --tasks-root catalog/sources`: exit 0,
  error count 0; no finding for `regex` (the command reports pre-existing
  warnings for unrelated catalog sources)
- Production compile with `--allow-private`, toolchain lock, and local CAS:
  exit 0; fresh output is byte-identical to the prior compiled projection
- Compiled production bundle: 58 files; manifest SHA-256
  `b22ab1ceb9f751276a8c5bf30bc70da332abc65b76e354b8c64e31b6f0ace453`
- Canonical manifest digest in the bundle: `sha256:1c35703e25f258421b99430f54d95c37c245be7b1ba4a80159ad373ecec6f69a`
- Toolchain lock digest in the bundle: `sha256:230a7dd32d1de931a868d75901ea4f340882cf1aad24e61ee7918543075ab366`

The private CAS contains the 488-byte dependency lock, the 10240-byte
verifier bundle, and the 10240-byte Oracle bundle. Their declared digests are
verified before compilation. Oracle and controls receipts, including network
probes and bounded call-hang behavior, are referenced by
`production-evidence.json`.

## Residual Risk And Handoff

The task has not had a model Agent Run in this lane. The source is native and
hard, so the first model run should use the exact compiled runtime and record
any build or implementation failure as model/environment/infrastructure using
the Harbor result taxonomy. The upstream compiler warning is non-fatal and is
present in the frozen reference build. `catalog/tasks/regex/` is intentionally
absent here because generated runtime integration belongs to the parent
integrator.

