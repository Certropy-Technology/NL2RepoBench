# `yarl` authoring audit

## Source freeze

- Upstream: `https://github.com/aio-libs/yarl`
- Commit: `f4314a0f11539162ea8655c591b659a9260f8e21`
- Tree: `6be6a76449c6249828f17aef2e6f54db63621c3c`
- Described revision: `v1.24.5-22-gf4314a0`
- Unprefixed `git archive --format=tar` SHA-256:
  `6fd74fd871f05a4e41223934380e224f9f3b8383f153cdf9a468dfe55c21948f`
- Archive: 798,720 bytes, 120 members, 98 regular files, 22 directories,
  no links or special files.
- License: Apache-2.0; `LICENSE` SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`.
- NOTICE SHA-256:
  `56d6ac6c8105c0a51304c21db060e361af9a8ea0af9a75c239c28b5d13693838`.

## Environment and dependency remediation

The revision supports Python 3.10 through 3.14. The task uses CPython 3.12.14
on the immutable `python:3.12.14-slim-bookworm` image digest
`sha256:0f5b26b9518d002b6173fd61daad821fa340635ebfec5bba471013f9ca114579`.

The upstream build backend can build a Cython extension or a documented
pure-Python wheel. `YARL_NO_EXTENSIONS=1` selects the pure-Python path, avoiding
a compiler and dynamic Cython build requirement without changing the tested
public contract. The 10-package build/runtime/Pydantic closure is exact-pinned
and hash-locked in `provenance/requirements.lock.txt`; verifier image build is
the only phase that accesses PyPI.

## Upstream test baseline

The first bounded collection probes identified two omitted test-bootstrap
requirements (`covdefaults` and Cython). After adding the revision's committed
Cython pin to the authoring-only test lock, the exact source installed as a
pure-Python wheel and ran offline on Python 3.12.14:

```text
1351 tests collected in 6.44s
1348 passed, 1 skipped, 2 xfailed in 35.62s
```

The fixed Harbor denominator is 44 deterministic public-behavior scenarios.
It deliberately excludes benchmark timing, property-based fuzz volume, and
native implementation details while covering every documented task surface.

## Verifier boundary

The private `custom-json-v1` verifier uses the repository's generic
`execute_script` candidate client. Every candidate observation occurs in a
separate UID-10001 process with per-call and cumulative timeouts, output and
resource limits, process-group termination, UID cleanup, and bounded storage
checks. Expected outputs were generated once from the frozen reference and are
kept only in the private content-addressed verifier artifact.

The trusted verifier never imports candidate `yarl`, and candidate code cannot
write collection, JUnit, grading, network, or reward artifacts.

## Network policy

Agent and verifier runtime policy is `no-network`; `agent_allowed_hosts` is
empty. Dependency installation occurs only during verifier image build from
the hash lock. The Oracle solution is the only task component containing Git
source acquisition. It fetches the exact commit, verifies `FETCH_HEAD`, creates
the canonical archive, and checks the frozen archive digest before populating
the workspace. The model Agent never receives that solution or source-host
authorization. 

## Task-local gate

The current source was compiled twice with the production Python compiler and
the two bundle manifests are byte-identical. The task-local separate verifier
image was built from the pinned Python base image and exercised with the
trusted Oracle solution plus empty, stub, forgery, install-hang, call-hang,
and offline controls. Structured receipts are stored under
`.nl2repo/authoring-work/yarl/`; `production-evidence.json` records their
hashes and the boundary that no Harbor Agent Run was started in this lane.
