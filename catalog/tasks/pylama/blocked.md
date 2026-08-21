# `pylama` Static Provenance and Verifier Audit

**Status: blocked.** This directory is an audit record only. It contains no
Harbor task descriptor, public instruction projection, Oracle bundle, verifier
scripts, dependency bundle, or hidden test bytes. The shared dataset, legacy
files, conversion-loop state, and other task directories were not modified.

The blocker is not an inability to identify the project. The pinned image and
upstream source can be resolved, but the frozen test contract is not coherent:
the legacy denominator is `34` while the image contains `35` statically
collectable test functions with no skip/xfail or parametrization mechanism.
The image also carries an unapproved lint-test/setup overlay and a direct
pytest-plugin boundary that is unsafe for the required separate verifier.

## Legacy contract

The four legacy artifacts under `test_files/pylama/` were read without editing:

| Artifact | Bytes | SHA-256 | Parsed meaning |
| --- | ---: | --- | --- |
| `start.md` | 58,834 | `5c44173f80323b9ba4322366496ab58454656030b54690078356c46075229620` | Public repository-generation instruction |
| `test_case_count.txt` | 2 | `86e50149658661312a9e0b35558d84f6c6d3da797f552a9657fe0558ca40cdef` | Declared denominator `34` |
| `test_commands.json` | 68 | `cadc8238072221f75564224456e541df542a9b3ed155d46318e07b6372942f99` | `pip install -e .`; `pytest --continue-on-collection-errors tests/` |
| `test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected test path `tests` |

All JSON parses successfully and the count file parses as an integer. The
trailing slash in the legacy pytest argument is retained here because it is
part of the frozen command bytes. The repository history records that the
count changed from `35` to `34` in commit
`781a1da1ee41fb8edb0bed22f586d69111610edf`; no test path or image lock changed
with that edit.

## Immutable verifier image

The conversion-loop record at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` reports this available
`linux/amd64` image for `pylama`:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pylama@sha256:e7929131b1d143025731ebdbc1d413317a69cd43773d58e2abe2ce0df8510e77
```

The recorded tag is
`ghcr.io/multimodal-art-projection/nl2repobench/pylama:1.0`; the digest-pinned
reference above is the only image identity used by this audit. A registry
manifest-only request returned the same `Docker-Content-Digest` and a Docker
Distribution v2 manifest. Its raw manifest SHA-256 is
`e7929131b1d143025731ebdbc1d413317a69cd43773d58e2abe2ce0df8510e77`.

Static config evidence:

- config digest: `sha256:b58db46fadc17a697df2f80fbb74b008fe14415effcf83e1fd81a76922548690`;
- config JSON size: 11,826 bytes;
- platform: `linux/amd64`;
- runtime: CPython `3.13.7`;
- working directory: `/workspace`;
- configured command: `sleep infinity`;
- image-created timestamp: `2025-09-24T02:59:06.497038186Z`.

Relevant manifest layers and history entries are recorded below. The layer
contents were inspected in temporary storage without starting an image or
container; hidden test files remain uncommitted.

| Image history purpose | Compressed layer digest | Size |
| --- | --- | ---: |
| `COPY ./pylama-develop/tests /workspace/tests` | `sha256:f28611caa1e072a1697523e511f90b638ae6d009dfca78c72d79c4828c09b8ee` | 3,975 |
| `COPY ./pylama-develop/requirements /workspace/requirements` | `sha256:a44ff01834a304a3d750331b52826c1612c83e641e8d4e039d6da88a02420716` | 347 |
| `COPY ./pylama-develop/setup.py /workspace` | `sha256:a9bd4a0ac7bc091766c184568ad3a69c2964d89e28096489139688c11ad04cb4` | 503 |
| `COPY ./pylama-develop/setup.cfg /workspace` | `sha256:679d5b8334129269f3ebab21401c50b02e4e47bc65b5a6234aa27449284cb3ac` | 1,002 |
| `COPY ./pylama-develop /pylama` | `sha256:19d6696bea7f0dbb39c2ae26ad9eb99d424c7472b1a3a1e5e884c746e6cc03eb` | 322,253 |
| dependency installation (`.[tests,all,toml]`) | `sha256:ec8005eb73c6cfe34528bfe5f54f9879828cbefb44b91c9898e6730090788fc6` | 45,260,178 |
| historical build-time `cd /pylama && pytest` | `sha256:a8309574b37b8680543416eeda81467cdbf01be7773c54b1728bb8e9dc39358f` | 1,103,534 |

The image history uses a public mirror for the editable install, upgrades
setuptools, runs pytest with the source `setup.cfg` defaults, and removes the
source checkout afterward. This is provenance evidence only; it is not a
structured collection record, Oracle result, or offline-control result.

## Upstream source and license lock

The image source tree is best resolved to the tagged upstream release:

- repository: `https://github.com/klen/pylama`;
- revision: `53ad214de0aa9534e59bcd5f97d9d723d16cfdb8`;
- tag: `8.4.1` (the annotated tag resolves to this commit);
- subject: `Bump version: 8.4.0 → 8.4.1`;
- commit date: `2022-08-08T14:25:05+03:00`;
- tree: `b8bcc40e1f0410607e2f383148881e715e5b5a16`.

The deterministic source lock is:

```text
git archive --format=tar 53ad214de0aa9534e59bcd5f97d9d723d16cfdb8
size: 174080 bytes
sha256: f0285a20650d73f2bccd24d2f08935fe743cf17454f5e31eac0090acaccf6c5e
```

`LICENSE` at that revision is the MIT License:

- Git blob: `a0d2abf83e647361aba0d6e50d78344d7c1c397b`;
- file size: 1,106 bytes;
- file SHA-256: `48a99ec7c6538b527657d8e79838d9ff3b76063ee62009cc7196e94575578f93`;
- SPDX expression: `MIT`.

An exhaustive comparison of the 868 reachable commits found a maximum of 54
matching files out of the 56 upstream-tracked paths present in the image
source copy. The two matching commits have the same tree: the release commit
above and tree-equivalent merge commit
`2f9ab070ba524595628e1f8d785e8381dd6d7fdb`. The annotated `8.4.1` tag selects
`53ad214...` as the source lock; the image has no retained `.git` metadata that
could distinguish the tree-equivalent merge commit.

## Frozen test inventory and denominator audit

The image's protected `/workspace/tests` tree contains nine files and 15,867
bytes. A path-sorted inventory manifest rooted at the protected path (entries use
`tests/<relative-path><TAB>size<TAB>sha256`) has SHA-256
`3dd1e0d92c8a060304d7a566f26fb366e353dd230a469746300dac715e9aeb00`.
Only paths and hashes are recorded here; the test bytes remain in the pinned
image.

| Frozen path | Bytes | Image SHA-256 | Static test functions |
| --- | ---: | --- | ---: |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `tests/conftest.py` | 1,090 | `d7bea3d16f50eed3ae2375aace6d85c77236161ad69675ada7968f655e322c81` | 0 |
| `tests/test_config.py` | 958 | `06fb48a6420f1a413277c02c96230f2e5026ec1dbe38046d070ecfdddde0e81c` | 3 |
| `tests/test_config_toml.py` | 1,700 | `79d83b80bab26038e8c452aafb1d0765efb9698c570d53f3afd6c3257e74f8b1` | 1 |
| `tests/test_context.py` | 2,549 | `83621ee76e89ee7a714713d027ac12db651055083035c975d62f665f12baf9e0` | 7 |
| `tests/test_core.py` | 1,048 | `603e99ba80c9b80be6b4502616aed30aea54f5c3a95803d17ff5878811bd4201` | 5 |
| `tests/test_linters.py` | 6,343 | `f1e0a7abb3be4fd953f6657879e5868b56d102f34d0ce681ebe5cd798d6e762f` | 11 |
| `tests/test_shell.py` | 1,925 | `d5f8dbc14357479ba25f1618ef9ff7823d05134d7707de4b678da62738bdc886` | 6 |
| `tests/test_vcs.py` | 254 | `3d5b12b96fd5d07d62e29f97021240923765b9325bbde70f90f8c29c570edf60` | 2 |

The static total is **35** test functions. There are no `pytest.mark.skip`,
`skipif`, `xfail`, `parametrize`, `pytest_generate_tests`, or collection-ignore
constructs in the frozen test tree. The count is therefore:

```text
legacy declared denominator: 34
static collectable functions: 35
unexplained difference: 1
```

This is not a frozen pytest collection result, but it is enough to reject a
fixed-denominator conversion: no evidence identifies a legitimate excluded
case, and changing `34` to `35` would change the legacy metric contract.
The image history's build-time pytest command did not preserve JUnit, node IDs,
or a collection manifest that could resolve the difference.

## Source/test overlays

The workspace setup/test files are not all upstream blobs at the locked tree.
The image and workspace copies are byte-identical to one another, but two
paths are overlays absent from every reachable upstream object:

| Path | Upstream blob | Image SHA-256 | Overlay result |
| --- | --- | --- | --- |
| `setup.cfg` | `d7f4683d57493bea11fd3f317a7c79cf8b62c33f` | `6c5876c83bf38afd0c7c2ec0d23b7a99475e9ef0380512a08c33da33bec145bc` | Pins `version = 8.4.1`; removes `long_description = file: README.rst` and `license_files = LICENSE`. |
| `tests/test_linters.py` | `6365eb0980d2e754249ed012b1ae58a0c02467be` | `f1e0a7abb3be4fd953f6657879e5868b56d102f34d0ce681ebe5cd798d6e762f` | Makes the mypy assertion vacuous, broadens the Pylint ignore from `C` to `C,R`, and retains an inactive commented test block. |

The canonical two-file unified patch (with stable `upstream/` and `image/`
labels) is 2,439 bytes with SHA-256
`e176c94f008515ef20afda8f9a3deaf3554c0056b2e22b587983c6735e5613e0`.
Neither overlay blob occurs in `git rev-list --objects --all` for the upstream
repository. No owner-approved immutable overlay manifest is present in the
conversion-loop state.

The other eight test files and both requirements files compare byte-for-byte to
the locked upstream tree. The workspace packaging/dependency copies are also
recorded here for the verifier audit: `setup.py` is 702 bytes with SHA-256
`01946070e8941e80310a5e38581ad56ff384e38d03a19214cac296b50fd0919e9`,
`requirements/requirements.txt` is 105 bytes with SHA-256
`3b6cabe324808dd7f6b89a85ad3c644746c37a6a0bc74884cb00988e5610816a`, and
`requirements/requirements-tests.txt` is 158 bytes with SHA-256
`65e14974201621709f192e7a586db6c7bae862125c898f0b34d0ed0369fee010`.
The image's installed lint/plugin closure is newer
than the source lower bounds, including:

```text
eradicate==3.0.0       isort==6.0.1          mccabe==0.7.0
mypy==1.18.2            pycodestyle==2.14.0   pydocstyle==6.3.0
pyflakes==3.4.0         pylint==3.3.8         pytest==8.4.2
pytest-mypy==1.0.1      pylama-quotes==0.1.0  radon==6.0.1
toml==0.10.2            vulture==2.14
```

The source requirement files contain only lower bounds and the image history
installs `.[tests,all,toml]` from a mirror. No hash-locked wheelhouse or
standalone dependency manifest is recorded. The overlay changes are
consistent with dependency drift (the upstream mypy and Pylint assertions do
not remain stable under the image closure), but consistency is not provenance
or approval.

## Lint/plugin and verifier-boundary risks

This task is unusually sensitive to the test runner boundary:

1. `setup.cfg` registers `pylama = pylama.pytest` under the `pytest11` entry
   point. `pylama.lint` also discovers optional linters through installed
   `pylama.linter` entry points; the frozen tests exercise Pylint, mypy,
   eradicate, radon, vulture, and the `pylama-quotes` plugin.
2. The legacy command does not disable pytest plugin autoload. A candidate can
   therefore affect the trusted pytest process through packaging metadata,
   `pytest11` entry points, `conftest.py`, or import-time plugin code. The
   frozen tests themselves import candidate modules directly through fixtures.
3. The production verifier contract requires a separate candidate client and
   forbids trusted pytest from directly importing candidate code. No
   pylama-specific subprocess/RPC adapter exists that preserves the linter
   and pytest-plugin assertions. A simple path-prepend adapter would make the
   candidate and report writer share the trusted process.
4. The upstream `setup.cfg` includes `addopts = -xsv`. Unless the verifier
   changes the legacy command, one lint/plugin failure stops execution after
   the first failure; a JUnit file can then contain fewer executed cases than
   the already mismatched fixed denominator. Changing `addopts` or excluding a
   test would be an unapproved metric/command change.

These are verifier/specification risks, not model failures. In particular, the
mypy assertion change and widened Pylint ignore reduce or alter the advertised
lint behavior while the legacy denominator supplies no principled exclusion.

## Decision and reopen conditions

Keep `pylama` **blocked**. Do not create `task.toml`, `instruction.md`, a
Harbor 1.4 tree, an Oracle solve script, or a private test fixture in this
lane. The source URL, tagged full SHA, MIT license, archive digest, immutable
image reference, image test inventory, and overlay hashes are sufficient for a
future re-open, but not for a coherent fixed-denominator task today.

To reopen, all of the following are required:

1. Reconcile the `34` versus `35` collection contract using a frozen collection
   and node-id record. Preserve `34` only if one explicitly documented,
   immutable exclusion is part of the approved legacy metric; otherwise create
   a new task version rather than silently changing the denominator.
2. Obtain an owner-approved overlay manifest for `setup.cfg` and
   `tests/test_linters.py`, or replace the image with exact upstream test/setup
   blobs. The manifest must state the overlay source, license, purpose, and
   expected behavior for the mypy/Pylint changes.
3. Lock the verifier lint/plugin dependency closure and isolate pytest plugin
   discovery. Provide a task-specific candidate-client adapter for direct
   linter and pytest-plugin behavior, or explicitly approve a new verifier
   contract with controls that prevent candidate plugin code from reaching
   trusted grading.
4. Freeze a command plan that handles the `-xsv` pytest configuration without
   changing the legacy metric, then run three independent valid Oracle trials
   and empty/stub/forgery/offline controls in a later execution lane.

## Static validation

Completed without starting Docker, Harbor, pytest, Oracle, or a negative
control:

- Read `AGENTS.md` and `CONTRIBUTING.md`; checked the task-local legacy shape
  and neighboring audit conventions.
- Parsed and SHA-256 hashed all four legacy artifacts; validated both JSON
  arrays and the integer denominator.
- Read the conversion-loop record and resolved the exact immutable image
  reference; performed a registry token/manifest/config request and verified
  the returned manifest digest.
- Downloaded only the relevant image layers to temporary storage, inspected
  their file lists/config/history, and retained no hidden fixture bytes in the
  repository.
- Cloned the upstream repository, resolved tag `8.4.1`, repeated the
  deterministic archive and license hashes, and compared image source paths
  against all 868 reachable commits.
- Inventory-counted the nine frozen test files with Python AST; found 35 test
  functions and no skip/xfail/parametrize or collection hook that explains the
  legacy `34`.
- Compared every frozen test/setup/requirements path with the locked upstream
  tree, checked overlay blob absence across reachable history, and hashed the
  canonical two-file patch.
- Inspected dependency metadata from the pinned image layer and recorded the
  lint/plugin versions above.

No test was added or executed. No Docker/Harbor/Oracle process was run.
