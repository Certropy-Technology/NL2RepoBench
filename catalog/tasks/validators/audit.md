# `validators` Authoring Audit

Status: **blocked development source**. This task-local directory contains
public source metadata and an implementable public specification only. It does
not contain source archive bytes, license bytes, upstream test bytes, an Oracle,
a dependency wheelhouse, verifier code, a command-plan artifact, Dockerfiles,
Harbor assets, or run results.

## Candidate and source provenance

- Discovery record: `reports/github-package-candidates.v1.json`, task ID
  `validators`.
- Upstream: `https://github.com/python-validators/validators`.
- Requested and resolved detached revision:
  `70de324322def13a49a93d222f798ec1ab700885`.
- Commit tree: `55e9626ea285586998647f05894648b477c791b5`.
- Commit authored/committed: `2026-03-14T13:09:46+05:30`.
- Submodules: none.
- Clean unprefixed `git archive --format=tar HEAD`: 491,520 bytes,
  SHA-256 `0706c0c18ad618adfc253d7e3630a9571018295139443044ec0dfa30e0876dc1`.
- The detached checkout was clean before validation and was returned to a clean
  state after removing ignored pytest/build caches.

The candidate report's license evidence URL ends in `LICENSE`, but that path
does not exist at the pinned revision. The tracked file is `LICENSE.txt`. It is
1,091 bytes, Git blob `0fba9fb043984adbac590cdb76b13a3296af975b`, and SHA-256
`43f5c5d4ed194818baae8b6e2d2d09e9630752392efaa4b3f8da673d9a1a844a`.
Its bytes are the MIT License, with copyright `2013 - 2025 Konsta Vesterinen`.
The project metadata and wheel metadata also declare MIT. The catalog records
the corrected path/hash as evidence here without committing a second license
copy.

## Package metadata and size

`pyproject.toml` was parsed with `tomllib` (SHA-256
`8bcc2fc3abc7b04a4a4a794001be59aeaa07172dd34a787a889d444f93bedd1f`):

- distribution/import package: `validators`;
- package version from `validators.__version__`: `0.35.0`;
- Python requirement: `>=3.9`;
- build backend: `setuptools.build_meta`, with unpinned build requirement
  `setuptools`;
- required runtime dependencies: none;
- optional `crypto-eth-addresses` extra:
  `eth-hash[pycryptodome]>=0.7.0`;
- package layout: `src/validators`;
- package data: `_tld.txt` and `py.typed`;
- console entry points: none.

The implementation contains 32 Python files under `src/validators`, totaling
3,143 physical lines: 2,403 nonblank/non-leading-comment lines, 544 blank
lines, and 196 comment-only lines. The repository-level `src/__init__.py` adds
one blank line and is not part of the installed package. The tests contain 28
Python files and 2,247 physical lines. Under this repository's original LOC
bands, 3,143 implementation lines make this **medium** (1,500-4,000), not the
discovery report's unmeasured `easy` label.

A local wheel build succeeded as `validators-0.35.0-py3-none-any.whl` (44,783
bytes, SHA-256
`9204ff92323556547223bbbc9fec9f109b1e098532ce5c09e5cc3897f554aacf`).
This build is only a source/package sanity check: the temporary build used the
host build cache and is not an approved dependency or Oracle artifact.

## Dependency evidence

Upstream provides a generated, hash-bearing
`package/requirements.testing.txt` (SHA-256
`173c53a2bbc589b3f131de11f280a26045a7ee2179e8aa72474700222d1de94a`).
For Python 3.13 it resolves the relevant test environment to:

```text
colorama==0.4.6
eth-hash==0.7.0
iniconfig==2.0.0
packaging==24.1
pluggy==1.5.0
pycryptodome==3.20.0
pytest==8.3.2
```

`pdm.lock` is also tracked (SHA-256
`00c9e02579db4e121222fcd19e80e55f7f156aa725efb8df07d5056aedd65fe4`),
but neither file is an offline closure: no task-authorized wheelhouse or private
dependency artifact is available. The testing requirements also do not pin the
`setuptools` build backend. The dependency provenance therefore remains
`unknown` in `task.toml`.

The optional dependency changes test behavior materially. With pytest 8.3.2
but without `eth-hash`, the source run was `878 passed, 17 failed`; all 17
failures were `tests/crypto_addresses/test_eth_address.py` raising the
documented `ImportError`. With the upstream pinned testing requirements, all
895 tests pass. A final verifier must freeze the optional dependency and build
backend closure rather than silently omit the ETH surface.

## Collection and baseline evidence

The upstream pytest configuration sets `testpaths = "tests"`,
`pythonpath = ["src"]`, and `addopts = ["--doctest-modules"]`. In a temporary
CPython 3.13.14 environment installed from the hash-bearing testing
requirements, cache-disabled collection succeeded with 895 nodes and no
collection errors. The collected node list was 80,662 bytes with SHA-256
`1a6b587688e9516f98e10aff3ae4c4651db0bfbcc0c940d6090c3a33b77aeb02`.
Its per-file shape is:

```text
crypto_addresses/test_bsc_address.py   25
crypto_addresses/test_btc_address.py    8
crypto_addresses/test_eth_address.py   17
crypto_addresses/test_trx_address.py   27
i18n/test_es.py                         59
i18n/test_fi.py                         29
i18n/test_fr.py                         34
i18n/test_ind.py                        10
i18n/test_ru.py                         20
test__extremes.py                       12
test_between.py                         14
test_card.py                            126
test_country.py                          26
test_cron.py                             26
test_domain.py                           55
test_email.py                            29
test_encoding.py                         40
test_finance.py                          21
test_hashes.py                           45
test_hostname.py                         32
test_iban.py                              4
test_ip_address.py                       65
test_length.py                            8
test_mac_address.py                       8
test_slug.py                              8
test_url.py                             135
test_uuid.py                              8
test_validation_failure.py                4
                                           ---
                                           895 nodes / 28 files
```


Three independent direct-source baselines used this command shape:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /tmp/validators-upstream-venv/bin/python -m pytest \
  -p no:cacheprovider -q --junitxml=<temporary-path>
```

Each run collected and passed 895 tests, with zero failures, errors, or skips;
reported suite times were 1.269s, 1.340s, and 1.312s. The temporary JUnit files
and source checkout are not included in this task. These are source baselines,
not Harbor Oracle rewards, and the catalog deliberately uses
`expected_total_source = "unknown"` until collection is reproduced after
private test materialization in the final verifier environment.

## API inventory and candidate boundary

The installed package has 55 public top-level function definitions and three
public classes by AST (`ValidationError`, `AbsMin`, and `AbsMax`). Package root
`__all__` contains 55 re-exported names: 54 functions (including
`validator`) and the `ValidationError` class. `uri` is public in
`validators.uri` but is not root-re-exported; `AbsMin`/`AbsMax` are used and
tested through the `_extremes` module. There is no CLI.

The source specification covers package layout/version/data, the common result
and exception-raising contract, every root re-export, the documented i18n and
crypto submodule imports, and the non-re-exported `uri` function. The frozen
suite is mostly value-validation assertions, but it is not directly usable by
the production separate verifier:

1. Upstream tests directly import candidate functions and the rich
   `ValidationError`, `AbsMin`, and `AbsMax` objects in the trusted pytest
   process.
2. `between` tests pass `datetime` objects; `uuid` tests pass `uuid.UUID`
   objects; `_extremes` tests compare live custom objects; and
   `ValidationError` tests inspect a stored callable and instance dictionary.
3. The public `validator` decorator accepts a callable, the `url`
   `validate_scheme` option accepts a callable, and environment-controlled
   behavior is process-local.
4. The generic `candidate_client.call` boundary accepts JSON inputs and calls
   `json.dumps` on candidate return values. It cannot represent these inputs,
   callable arguments, or successful calls returning `ValidationError`
   instances without a task-specific scenario/normalization operation.

Trusted pytest must not import the candidate directly. A task-specific child
adapter should accept declarative JSON-safe scenarios, reconstruct rich values
and callables inside the untrusted child, and normalize results to JSON-safe
observations while preserving upstream assertions.

## Static commands run

The following commands were run without Docker, Harbor, Oracle, or a shared
catalog/dataset update. Temporary paths below are outside this task directory:

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout \
  https://github.com/python-validators/validators /tmp/nl2repo-validators-source
git -C /tmp/nl2repo-validators-source checkout --detach \
  70de324322def13a49a93d222f798ec1ab700885
git -C /tmp/nl2repo-validators-source archive --format=tar HEAD | sha256sum
sha256sum /tmp/nl2repo-validators-source/LICENSE.txt
uv pip install --python /tmp/validators-upstream-venv/bin/python \
  --require-hashes -r package/requirements.testing.txt
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /tmp/validators-upstream-venv/bin/python -m pytest \
  -p no:cacheprovider --collect-only -q
for run in 1 2 3; do \
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /tmp/validators-upstream-venv/bin/python -m pytest \
  -p no:cacheprovider -q --junitxml=/tmp/validators-final-${run}.xml; \
done
uv build --wheel --out-dir /tmp/validators-dist
uv run --frozen nl2repo task validate-source catalog/tasks/validators
uv run --frozen pytest -q
git diff --check
git status --short --untracked-files=all
git diff --cached --name-only
```

## Exact blocker and recommendation

There is no authorized durable private artifact store or task-local reference
for a hidden test bundle, allowlisted verifier command plan, complete offline
dependency wheelhouse, or Oracle bundle. There is also no reviewed
validators-specific subprocess adapter. Creating opaque refs without the bytes
would be non-resolvable; copying upstream tests here would publish hidden test
bytes; using direct-import pytest would violate the separate-verifier policy.

Keep the task blocked and do not create `harbor/`. To reopen it:

1. Build and review the task-specific scenario adapter, including normalized
   `ValidationError`, rich input, decorator/callable, and environment cases.
2. Materialize private content-addressed test, command, dependency, and Oracle
   artifacts; pin the build backend and Python/base image.
3. Recollect in the final offline verifier and freeze the structured
   denominator.
4. Run three valid Harbor Oracle jobs, then empty, stub, forgery, and offline
   controls before review or publication.

The root repository regression command `uv run --frozen pytest -q` completed
with 140 passing tests and 80.17% coverage. No Docker, Harbor, Oracle, negative
control, dataset compilation, or shared-catalog mutation was run.
