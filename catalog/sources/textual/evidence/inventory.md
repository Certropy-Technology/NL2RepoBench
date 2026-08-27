# Textual Authoring Inventory

## Frozen source

- Upstream: `https://github.com/Textualize/textual`
- Revision: `06dbeef4bb70fb718236aa418ed658ef4667a126`
- Package version: `8.2.8`
- License: MIT
- Python support used for the task: 3.12
- Source archive evidence: `.nl2repo/authoring-work/python-author-wide-20260826-r2/textual/freeze/git-archive.tar`
- Archive SHA-256: `sha256:481fcda705dcc2e3addded9d53b64c78232a7f46607621c9d0a33c4a6e0378b0`

The archive is the byte-reproducible output of `git archive --format=tar` for
the frozen revision. The trusted Oracle reconstructs and verifies this digest
before extracting the reference implementation.

The frozen checkout contains 247 Python package files, 252 test files, and 2,060
test-function declarations. The full upstream suite is not the task denominator:
it includes terminal rendering, snapshots, event loops, and optional integrations.

An isolated Python 3.12 environment with `pytest==8.4.1`,
`pytest-xdist==3.6.1`, and `pytest-textual-snapshot==1.0.0` collected 3,467
upstream tests without collection errors. The deterministic upstream files
`test_slug.py`, `test_case.py`, `test_wrap.py`, `test_validation.py`,
`test_color.py`, `test_geometry.py`, and `test_markup.py` passed 334/334.
Receipts are task-local at:

- `.nl2repo/authoring-work/python-author-wide-20260826-r2/textual/upstream-collect.log`
- `.nl2repo/authoring-work/python-author-wide-20260826-r2/textual/upstream-slice.log`

## Deterministic task slice

The private verifier contains 24 JSON-safe leaf cases covering the following
public behavior families:

| Family | Import paths | Cases |
| --- | --- | ---: |
| Slugs and identifiers | `textual._slug` | 5 |
| Naming | `textual.case` | 2 |
| Terminal cells | `textual._cells` | 3 |
| Wrapping | `textual._wrap` | 2 |
| Geometry | `textual.geometry` | 5 |
| Colors | `textual.color` | 4 |
| Markup | `textual.markup` | 1 |
| Validation/error contract | `textual.color` | 1 |

Every leaf crosses the candidate boundary through `custom-json-v1`; the
candidate process returns only JSON-safe values or a typed exception result.
The fixed denominator is 24 and collection mismatch is a verifier failure.

## Environment

- Agent base: `python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
- OS/architecture: Debian 13, linux/amd64
- Candidate dependencies: private hash-locked pip requirements artifact
  `sha256:a3a41659d2b2a9f2d37b1ab47273e9337b5f59c3667f623bfede67de76a49f09`
- Agent and verifier run mode: no-network
- Source fetch is available only to the trusted Oracle solution.
