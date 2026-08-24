# SALib authoring audit

Status: `blocked` development source. This file records public provenance and
local validation evidence only. It contains no upstream test bytes, hidden
assertions, verifier implementation, dependency wheels, secrets, Docker files,
or Oracle bundle.

## Candidate source and license

- Candidate manifest: `reports/github-package-candidates.v1.json`
- Candidate ID: `salib`
- Upstream: `https://github.com/SALib/SALib`
- Checkout used for this audit: `/tmp/nl2repo-candidates/salib`
- Revision: `aa2c5545b3bfd0a982e9fad7625070a8ea340d38`
- Revision check: `git -C /tmp/nl2repo-candidates/salib rev-parse HEAD`
- Checkout status: clean at the start and end of the audit
- Git submodules: none (`git submodule status` produced no entries)
- Source archive command: `git -C /tmp/nl2repo-candidates/salib archive --format=tar HEAD`
- Repeated unprefixed archive SHA-256 (three runs):
  `484d5d062d3cedcd0a1ce13d3431e945e12177330badc39517ec0ee2c65337d0`
- Archive byte count: `3696640`
- License path: `LICENSE.md`
- License declaration: MIT (`pyproject.toml` and `LICENSE.md`)
- License size: `1107` bytes
- License SHA-256:
  `954fea77d90439a34c285a0989b31350c6f9c3e32bd44ad373fbe235995e56d1`
- Tracked Python files: `86` (`39025` lines by `wc -l`)
- Package Python files: `48` (`32257` lines by `wc -l`)
- Test Python files: `23` (`5836` lines by `wc -l`)

The candidate report supplied `difficulty = "medium"`, which is retained as a
provisional discovery label. Under the original NL2RepoBench LOC bands, 32,257
package lines fall in the **hard** band. The final dataset policy must resolve
that discrepancy before publication; this blocked audit does not assign a
production difficulty.

The source digest in `task.toml` is the exact unprefixed Git archive digest,
not a GitHub-generated prefixed tarball digest.

## Package and dependency inventory

`pyproject.toml` at the pinned revision declares:

- Python `>=3.10`;
- runtime lower bounds `numpy>=2.0`, `scipy>=1.9.3`, `matplotlib>=3.5`,
  `pandas>=2.0`, and `multiprocess`;
- optional `distributed` dependency `pathos>=0.3.2`;
- test extra `SALib[distributed]`, `pytest`, and `pytest-cov`;
- Hatchling/Hatch-VCS build requirements;
- the `salib = SALib.scripts.salib:main` console entry point.

`environment.yml` repeats broad lower bounds and adds the test, development,
and documentation environments. The pinned commit does not track `uv.lock`, a
requirements lock, a hash-pinned wheelhouse, or an equivalent dependency
bundle. A source import scan found direct imports of NumPy, SciPy, pandas,
matplotlib, `multiprocess`, and optional `pathos`; `p_tqdm` is optional and is
caught when unavailable. The dependency closure is therefore **not proven**.

A network-backed audit probe was able to build the source in a temporary Python
`3.13.14` environment. Its resolved versions were:

```text
SALib==1.5.3.dev69+gaa2c5545b
numpy==2.5.2
scipy==1.18.1
matplotlib==3.11.1
pandas==3.0.5
multiprocess==0.70.19
pathos==0.3.5
ppft==1.7.8
pox==0.3.7
dill==0.4.1
pytest==9.1.1
pytest-cov==7.1.0
hatchling==1.32.0
hatch-vcs==0.5.0
```

This probe is evidence of one install, not a lock. Sorted environment output was
saved outside the repository with SHA-256
`8ab01ba1ef962ec9611690f150e1e824f22b988850ac9146c0e2b653d2fa070b`.
No resolved package bytes were copied into the catalog.

A clean-cache offline build probe was also run:

```bash
UV_CACHE_DIR=/tmp/salib-empty-uv-cache \
  uv pip install --offline --no-cache \
  --python /tmp/salib-offline-venv/bin/python \
  --no-deps -e /tmp/nl2repo-candidates/salib
```

It exited `1` because `hatchling` was absent from the empty cache while
resolving `build-system.requires`. The captured diagnostic SHA-256 was
`deca8f6cdd2a177263f9181db627685a2afa61459e6df8e72197632cb55f528b`.
This is a direct indication that an offline closure has not been provisioned;
it is not an Oracle or full test run.

## Collection evidence

Collection command (no test bodies were copied into this repository):

```bash
cd /tmp/nl2repo-candidates/salib
PYTHONDONTWRITEBYTECODE=1 \
  /tmp/salib-audit-venv/bin/python -m pytest \
  --continue-on-collection-errors --collect-only -q -p no:cacheprovider
```

- Interpreter: CPython `3.13.14`
- Probe dependency versions: see the inventory above
- The temporary probe environment was disposable; only summarized evidence and hashes are retained here.
- Exit status: `0`
- Collected tests: `209`
- Collection errors: `0`
- Collection log SHA-256:
  `4bf9eaa90075b4573a9872a609d23eee31fe7fa2de2338ba522bb83110af1887`
- Test module count: `22`
- One `xfail` marker was collected (`tests/sample/morris/test_morris.py`);
  no skip markers were found by the static scan.

Observed module totals:

| Module | Collected |
| --- | ---: |
| `tests/sample/morris/test_morris.py` | 21 |
| `tests/sample/morris/test_morris_strategies.py` | 24 |
| `tests/sample/test_latin.py` | 6 |
| `tests/test_analyze_delta.py` | 16 |
| `tests/test_analyze_fast.py` | 2 |
| `tests/test_analyze_morris.py` | 14 |
| `tests/test_analyze_pawn.py` | 1 |
| `tests/test_cli_analyze.py` | 8 |
| `tests/test_cli.py` | 2 |
| `tests/test_cli_sample.py` | 7 |
| `tests/test_discrepancy.py` | 1 |
| `tests/test_ff.py` | 8 |
| `tests/test_groups.py` | 2 |
| `tests/test_hdmr.py` | 8 |
| `tests/test_problem_spec.py` | 7 |
| `tests/test_regression.py` | 19 |
| `tests/test_sample_seed.py` | 5 |
| `tests/test_sobol.py` | 14 |
| `tests/test_sp_sobol.py` | 12 |
| `tests/test_test_functions.py` | 14 |
| `tests/test_to_df.py` | 6 |
| `tests/test_util.py` | 12 |
| **Total** | **209** |

The `209` count is a local collection observation only. It is deliberately
recorded as `expected_total_source = "unknown"` in `task.toml` until a final
hash-locked verifier environment and private test bundle are available.

## Randomness and numerical tolerance review

Static scan command:

```bash
cd /tmp/nl2repo-candidates/salib
# AST/regex scan over tests for seeds, random calls, tolerances, and markers.
/tmp/salib-audit-venv/bin/python /tmp/salib-collection-audit/static-analysis.py
```

The equivalent scan output was saved outside the repository with SHA-256
`e9740a4842694a9078fef15a9d4b04f58ac7c6a2509163292948c0b95f51a892`
(script SHA-256: `c08f1237096d571eafdd63b8a2c3448b038f814a0eca28396bab022daa33a262`).
The audit found:

- explicit seed-related references in many tests (`47` `seed=` matches, `21`
  `handle_seed(...)` matches, and explicit NumPy/stdlib seed setup in the
  regression fixture);
- `9` random calls without a local seed/default RNG in five test modules:
  Sobol and SP-Sobol parallel helpers, two regression multivariate-normal
  inputs, two FAST sample-size selectors, and one Morris strategy error-path
  input;
- eight analyzer modules use `if seed:` rather than an explicit `seed is not
  None` check (`sobol`, `pawn`, `hdmr`, `ff`, `fast`, `enhanced_hdmr`, `dgsm`,
  and `delta`), so the behavior of `seed=0` needs an explicit contract;
- floating-point assertions span strict and broad tolerances, including
  `atol=0`/`rtol=1e-5`, exact `assert_allclose` calls, and broad values such as
  `rtol=1e-1`, `atol=5e-2`, and `atol=1e-1`; tolerance-bearing assertions occur
  in `12` test modules;
- the suite exercises NumPy/SciPy random generators, SciPy statistical and
  numerical routines, pandas conversion, multiprocessing, and numerical
  regression values.

Consequently, deterministic behavior and cross-platform numerical parity are
not proven by collection alone. Before publication, run repeated collection
and full baseline checks in the final locked environment, define whether
`xfail` is excluded or counted, and preserve the exact seed/tolerance policy
in the public specification and verifier contract.

## Separate-verifier boundary

The upstream suite is not expressible as a generic JSON-only candidate call:

- `ProblemSpec.evaluate` and related tests pass live Python callables and
  model functions into the candidate;
- tests exchange NumPy arrays and pandas DataFrames, inspect chained mutable
  `ProblemSpec` state, and call `evaluate_parallel`/`analyze_parallel`;
- CLI tests spawn the `salib` executable in subprocesses and use temporary
  files;
- plotting and result-conversion paths return or inspect scientific Python
  objects; and
- the package imports `multiprocess`, with optional distributed `pathos`
  behavior.

A task-specific adapter would need to run declarative scenarios in the
candidate process and return JSON-safe arrays/results while keeping expected
values and hidden assertions in a private verifier bundle. No such adapter,
private test bundle, or separate verifier command artifact is present here.
Direct trusted imports of candidate code would violate the required boundary.

## Decision and next stage

**Recommendation: keep `salib` blocked and do not publish or run Oracle.**

Unblock only after all of the following are separately evidenced:

1. a platform/Python-specific, hash-locked dependency bundle including build,
   runtime, test, and optional-process dependencies;
2. a pinned verifier image and fresh collection in that image, with a stable
   denominator and explicit xfail/skipped semantics;
3. repeated deterministic baseline evidence covering unseeded paths, seed `0`,
   BLAS/SciPy/NumPy variation, and the recorded floating-point tolerances;
4. a task-specific subprocess/JSON-safe adapter for callable, array, dataframe,
   CLI, and multiprocessing behavior; and
5. private hidden-test, command-plan, and Oracle artifacts resolved through the
   authorized private artifact store, followed by the required controls.

No Docker build, hidden-test materialization, shared index edit, secret use, or
Oracle run was performed for this pilot.
