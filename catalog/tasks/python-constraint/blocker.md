# python-constraint Freeze Audit and Blocker

## Recommendation

**Blocked. Do not compile or publish a Harbor task from this directory.** The
source freeze and upstream baseline are healthy, but the current production
verifier cannot preserve the upstream assertions across its separate-verifier
subprocess boundary. No hidden tests, Oracle solution, or `harbor/` bundle are
stored here.

## Frozen source and license

- Upstream: `https://github.com/python-constraint/python-constraint`
- Commit: `d91ba03d1fd6acc30d64fd9d513dc0523f697b5b`
- Tree: `a2f6010080fc1518988e86bcbb8de1b4bfb233cf`
- Commit date: `2026-08-18T16:06:43+02:00`; submodules: none.
- `git archive --format=tar HEAD` SHA-256, reproduced three times:
  `c15171bf0b6e8271e099566d5acef4c322e2d2efa13dd1f92cb3370b5f4675ff`.
- `LICENSE`: 1,335 bytes, 23 lines, Git blob
  `1551a23ae2154250683c4e52001ade66e147d5cd`.
- `LICENSE` SHA-256:
  `e5894c331ba462210b707470b25f61ccd46bdadec5ee8290e71482a74742b62c`.
- Both pinned raw GitHub URLs returned identical license bytes. The text is the
  two-condition BSD license and `pyproject.toml` declares `BSD-2-Clause`.
- The unauthenticated GitHub license API probe returned HTTP 403; no claim here
  depends on that endpoint.

## Python, dependencies, and size

- Upstream supports Python `>=3.11`; the baseline used CPython `3.12.14` on
  Debian 13 (trixie), `linux/amd64`.
- Base image: `python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`.
- Required system packages: `gcc=4:14.2.0-1` and
  `libc6-dev:amd64=2.41-12+deb13u3`. GCC without libc headers failed at missing
  `stdlib.h`.
- Runtime dependencies: none. Build roots: `poetry-core==2.4.1`,
  `setuptools==84.0.0`, `Cython==3.2.9`. Test roots: `pytest==9.1.1`,
  `pytest-cov==7.1.0`, `pytest-benchmark==5.2.3`, `pep440==0.1.2`.
- No upstream lockfile or hash-locked offline wheelhouse exists; dependency
  provenance remains `unknown` and is an additional publication gap.
- Newline-counted tracked Python LOC: 3,235 in `constraint/*.py`, 4,148 for
  package plus examples, and 5,819 across all tracked Python files.
- Static package inventory: 43 non-underscore top-level definitions (30 classes
  and 13 functions), before imported star-reexports.

## Deterministic source baseline

Every run copied the frozen source into a fresh container, installed it with:

```text
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

and ran:

```text
python -m pytest --no-cov --benchmark-json=/out/benchmark.json \
  --junitxml=/out/junit.xml tests
```

The compiled environment collects 52 tests. Source-only collection is 49
because the benchmark module skips at module scope when extensions are absent;
52 is therefore the frozen compiled-environment baseline.

| Run | Exit | Collected | Passed | Fail/error/skip | Effective | Reward | Install | Pytest |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 52 | 52 | 0/0/0 | 52 | 1.0000 | 104 s | 66 s |
| 2 | 0 | 52 | 52 | 0/0/0 | 52 | 1.0000 | 112 s | 63 s |
| 3 | 0 | 52 | 52 | 0/0/0 | 52 | 1.0000 | 105 s | 66 s |

Each JUnit report contains 52 testcase elements and the stable failure set is
empty. Reward is `passed / frozen_total`. These are valid source baselines, not
Harbor Oracle jobs: no Harbor `grading.json` or `valid` field is claimed.

## Exact verifier boundary blocker

The production `candidate_client` starts a fresh unprivileged process for each
operation and transports requests/results through JSON. It can call one module
attribute, read one attribute, or run a module/console entry point. It has no
object-handle/session protocol, and returned values must be JSON serializable.

The frozen assertions require all of the following in one candidate process:

- construct a `Problem`, mutate it through several API calls, then solve it;
- pass lambdas and custom `Constraint` subclasses;
- preserve custom `Domain` subclasses and inspect forward-check mutations;
- consume generators and inspect returned constraint object types;
- execute candidate doctests and README examples;
- exercise `ParallelSolver` thread/process modes and pickling rejection.

Direct candidate imports from trusted pytest violate repository policy. Moving
assertions into a candidate-owned process makes them forgeable. Flattening them
into independent JSON calls changes their state, callback, subclass, generator,
or multiprocessing semantics. Preserving the assertions requires an approved
stateful task RPC/driver that keeps assertions and reports trusted while only
candidate implementation code runs unprivileged. That adapter does not exist.

Until that verifier capability and an offline dependency bundle exist, this
task must remain `blocked`; a complete-looking Harbor 1.4 bundle would be
misleading.
