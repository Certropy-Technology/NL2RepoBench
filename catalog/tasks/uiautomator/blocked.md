# `uiautomator` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. It contains no
Harbor task descriptor, public instruction projection, Oracle solution,
verifier script, grader, or hidden test bytes. No legacy artifact, dataset
file, conversion-loop state, or other task directory was changed.

The legacy count is numerically consistent with the immutable image's cached
collection and historical log, and an upstream baseline and MIT license can be
identified. Publication is nevertheless blocked by unapproved functional
source/test overlays, a dependency installation that is not an offline
hash-locked closure, and a verifier suite that directly imports and patches
candidate code instead of using the required separate candidate boundary.

## Legacy Contract

| Artifact | Bytes | SHA-256 | Parsed value |
| --- | ---: | --- | --- |
| `test_files/uiautomator/start.md` | 86,937 | `8259abf353f5c38ab5ec7127dcc494541fb7f2afc82da25057cacbca586ab762` | Public repository-generation instruction |
| `test_files/uiautomator/test_case_count.txt` | 3 | `16dc368a89b428b2485484313ba67a3912ca03f2b2b42429174a4f8b3dc84e44` | Declared denominator `101` |
| `test_files/uiautomator/test_commands.json` | 61 | `0bd1b3d8d819a9bc29dce9aa35222ac4c7042dbf780304a6e34126f7e1d2dd3b` | `pip install -e .`; `pytest --continue-on-collection-errors` |
| `test_files/uiautomator/test_files.json` | 8 | `ecfd160805b1b0481fd0793c745be3b45d2054582de1c4df5d9b8fa4d78e7fbc` | Protected path `test` |

The command has no explicit test path; the legacy protected path is `test`.
The four artifacts parse successfully and were audited byte-for-byte.

## Immutable Verifier Image

The conversion-loop record at
`/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json` (read-only;
not in this worktree) records an available `linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/uiautomator@sha256:ba270145e580c003d5a32c0c8c9db9e5a9285f8359ce1c5cc46dea908420c9fb
```

The tagged reference in that record is
`ghcr.io/multimodal-art-projection/nl2repobench/uiautomator:1.0`; it is not
used as a source of identity. Read-only registry inspection resolved:

- Manifest digest and manifest JSON SHA-256:
  `ba270145e580c003d5a32c0c8c9db9e5a9285f8359ce1c5cc46dea908420c9fb`.
- Config digest:
  `sha256:9fe9501c2a34f82dc8bf49e4fbe6dc443d1d1823e3f7e2c648f664f38ca4ea9c`.
- Image creation time: `2025-09-01T05:29:44.412939029Z`.
- Runtime metadata: CPython `3.12.4`, pip `24.0`, `/workspace`,
  `CMD ["tail", "-f", "/dev/null"]`.

Relevant immutable layer evidence is:

| Content/history | Layer digest | Compressed bytes |
| --- | --- | ---: |
| `/workspace/test` | `sha256:f7bf2b9c2a8e577a9c02cf88ddc5ab9d7823709a3850712b7c0d95383375cd09` | 11,324 |
| `/workspace/setup.py` | `sha256:3f613ec17fcdc5685de16b4105c6427af259b80b3b6704683c4fd2130a9905e2` | 864 |
| `/workspace/requirements.txt` | `sha256:ed5b281f650867700c6f3b754f46a3c3e9b985a5eff3f6a257c49d39174739cc` | 165 |
| source checkout copied to `/uiautomator` | `sha256:947c88057c5927e26e51026c8b4a0d1ab8a11db435d859e813755ae87f1e6a9a` | 5,772,047 |
| historical `.pytest_cache` | `sha256:5b5972f221a29fd17b525c0fb0ac9e2861822c948855090ba5d977f42dac43fe` | 289,083 |
| final whiteout removing `/uiautomator` | `sha256:34476bd11e81ec2de8409640f6a4722e9a9242c0cbf2a6fceb402d6a7a03fc6e` | 81 |

The image history copies `test`, `setup.py`, and `requirements.txt` into
`/workspace`, copies a source checkout into `/uiautomator`, then runs:

```text
cd /uiautomator && pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /uiautomator && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install mock nose coverage pytest -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /uiautomator && pytest
rm -rf /uiautomator
```

The historical run is not a final structured collection artifact, and its
plain `pytest` command differs from the preserved legacy command.

## Upstream Baseline And License

The GitHub repository is `https://github.com/xiaocong/uiautomator`. Exhaustive
reachable-commit comparison identifies the following nearest upstream tree:

- Commit `53d288adcf9fc0fb8182fd738f7424c6e7b9387a`, full SHA, tree
  `bd81f1e03da05a381120570c9ca59b12e6af7ef3`, dated 2020-11-12, message
  `Fix missing sdk_version function call in __init__`.
- The current GitHub `master` commit is
  `ddef372b5bd3811f196290a1f75b636c6be9da2b`, with the same tree. The image
  has no Git metadata, so the image cannot distinguish these two commits.
- Unprefixed `git archive --format=tar 53d288adcf9fc0fb8182fd738f7424c6e7b9387a`:
  6,451,200 bytes, SHA-256
  `15a45f13c8e140fc0da64adc2b80eaea2909cd17903dac701e6ca60b4c98a2d3`.
- Unprefixed `git archive --format=tar ddef372b5bd3811f196290a1f75b636c6be9da2b`:
  6,451,200 bytes, SHA-256
  `082561c98864e47a4fd1608805a198d44e212aa9e3ce1c0ef850be8c49e76f89`.
- GitHub source `LICENSE` is MIT. At commit `53d288...` it is 1,077 bytes
  with SHA-256
  `d5bc10be88fb5064f566458124b11cede12bd7b31766f5e0035a9e797f345f2c`.
  The image copy is CRLF-normalized equivalent but has raw SHA-256
  `18a090cbbaa6dfd6f3386888870151161739b84b76edaa415b20d0134605dec1` and
  1,097 bytes.

These are the strongest upstream baseline candidates, not an exact source
lock for the verifier image: seven semantic image blobs below are absent from
all reachable upstream commits.

## Source, Setup, And Test Overlays

The source layer contains the 28 tracked paths from the upstream tree plus a
generated `test.log`. Ten text paths are CRLF-only equivalents of upstream
blobs and do not change content:

```text
.gitignore  .travis.yml  LICENSE  MANIFEST.in  README.md
requirements.txt  setup.py  test/test_device_obj.py
test/test_param_to_property.py  test/test_selector.py
```

The source `/uiautomator/test` tree and the workspace `/workspace/test` copy
are identical. `test/res/layout.xml` and all six APK/JAR package assets are
byte-identical to the upstream baseline. The seven semantic overlays are:

| Path | Image SHA-256 | Upstream blob SHA-256 | Overlay evidence |
| --- | --- | --- | --- |
| `setup.cfg` | `c73b5c1233d72868896bb313373d3b4958fb11e5fe01d0f577d3f5a03e089400` | `71f81489f9dcac4958232c39fc4b0e05d84b407010c0d39cd28b852294e4fd88` | Comments out the upstream metadata/description-file entries. |
| `test/test_adb.py` | `3d1e92d3557aabc57ba0aaa4eb99cb6352420fec23fe3f4e30fbf041dccece6f` | `b549a9d1965f61a4bb84d6284030270bb461bb70168168ea1cf28ca2acf11869` | Replaces the `distutils.spawn.find_executable` patch with `shutil.which`. |
| `test/test_device.py` | `55e862da9940967195228bf2ce21578413b733183d43a601ef87b6104c02e578` | `1b2f659f476b568eceb74e844530813e51f28159abc059748ab0db653c72f474` | Rewrites dump/screenshot assertions and uses a temporary file. |
| `test/test_jsonrpc.py` | `24525be5a5ba4d618655a4bdd5bf90adff25aff70face2ae2ce9065150234370` | `6d00ba827998b7b5d97a935d8049f11a0b6fd1724f81792372a1780819a86355` | Changes urllib patching and RPC setup, and removes an assertion. |
| `test/test_misc.py` | `a96a08801a80fee05a021f910887a079addeb32e76a79b018e41981e73e8eb03` | `a36bf49e3bc367ce300b2bd9012293cd05116a6577c1ed64f32543cbd53a2009` | Replaces the reload test with `__all__` checks and comments out reload. |
| `test/test_server.py` | `1983235d4108590e7354d9cb9a5d74625b40b91500561e7870228453574a11cd` | `7289c489b5acc71686f27f6bce951541bf7f18f85dd81f81c4611efa83d4520c` | Changes teardown, server-start expectations, recovery mocks, and file handling. |
| `uiautomator/__init__.py` | `f02db72fea2ff81b67c4affbafbfaf6ba90361cb347eb830b4ea6bf078fd9f6a` | `fcd2cd7a0a603d6d87a8ff541828a378a2cbb5a38027d29b8b3b979c8c3cbfb4` | Changes RPC IDs, ADB lookup, selector initialization, dump formatting, and exports. |

The semantic image blobs were checked against all reachable upstream objects;
none occurs in upstream history. Treating these files as the pinned GitHub
revision would therefore fabricate provenance. `test.log` is a historical
Windows run artifact, not an upstream source or a frozen structured result.

## Denominator Audit

Static evidence agrees on 101 nodes, but does not satisfy the production
freeze gate:

- The eight Python test files contain 101 `unittest` methods matching
  `test*`: `test_adb.py` 10, `test_device.py` 23, `test_device_obj.py` 34,
  `test_jsonrpc.py` 6, `test_misc.py` 5, `test_param_to_property.py` 3,
  `test_selector.py` 6, and `test_server.py` 14.
- The image's cached `uiautomator/.pytest_cache/v/cache/nodeids` contains 101
  node IDs; its SHA-256 is
  `911eb32587701d081d719acaa0471da34da1c1149f715e5b2d995abf2e3ea398`.
- The image `test.log` reports `collected 101 items` and `101 passed` on
  Windows, Python 3.12.4, pytest 8.4.1.

There is no preserved JUnit/JSON collection record from the final Linux image,
and the build-time command was plain `pytest` from `/uiautomator`, not the
legacy command from the workspace. Thus `101` is numerically coherent but its
`expected_total_source` is not `frozen-collection`; a final verifier
collection is required before publication.

## Dependency Closure

The declared dependency inputs are:

- `setup.py`: `urllib3>=1.7.1`;
- `setup.py` test requirements: `nose>=1.0`, `mock>=1.0.1`,
  `coverage>=3.6`;
- `requirements.txt`: `tox==1.6.0`.

Static image metadata shows these installed distributions and versions:

```text
coverage 7.10.6       distlib 0.4.0       filelock 3.19.1
iniconfig 2.1.0       mock 5.2.0          nose 1.3.7
packaging 25.0        platformdirs 4.4.0  pluggy 1.6.0
py 1.11.0             Pygments 2.19.2     pytest 8.4.1
tox 1.6.0             urllib3 2.5.0       virtualenv 20.34.0
```

This is an installed-state inventory, not a reproducible dependency bundle.
The image build downloads editable/runtime/test dependencies from the mutable
Tsinghua PyPI mirror, retains no hash-locked requirements file or complete
wheelhouse, and does not record a system-package lock. The immutable image
digest fixes this particular built state, but it does not provide the
offline, independently verifiable dependency artifact required for a new
no-network separate verifier.

## Candidate Boundary

The frozen tests are ordinary in-process `unittest` tests. They import
candidate symbols directly from `uiautomator`, patch `uiautomator.*` module
objects, patch `urllib.request.urlopen` and `subprocess.Popen`, inspect mock
call lists, and instantiate `Adb`, `AutomatorDevice`, `AutomatorServer`, and
related objects in the trusted pytest process. No `candidate_client`, RPC
adapter, CLI subprocess contract, or trusted/untrusted report boundary exists.

The legacy image therefore cannot be used as a Phase 2 Harbor verifier by
simply copying the workspace and prepending a candidate path: candidate
imports and behavior would execute in the trusted test process, and the
test-specific patch/object-identity semantics cannot be preserved by a
transparent subprocess wrapper. Replacing this with a task-specific client
would be a verifier redesign and must not silently change the frozen behavior
contract.

## Decision And Reopen Conditions

Keep `uiautomator` **blocked**. Do not create `task.toml`, `instruction.md`,
Harbor Dockerfiles, a solution script, private test references, or a Harbor
bundle. The precise publication blockers are:

1. `setup.cfg`, five test files, and `uiautomator/__init__.py` contain
   unapproved semantic overlays with no matching upstream Git object.
2. The verifier image's dependency setup is networked and lacks a complete
   hash-locked offline dependency artifact.
3. The 101-item denominator has only historical/cache evidence, not a final
   structured collection record under the legacy command.
4. The tests directly import and patch the candidate in the trusted process;
   the required separate candidate boundary is absent.

To reopen, obtain an owner-approved immutable overlay manifest or rebuild the
image from exact upstream files, preserve the intended test behavior in a
reviewed candidate-client/subprocess adapter, produce a hash-locked offline
dependency bundle, and collect the final verifier suite to establish the
fixed denominator. Only then run the three Oracle and empty/stub/forgery/offline
controls in a later execution lane.

## Static Validation

Completed without Docker, Harbor, pytest, Oracle, or negative-control runs:

- Read `AGENTS.md`, `CONTRIBUTING.md`, the legacy four-file contract, the
  conversion-loop implementation, and the Harbor verifier requirements.
- Read the conversion-loop record and resolved the immutable GHCR manifest;
  downloaded manifest/config/layer blobs by read-only registry requests and
  verified each blob digest, then inspected tar members without starting a
  container.
- Cloned the GitHub repository, enumerated 324 reachable commits, compared all
  28 tracked image paths against upstream history, computed both candidate
  archive hashes, and hashed the MIT license.
- Parsed the test tree with Python AST/static name counting and inspected the
  cached node IDs; all three static counts are 101. No pytest collection was
  run.
- Read package metadata for the installed dependency inventory and checked
  the image build history for dependency/network commands.
- Confirmed `git status` has no staged files outside this new task-local audit;
  no shared script, dataset, legacy task file, or loop state was edited.

No task-local Harbor files were generated because provenance, dependency
closure, denominator freeze, and the candidate-boundary gates are blocked.
