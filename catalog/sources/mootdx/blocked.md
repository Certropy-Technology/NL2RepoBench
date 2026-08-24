# `mootdx` Static Provenance and Blocker Audit

Status: **blocked**. The single failure class is `environment`: the final
legacy test path depends on mutable finance services and current-date/cache
behavior. This file is the historical audit; the directory now also contains
a parseable blocked descriptor and hashed remediation evidence, but no Harbor
runtime, Oracle solution, verifier script, dependency wheelhouse, or hidden test
bytes. The dataset catalog, shared indexes, conversion-loop state, and
`test_files/mootdx/` are unchanged.

The primary blocker is environmental: the effective test suite exercises live
TongdaXin/Sina/同花顺 financial-data services and current-date behavior. That
cannot be made a deterministic no-network Harbor verifier by pinning the
legacy image alone. The same environmental blocker is compounded by two
different test trees and a late, unapproved test/packaging overlay; the only
pytest collection cache belongs to the other tree.

## Legacy four-file contract

All four required artifacts exist and were read as JSON/text without running
pytest:

| Artifact | Size | SHA-256 | Observed value |
| --- | ---: | --- | --- |
| `start.md` | 153,768 bytes / 5,207 lines | `c2d17e68567c9e340685ab866da68bf5ef373f998e1e35dc9e6e6783034317cb` | Public instruction; claims Python 3.11.7 and mootdx 0.11.7 |
| `test_case_count.txt` | 2 bytes | `8241649609f88ccd2a0a5b233a07a538ec313ff6adf695aa44a969dbca39f67d` | `92` |
| `test_commands.json` | 90 bytes | `d3a2d6275cfc9336d62cbad263d1a09582e4c0098b47f36e45cbcba06ea8b1bb` | `pip install -e .`; `pip install requests`; `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 bytes | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | `["tests"]` |

The public instruction explicitly asks for real-time quotes, K-line/index/
minute data, server selection, financial-file download/parsing, ex-rights
adjustment, and holiday data. Those are not merely optional examples: the
frozen tests below call the corresponding live APIs.

## Immutable verifier image

The conversion-loop record at
`/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json` (and the
canonical retry state under `/root/NL2RepoBench`) assigns:

```text
ghcr.io/multimodal-art-projection/nl2repobench/mootdx@sha256:3250e7d6ef515f288f6307957d93b05a4d66889dbb2b3de3844f612f9457ddaf
```

The registry manifest fetched for that immutable reference has exactly the
requested digest and reports `linux/amd64`:

- Manifest media type: Docker distribution manifest v2.
- Manifest SHA-256: `3250e7d6ef515f288f6307957d93b05a4d66889dbb2b3de3844f612f9457ddaf`.
- Config digest: `sha256:88eb41fe3294ebca698d6410627e3271ccc517962647f705b6042168fc50f7ca`.
- Image config: CPython `3.11.7`, working directory `/workspace`, command
  `sleep infinity`, created `2025-09-16T07:48:32.796563892Z`.

Relevant manifest layers inspected without starting Docker:

| Build purpose | Layer digest | Compressed size |
| --- | --- | ---: |
| `COPY ./mootdx-master/tests ./tests/` | `sha256:5ef4122d3c14ab67f5d398e26f00e475964a017bb515e08e6a116e0becf3bfdc` | 11,372,837 |
| `COPY ./mootdx-master/pyproject.toml ./` | `sha256:8184dd389a3b3d1ba108e9f00bcd3202cfbb8a8d0b9ee05fe76b1525d177b67a` | 1,018 |
| `COPY ./mootdx-master /project/` | `sha256:36e6a3ebd4db24be55ff3052513047794b3443dd4390bdc20bc2d84fb12b43f8` | 11,594,010 |
| `RUN pytest ./tests/` and its cache | `sha256:a91056f02c2e9bbe480cd4b71d8b2074e2e710aec247c2580b81d8594bf1252b` | 755,878 |
| final DockerService workspace snapshot | `sha256:4b10a181982aefbc78eca1f2ec8498859e9145b6a34029e076afc3f2d66a4e13` | 11,375,086 |

The last three image-history entries are opaque `bash`/`sleep infinity`
DockerService snapshots rather than reproducible source-build commands. They
matter because the final snapshot changes `workspace/tests` after the image's
only retained pytest collection cache was produced.

## Upstream source lock

The source tree in the image's `/project` layer (excluding build-context
`.idea` extras and the test files discussed below) matches the following
reachable GitHub revision byte-for-byte across 85 tracked non-test paths:

- Repository: `https://github.com/mootdx/mootdx.git`
- Full revision: `e99ae34382d970c68654c6d17c45512e728f130d`
- Subject: `Create django.yml`
- Commit date: `2024-07-16T17:09:05+08:00`
- Parent: `98d87a655c2669dd0f02bf0c328ab35c6641cf4d`
- Tree: `6d436e514164f2a3ba13b680836888b1bd016258`
- Version declared by the revision: `0.11.7`

The reproducible source archive command is:

```bash
git -C /tmp/mootdx-upstream archive --format=tar \
  e99ae34382d970c68654c6d17c45512e728f130d | sha256sum
```

It produces a 57,600,000-byte unprefixed archive with SHA-256
`1572a695d11188fbf3319d89ea101960055186dfbc92322cce1e9ee560b984a4`.

License evidence is consistent:

- GitHub's commit-specific license endpoint identifies `LICENSE` as `MIT
  License` with SPDX `MIT` at this revision.
- `LICENSE` Git blob: `872bd63bfae78492149581f2472d14e3cb14dd2c`.
- `LICENSE` size: 1,065 bytes.
- `LICENSE` SHA-256:
  `ee03a051e103766e566b0a3ac0532daa665bb063cf8f30de46fd7c7ac9d00ec6`.
- The source `pyproject.toml` also declares `license = "MIT license"`.

The source dependency lock copied into the image is 22 lines,
`requirements.txt` SHA-256
`3cd5c6d70e3f2b359433ae2a451b04840a61ffad66aeb54cadae9851f713d648`, and
pins the main runtime packages (including `httpx==0.25.0`,
`mini-racer==0.12.0`, `numpy==1.24.3`, `pandas==1.5.3`, `tdxpy==0.2.6`, and
`tenacity==8.2.2`). This does not constitute a standalone offline wheelhouse:
the image build installed those packages from a network, and the test
requirements file is unpinned (`pytest-datadir`, `pytest-cov`, `pytest`, and
`freezegun`).

## Test-tree overlay and denominator audit

The image has two distinct test trees:

1. The original build layers retain `/tests` and `/project/tests`. This tree
   has 118 files (56,756,374 bytes); its path/size/SHA-256 manifest (paths
   relative to the test root, LF-terminated) is
   `00b0f4b8cbb20107787e568660df0668998e49bbc30f1ef3a900ab2f35049e4e`.
   Twenty-four Python files contain a benchmark-only import/lazy-import or
   fixture-skip overlay (mostly replacing explicit imports with wildcard
   imports), and one CSV is CRLF-normalized differently. The retained pytest
   cache was generated from this tree and contains **143** node IDs.

2. The final DockerService layers add `/workspace/tests`, which is the path
   used by the legacy post-processor after it removes the candidate's
   `tests` directory and runs `pytest ... tests` in `/workspace`. This tree
   also has 118 files (56,752,158 bytes); its corresponding manifest digest is
   `c286a5800a0b9b511eee52a9475e39ba9b750415a4b3df27305e398cf7dc7cc1`.
   It is not the tree represented by the 143-node cache.

The final `/workspace/tests` comparison to revision `e99ae34` is:

| Difference | Evidence |
| --- | --- |
| Upstream tracked `tests/.DS_Store` is absent | Upstream file: 6,148 bytes, Git blob `5008ddfcf53c02e82d7eee2e57c38e5672ef89f6`, SHA-256 `d65165279105ca6773180500688df4bdc69a2c7b771752f0a46ef120b7fd8ec3` |
| `tests/utils/test_utils.py` is an unapproved overlay | Upstream: 2,080 bytes, Git blob `65e190f0bd3033975ca470f99c5688b9f37504f2`, SHA-256 `3baf06c884b30a1e270685d6e843794a5b581ce975d0d46ac5f309d663f2bc59`; final image: 1,262 bytes, Git blob `4db7a85e6d24502cc355024117e2da05a008c641`, SHA-256 `935e05f54c1722d4659f3ce2f674f9835c87f1044667e2f0027ac3df0b980ed6` |

The overlay removes the `get_config_path` import and the three
`TestConfigPath` tests (`test_platform_windows`, `test_platform_linux`, and
`test_platform_Darwin`). The final overlay blob is absent from the reachable
history of `tests/utils/test_utils.py`; no owner-approved overlay manifest is
present in the loop state or repository.

Static AST inventory of the final tree finds 104 test function definitions
(107 at the upstream revision). Expanding the same literal parametrizations
represented in the image cache gives 140 collected items (143 minus the
three removed `TestConfigPath` items). Marker inventory gives:

- 48 unconditional skipped items, including the class-level financial,
extended-quotes, factor, and duplicate-test skips;
- 8 `skipif(not_mini_racer, ...)` holiday items;
- 84 unmarked items.

The pinned runtime requirements declare `mini-racer==0.12.0`, whose import
surface is `py_mini_racer`, so the expected effective count is
`140 - 48 = 92`, matching the legacy count **only as a static inference**. If
that module is unavailable, the effective count becomes 84. There is no final
`/workspace/tests` collection cache, JUnit file, or skip report. The available
143-node cache belongs to the other tree, so `expected_total_source =
"frozen-collection"` is not proven. A verifier must not silently choose
between the 143-item `/tests` tree and the 140-item final workspace tree.

The final workspace also has a packaging overlay. Its `pyproject.toml` is
1,079 bytes with SHA-256
`36403af847ed3ea71f4479b21a693ba673bdbe019e9e4def3bae91446c2d5a22` (Git
blob `58766422572cc15ec394b964393fb860ef7136a7`), versus the upstream
1,862-byte file SHA-256
`bd3b280f745a6608901c2f74bd658e6d2658fb61806195c6c9715c07cf996866` (Git
blob `33e1eef31fe419c95f9d798795530bddd86d5ee5`). The overlay removes the
README requirement and test/pytest/Poetry task sections. It is not an
upstream revision and has no separate provenance record.

## Network and finance dependency risk

The active test path is not offline-safe:

- `tests/quotes/test_quotes_std.py` constructs `Quotes.factory(...)`, which
  opens TCP connections to configured TongdaXin HQ servers on ports 7709 and
  requests live quotes, bars, index/minute data, transactions, F10, finance,
  and XDXR data. `test_minute` uses `datetime.now()` and compares current-day
  results from two live requests.
- `tests/test_adjust.py::TestAdjustUtil` and `tests/test_xdxr.py` call
  `get_xdxr`, which creates a live `Quotes` client when its 24-hour cache is
  missing or stale.
- `tests/tools/test_reversion.py` creates a live `Quotes` client and requests
  bars/XDXR data.
- Adjusted reader/quote cases transitively call live XDXR data through
  `to_adjust`/`get_xdxr`; the reversion helpers additionally call Sina factor
  endpoints through `fq_factor`.
- Holiday cases call `https://www.tdx.com.cn/url/holiday/` and
  `https://finance.sina.com.cn/realstock/company/klc_td_sh.txt`; the holiday test setup deliberately clears/resets a holiday cache.
- `get_adjust_year` uses `http://d.10jqka.com.cn/...` when its duplicate
  adjustment tests are enabled; those tests are currently marked skipped, but
  the API is part of the public contract.

The image contains `/root/.mootdx` cache files generated during the original
build. Their tar mtime is `2025-08-20 08:39`, while the cache decorators use a
24-hour refresh interval; they cannot freeze current evaluation behavior.
Several tests explicitly unlink or truncate those caches before exercising the
API. Consequently, a no-network verifier will fail, hang, or return a
service-dependent result, while a public-network verifier makes the score
vary with market state, trading date, remote server selection, and upstream
service availability. The required offline control cannot be meaningful with
this test contract.

The legacy command `pip install requests` is also unpinned and is not part of
the pinned source `requirements.txt`; the command plan has no recorded
wheelhouse or hash-locked artifact for it. This is an additional no-network
installation risk.

Finally, the tests directly import candidate modules and exercise live client
objects in the trusted pytest process. No task-specific subprocess/
`candidate_client` adapter exists in the image. Directly reusing these tests
would violate the separate-verifier boundary required for production Harbor
verifiers even if network access were enabled.

## Decision and reopen requirements

Keep `mootdx` **blocked**. The blocked `task.toml` and this audit are public
metadata only; do not create `instruction.md`, `harbor/`, a runtime task, or
any public copy of the hidden tests from this evidence.

To reopen, the owner should:

1. Build one new immutable image with one explicitly selected test path and a
   reviewed overlay manifest (or remove the unapproved overlay and rebuild
   from the exact upstream test blobs).
2. Run collection in the final verifier image and record JUnit/node IDs and
   skip outcomes. Preserve the legacy effective denominator of 92 only if the
   final run proves 140 collected and 48 skipped with `py_mini_racer` present;
   otherwise create a new task version rather than changing the denominator.
3. Replace live TDX/Sina/同花顺 calls with pinned local fixtures or a reviewed
   deterministic protocol stub, lock the complete dependency/native closure
   in an offline wheelhouse, and remove the unpinned `pip install requests`
   step or explicitly version the task contract.
4. Implement a task-specific candidate subprocess adapter before attempting a
   separate verifier, then run the three Oracle trials and empty/stub/forgery/
offline controls in a later lane.

## Static validation performed

The following checks were completed without starting Docker, Harbor, pytest,
or Oracle:

- Read `AGENTS.md` and `CONTRIBUTING.md`; inspected a neighboring complete
  task and blocked-audit formats.
- Parsed all four legacy artifacts and verified their byte hashes, JSON shapes,
  command order, protected path, and declared count.
- Resolved the immutable image reference from the conversion-loop state and
  fetched the registry manifest/config/layer metadata; manifest and blob
  digests were checked with SHA-256.
- Cloned the upstream GitHub repository, resolved the full revision, verified
  the commit-specific GitHub MIT license result, `LICENSE` blob/hash, and
  deterministic unprefixed `git archive` hash/size.
- Extracted only temporary OCI layers outside the repository, compared source
  and test trees by path/hash, recorded the final test and packaging overlays,
  and computed aggregate manifests without copying hidden bytes into this
  repository.
- Parsed the final test tree with Python `ast`, counted test definitions and
  parametrization markers, matched the image node-ID cache, and counted
  unconditional/conditional skip markers.
- Inspected source call sites and cache decorators statically for live finance
  endpoints, TCP server connections, current-date behavior, and refresh ages.
- The historical audit above did not run Docker, Harbor, pytest, Oracle, or
  controls. The later descriptor validation and blocked compile probe are
  recorded in `evidence/remediation.txt` and `production-evidence.json`; no
  shared catalog, generated runtime, or legacy file was edited.
