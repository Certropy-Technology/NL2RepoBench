# `schedule-master` Provenance

## Naming

The legacy benchmark task ID is `schedule-master` and is intentionally retained.
The Python distribution and import package implemented by the task are both named
`schedule`.

## Frozen Verifier

### Current production verifier (task version 0.2.0)

The task was re-based off the legacy GHCR projection onto the reproducible
base image shared by the other published tasks, and converted to a private
`custom-json-v1` separate verifier.

- Base image: `python:3.12.14-slim-bookworm`
- Base image digest: `sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e`
- Runtime: Python 3.12.14 on Debian 12
- Locked candidate dependencies: pytest 8.4.1 and pytz 2025.2 (installed from the
  private offline wheelhouse during the Docker build phase)
- Verifier protocol: `custom-json-v1`, entrypoint `run.py`
- Frozen effective collection: 81 tests, no skipped cases

`system_packages` is empty. The frozen test module selects explicit POSIX `TZ`
strings (for example `CET-1CEST,M3.5.0,M10.5.0/3`) and calls `time.tzset()`, and
remote timezone behavior comes from the pinned pytz wheel, so no host tzdata
participates in grading. This was confirmed empirically: all timezone and
`align_utc_offset` cases pass on the plain slim base with no `tzdata` package.

Time-dependent behavior is deterministic and uses no real sleeps. The frozen
module contains no `time.sleep` call. It drives the clock with the upstream
`mock_datetime` context manager, which substitutes `datetime.datetime` with a
`MockDate` returning fixed instants and swaps `os.environ["TZ"]` plus
`time.tzset()`. The verifier preserves that injected-clock mechanism verbatim
instead of reimplementing it.

### Private artifacts

All three are registered in the private artifact store with media type
`application/vnd.nl2repobench.private-bundle+tar`:

| Bundle | Digest | Size (bytes) |
| --- | --- | --- |
| dependency wheelhouse | `sha256:7189900847f846f228fa95b397d2e358a1a66da7000cceb55e8e5fb2e880f95b` | 3512320 |
| verifier | `sha256:b768f96ccfa3a335d6c248cc22d8637e6065ee211b0f13f3002ab68fe3ae5cc1` | 92160 |
| oracle | `sha256:d44f267ff683af724478ec41bc8235dfd7d6638554a4f41a8fd344bbc2c50832` | 215040 |

The dependency wheelhouse holds every wheel at tar root plus a
`requirements.lock.txt` in which every pin carries a `--hash=sha256:` entry:
pytest 8.4.1, pytz 2025.2, iniconfig 2.1.0, packaging 25.0, pluggy 1.6.0,
pygments 2.19.2, setuptools 75.8.0 and wheel 0.45.1. `pygments` is required by
pytest 8.4.1. `setuptools` and `wheel` are required because candidate
installation runs `pip install --no-deps --no-build-isolation` against an
upstream `setuptools.build_meta` backend. `pytz` must be present for a
correctness reason and not only for convenience: the frozen module calls
`skipTest("pytz unavailable")` when pytz is missing, and the metric contract
excludes skipped cases, so a missing pytz would silently shrink the effective
denominator.

The verifier bundle holds `run.py` (trusted), `adapter.py` (candidate side) and
the frozen `test_schedule.py`. `run.py` runs as root and never imports candidate
code; it copies the frozen module into a candidate-owned scratch directory,
launches `runuser -u candidate -- ... python -I -B -` with `adapter.py` on
stdin, and folds the child's JSON report into leaves. Because `python -I`
ignores `PYTHONPATH`, the adapter inserts both `/tmp/candidate-site` and
`/opt/candidate-dependencies/site` onto `sys.path` explicitly, candidate site
first, so `schedule` resolves from the candidate while pytest and pytz resolve
from the locked dependency site. The adapter executes the frozen pytest module
in process so all 81 original upstream assertions run unmodified; no assertion
was rewritten or removed. It writes JSON to a trusted-created report file and
redirects pytest console output to stderr, so pytest output cannot pollute the
protocol boundary. Nothing but fixed trusted directory arguments crosses that
boundary: no Python source, import paths or shell commands. `run.py` embeds the
81 frozen node ids and emits exactly one leaf per frozen id, mapping an absent
id to `failed`, so a candidate cannot add, remove or rename graded leaves.

### Legacy verifier (task version 0.1.0, historical)

- Tagged source: `ghcr.io/multimodal-art-projection/nl2repobench/schedule-master:1.0`
- Immutable linux/amd64 manifest: `sha256:903e864b08437cacb1dbf4305f6ecc1443d09c6af7a714e2d81c4c5fee2d6677`
- Image creation timestamp: `2025-08-20T00:41:20.233994797Z`
- Runtime: Python 3.12.3 on Debian 12
- Relevant frozen packages: pytest 8.4.1 and pytz 2025.2
- Hidden path: `/workspace/test_schedule.py`
- Hidden bytes: 66,477 bytes, 1,592 lines
- Hidden SHA-256: `05bba4db69922fc2a9722451e668bb0bcc86d9a1b26550864abd7a631c46c66a`
- Hidden Git blob ID: `350ab5602d5f91b8044a9c78c738d7567ea6a520`
- Frozen effective collection: 81 tests, with no skipped cases in the pinned image

The frozen module carried forward into the current verifier bundle was extracted
from this legacy image and its SHA-256 still matches
`05bba4db69922fc2a9722451e668bb0bcc86d9a1b26550864abd7a631c46c66a`, so the
graded assertions are byte-identical across the re-base.

The legacy verifier started with `TZ=UTC`, `LANG=C.UTF-8`, and `LC_ALL=C.UTF-8`.
The frozen test module then selects an explicit POSIX Europe/Berlin timezone and
calls `time.tzset()`. The current verifier applies the same three environment
variables to the candidate child process.

## Denominator Evidence

The 81-test denominator survived the re-base, which was the precondition for
proceeding with it. Collecting the frozen module against the frozen upstream
source on `python:3.12.14-slim-bookworm` with the locked wheelhouse yields
`81 passed`, 81 collected, 0 skipped and 0 collection errors. The compiled
Oracle run then reported `collected: 81` equal to `expected_total: 81` with
`collection_errors: []`.

`expected_total_source` is `frozen-collection`.

## Gate Evidence

| Gate | Result | Artifact path |
| --- | --- | --- |
| Oracle | `valid=true`, reward `1.0`, 81/81 passed | `.nl2repo/runs/oracle/schedule-master-cmp/` |
| empty workspace | reward `0.0`, 0 collected | `.nl2repo/runs/oracle/schedule-master-empty/` |
| packaging + stub functions | reward `0.0`, 81 collected, 81 failed | `.nl2repo/runs/oracle/schedule-master-stub/` |
| forged reward files | reward `0.0`, forgery ignored | `.nl2repo/runs/oracle/schedule-master-forgery/` |
| offline verifier | completed with verifier network unavailable | `verifier/network.json` in each run |
| network policy lint | 0 errors | `uv run nl2repo task lint-network` |

The stub and forgery controls both keep the denominator at 81 with no collection
errors, so their zero score is attributable to missing behavior rather than to an
installation or collection failure. The forgery control writes
`{"reward": 1.0}` into `/logs/verifier/reward.json`, `/logs/verifier/grading.json`,
`/logs/verifier/junit.xml`, `/logs/verifier/collection.json` and
`/tmp/trusted-results/reward.json` from both the solve script and module import
time; graded output remained `reward 0.0`.

## Decisions Recorded

- Re-based the pinned base image from the legacy GHCR projection to
  `python:3.12.14-slim-bookworm` and bumped the task version from `0.1.0` to
  `0.2.0`. The denominator was re-collected on the new base first and survived
  unchanged at 81.
- Converted grading to a private `custom-json-v1` separate verifier. This keeps
  the original upstream assertions while satisfying the rule that trusted pytest
  must not import candidate code, and it removes the
  `tests.commands_artifact` publication gap.
- Replaced the Oracle `git fetch` with purely local extraction of
  `/solution/source.tar`. The agent stage is no-network, so the previous fetch
  could not succeed there and would have risked exposing a reference-source
  endpoint. The revision is unchanged and the archive digest proves the content
  is identical, so this does not change task semantics.
- Removed `tzdata` from `system_packages` after confirming empirically that the
  frozen POSIX-TZ tests pass without it.

## Source Revision

Upstream is `https://github.com/dbader/schedule`. The immutable source revision
is release 1.2.2 commit:

`82a43db1b938d8fdf60103bd41f329e06c8d3651`

The verifier image's `pyproject.toml` and `setup.py` exactly match Git blobs
`8f8ab03e8a264c41986524b616c7e5425d96407e` and
`3b340337d8ca8f43dfaf5d7560124eef54a6b75c` at that commit. The upstream test
blob is `f497826d1dca3c209ec55d205553ff4660268ab5`. The benchmark changed only its
import surface from the upstream explicit import list to a wildcard import;
the remainder of the test bytes is identical. This intentionally checks the
package's unified export surface without changing any behavioral assertion.

Reproduce the source archive digest with:

```bash
git -C /tmp/schedule archive --format=tar \
  82a43db1b938d8fdf60103bd41f329e06c8d3651 | sha256sum
```

Expected result:

`718fc6887ae9165aaf5f751780416ead8ce82844a2f615543f43acfaac7d4cff`

## License

`LICENSE.txt` at the pinned revision contains the standard MIT license and has
SHA-256 `30a8352c318ce1b645acde0299697342d4380ed2637d7ca18a8ad25661e3b41b`.
The same revision also declares `MIT License` in `pyproject.toml`, `MIT` in
`setup.py`, and the classifier `License :: OSI Approved :: MIT License`.
