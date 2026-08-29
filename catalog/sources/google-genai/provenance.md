# google-genai Authoring Provenance

## Frozen source

- Upstream: `https://github.com/googleapis/python-genai`
- Revision: `66518c9104b15a89225ee255fe03d906c7e4cb35`
- Commit date: `2026-08-25T14:13:58-07:00`
- Commit subject: `chore(main): release 2.20.0 (#2884)`
- Distribution version: `2.20.0`
- `git archive --format=tar HEAD`: 685 members, 44,800,000 bytes,
  SHA-256 `3e7ba8998c9bf652f892ee871a28277e3dfb5bfb6a9a7cf6a2e7c29483a08f12`
- License: Apache-2.0; `LICENSE` blob
  `d645695673349e3947e8e5ae42332d0ac3164cd7`, 11,358 bytes, SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- Submodules: none.

The Oracle fetches only this revision, asserts `HEAD`, recreates the Git
archive, and rejects a digest mismatch before extracting into `/workspace`.
The exact `github.com` authorization is supplied only to the trusted Oracle.

## Inventory and adaptation

The revision contains 527 Python files, 164 `test_*.py` files, 1,327 statically
declared test functions, and 3,133 top-level public class/function declarations.
Its service/replay suite requires external replay configuration: a bounded full
collection found 1,318 tests plus 85 collection errors for missing
`GOOGLE_GENAI_REPLAYS_PATH`. A deterministic nine-file slice covering types,
transformers, client helpers, chat history, and errors passed 218 tests with 6
skips in 1.93 seconds.

The task therefore freezes a 40-leaf `custom-json-v1` adaptation of the
offline typed-content and local-state contract. It excludes credentials,
inference, uploads, live sessions, MCP, local tokenizers, and replay fixtures.
No failing assertion was removed to meet a score threshold.

## Environment and dependencies

The production toolchain pins Python 3.12.14 on Debian 13 and base image
`python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
The candidate closure contains 27 exact requirements and 543 SHA-256 artifact
hashes. Its lock is 48,729 bytes with SHA-256
`d2ef79f7a68c430c7193acf86f4044d3bad95d269206da01353071843036a7bf`.
Dependencies are installed at Docker build time; candidate and verifier phases
run without public network access.

## Verifier boundary

The private verifier bundle uses `custom-json-v1` and entrypoint `run.py`. The
trusted process imports no candidate code. It invokes eight bounded scenarios
through the generic UID-10001 `candidate_client.execute_script` boundary; only
those child processes import the candidate. The wrapper validates exactly 40
unique leaves, generates verifier-owned collection/JUnit/grading/reward files,
enforces cumulative time and output limits, and probes network isolation.

Local replay against the frozen source passed 40/40 before bundle generation.

## Production results

The production compiler completed repeatedly with the same 60-file inventory.
The recheck-final compile uses the current private verifier artifact and has
bundle manifest SHA-256
`sha256:01f0f4a6042b84277e3b22d0927e72e04859d15651bbc85c1fcf0e3021eadf78`
and canonical manifest digest
`sha256:98b249e525e76a91bf44c0608850fb2f89032046d605c0e3dc261e171287fabd`.
Its files have no missing or digest-mismatched entries, no undeclared files,
no Agent compose network override, and a separate verifier compose with
`network_mode: none`.

Harbor 0.21.0 and direct no-network controls produced:

```text
oracle             valid=true  40/40  reward=1.000
empty              valid=true    0/0  reward=0.000  candidate-installation-failed
stub               valid=true    3/40 reward=0.075
forgery            valid=true    0/40 reward=0.000  planted reward ignored
workspace-invalid  valid=true    0/0  reward=0.000  candidate-workspace-rejected
install-hang       valid=true    0/0  reward=0.000  install outcome=timeout, returncode=-9
call-hang          valid=true    0/40 reward=0.000  bounded in 69 seconds
offline replay     valid=true  40/40  reward=1.000
```

Every result's `network.json` reports `public_network_available=false` and
failed probes to both `pypi.org:443` and `1.1.1.1:443`. No model Agent Run was
started. Blind review, model pilot, dataset integration, and publication remain
outside this lane.
