# PyMongo Authoring Audit

## Frozen Source

- Upstream: `https://github.com/mongodb/mongo-python-driver`
- Revision: `ebc4bffcc842464e48a3edbd04802d1a42bc818a`
- Commit date: `2026-08-21T11:01:20-07:00`
- License: Apache-2.0; `LICENSE` is 11,357 bytes with SHA-256
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
- Unprefixed `git archive --format=tar <revision>`: 21,166,080 bytes,
  SHA-256 `933f254602e0ec43f463d7a9648f46623c86ba4fd81d9c8703bbe444d13aa068`.
- The static scanner's content-tree digest is
  `d2882d62405f4f6a5746bb5b91756246b5279715850d1fd9cef98c268038af6d`.
  It is recorded as inventory evidence only; the production source pin uses
  the reproducible Git archive digest above.

## Inventory And Baseline

The deterministic AST inventory reports 201 implementation Python files,
64,805 implementation LOC, 7,970 public symbols, 226 test files, 67,016 test
LOC, and 3,062 static test nodes. The repository-wide risk flags are dynamic
execution and external services. The published task intentionally narrows those
risks to local BSON, ObjectId, URI, and scalar validation behavior.

The upstream `test/test_json_util.py`, `test/test_objectid.py`, and
`test/test_uri_parser.py` subset ran three times in a Linux network namespace.
Every run produced 69 passing test methods plus 5 passing subtests. Each JUnit
document contains 74 leaves with zero failures, errors, or skips.

The production verifier contains 51 unique allowlisted subprocess scenarios:

| Contract | Leaves | Upstream coverage source |
| --- | ---: | --- |
| package version | 1 | package metadata and import smoke |
| JSON utilities | 7 | `test/test_json_util.py` |
| ObjectId validation | 7 | `test/test_objectid.py` |
| host parsing | 9 | `test/test_uri_parser.py` |
| host-list parsing | 5 | `test/test_uri_parser.py` |
| URI parsing | 10 | `test/test_uri_parser.py` |
| scalar validators | 12 | public validator implementations and `test/test_common.py` inventory |

All 51 reference outputs were generated independently three times and were
byte-identical. The case document SHA-256 is
`06d0893e97770822bb737270133414ac9016b6bab7780fe814e9e527202ccf1b`.
Expected values and scenario inputs remain in the private verifier artifact.

## Boundary And Network

The separate verifier copies and installs `/workspace` into a candidate-owned
site directory with `--no-deps --no-build-isolation`, then invokes each
allowlisted operation in a fresh UID 10001 subprocess. Trusted code compares
the resulting JSON values and writes the structured 51-leaf report. Candidate
code never imports into the trusted report writer.

The agent and verifier phases use `no-network`. The candidate/build closure is
installed from a SHA-256 hash-locked requirements file at image-build time; no
wheelhouse is vendored. The Oracle receives a private, digest-verified archive
of the exact revision and therefore does not need runtime source access.
