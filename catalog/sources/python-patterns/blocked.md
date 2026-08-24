# `python-patterns` Static Conversion Audit

Status: **blocked**. This directory is an audit record only. It does not
contain a Harbor task descriptor, public instruction projection, Oracle
solution, verifier code, dependency bundle, copied source, or hidden test
bytes. No dataset, shared index, conversion-loop state, legacy task file, or
other task directory is changed by this audit.

## Decision

Do not emit a Harbor 1.4 bundle from the current legacy contract. The declared
denominator is numerically consistent with the immutable image, but four
independent publication blockers remain:

1. The source-identifying upstream revision has no license file, no SPDX or
   project license declaration, and no GitHub-detected license. An unmerged
   pull-request commit that added `LICENSE` is not in the revision's ancestry.
2. The image contains an unapproved 17-file metadata/test overlay. None of the
   17 image blobs occurs in any of the 1,151 reachable upstream commits that
   were inspected.
3. The editable-install command has no hash-locked offline build closure. The
   image `pyproject.toml` requires `setuptools>=77.0.3`, while the global image
   backend is `setuptools==65.5.1`; the historical build resolved dependencies
   from a public package mirror.
4. Every nonempty hidden test module imports candidate code directly and
   exercises live, stateful Python objects. No task-specific subprocess adapter
   exists for the required separate-verifier boundary.

The public instruction also contradicts the image-backed implementation and
test surface in material ways. These are specification/verifier problems, not
model failures.

## Legacy Contract

The four legacy artifacts under `test_files/python-patterns/` were read without
modification:

| Artifact | Bytes | SHA-256 | Parsed meaning |
| --- | ---: | --- | --- |
| `start.md` | 36,208 | `56910e9f2cc3a74c153a85c08b4bf1fad724b115b5a6ee3ca6c8527d5b0e4487` | Public instruction |
| `test_case_count.txt` | 2 | `a21855da08cb102d1d217c53dc5824a3a795c1c1a44e971bf01ab9da3a2acbbf` | Declared denominator `68` |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`, then `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The command and protected path have not changed since legacy initialization at
repository commit `dbe72aad8828d83ecee8f623c96fc961b80654f6`. The count was
changed from `84` to `68` at
`781a1da1ee41fb8edb0bed22f586d69111610edf` without changing the command or
test path. The image evidence below explains `68`; it does not explain the
earlier value `84`.

## Immutable Verifier Image

The canonical conversion-loop record observed at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` assigns this available
`linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/python-patterns@sha256:edff5bb715056497181080dab11470d077748e40667093dfb432471df180e9ad
```

Read-only registry retrieval returned a Docker Distribution v2 manifest whose
raw SHA-256 and `Docker-Content-Digest` both equal the assigned digest. Static
config evidence is:

- config digest:
  `sha256:b39c10663ad0a68ab7b70ddacf0a65ed11a61c0e4b9362ab329977c9d29ce8fe`;
- platform: `linux/amd64`;
- image-created timestamp: `2025-08-22T10:39:49.541885932Z`;
- runtime: CPython `3.10.11`, pip `23.0.1`, setuptools `65.5.1`, and wheel
  `0.40.0`;
- working directory: `/workspace`;
- configured command: `tail -f /dev/null`.

All task-relevant compressed layers below were downloaded into temporary
storage and checked against both manifest size and SHA-256. No image process
was started.

| Purpose from image history | Compressed digest | Bytes | Uncompressed diff ID |
| --- | --- | ---: | --- |
| Copy `tests/` to `/workspace/tests` | `sha256:502b11f7a847605cdcb45f844de323723707332018d0c3101dfd36ce4c60d4cf` | 35,106 | `sha256:183214e4bdb773955ab9c42d3ae500f3a8bef6f9adf2ccc7911d20cbbb64954c` |
| Copy `pyproject.toml` to `/workspace` | `sha256:9e165faf5dc8d061b51229263fe9c2de2c7bae8d086d8a5a2af02fd7d0924d6a` | 1,382 | `sha256:5c716c884f6391e55bdb61929a67cf048886bbfdf4190bfc05f18633f9f95e37` |
| Create `/python-patterns` | `sha256:7bcec93c04c0b1a604b6d204901edd98266dc1d6254174026d6200b959936223` | 105 | `sha256:01d695b401177e63443469ee0dc32f6a177a57b2d5df2293092018a5c890a9fb` |
| Copy complete source | `sha256:176c091df932c2b9683af13d84131708fe6408c1aa8cb5aba5db11852cacd7fc` | 3,344,515 | `sha256:1bcbb7e0f15bff8caaadc05c2e7ada09c3b4c6fa017af43bb3aec7f392c40c3c` |
| Online editable `.[dev]` install | `sha256:64776388d54dcf53f10ebc43c510d0b606d28188b13f6b93685aa8ffbd69f05d` | 57,486,611 | `sha256:116dba0a3ae017c2aa9678ef73c922ff820d26b11648152c9dfa5059b2122da8` |
| Historical `pytest` step | `sha256:1c9d59cc618ff1bd542b9cd200c04b4ab1a1f457050fe5bd594fba2254777a45` | 277,405 | `sha256:b3a19cf0811b502f4c9265ce9910fb84a72dde674874b4330aff49cf8c3175ef` |
| Delete source copy | `sha256:d9f14d41678c765b0caea40d9471e84733a7b9785e573d72f0d75a254e7c1244` | 85 | `sha256:3ca807775b213a3b88eed0d7d44b5f2407a007d773b1342bc51958ac16202447` |
| Remove stale editable artifacts | `sha256:2d5a606268ba222de614adb9b0bc83e0f9a9b2f3c70e56de74f125b7af224f80` | 6,927 | `sha256:8ceb53378799651d28e18b2d636b94c2760108ca7078c80fd9562f7e98d08af0` |

The exact historical build sequence was:

```text
COPY ./python-patterns-master/tests /workspace/tests
COPY ./python-patterns-master/pyproject.toml /workspace
COPY ./python-patterns-master /python-patterns
cd /python-patterns && pip install -e .[dev] -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /python-patterns && pytest
rm -rf /python-patterns
```

The successful image build and retained pytest cache are useful provenance
signals. They are not a structured collection record, JUnit report, Harbor
Oracle result, or offline-control result.

## Frozen Tests And Denominator

The retained workspace test tree and source-copy test tree are identical across
all 51 files. Excluding 34 generated CPython 3.10/3.11 bytecode cache files
leaves 17 authored files and 22,239 bytes. A canonical path/size/SHA-256
manifest for those 17 files has SHA-256
`eb5da4b65798839d29d515f40859af75d4f58c35f4db72e454a0ee8973d61be9`.
Including cache files gives 51 files, 141,843 bytes, and manifest SHA-256
`6965f4d86d7574a9fd3bf0d6bd68e9a87bccbee0a7d7a304fbc5fcc3a3f4c036`.
Only aggregate facts, paths, and hashes are recorded here; no test bytes are
stored in this task directory.

Static AST inspection produces this count:

| Group | Test modules | `test_*` definitions | Expanded cases |
| --- | ---: | ---: | ---: |
| Behavioral | 5 | 16 | 19 |
| Creational | 6 | 21 | 21 |
| Structural | 4 | 17 | 17 |
| Hierarchical state machine | 1 | 11 | 11 |
| **Total** | **16** | **65** | **68** |

The three parametrized functions each have two statically declared cases, so
they add three cases beyond their three function definitions. No skip, xfail,
module-level skip, collection-ignore, or collection-hook construct occurs in
the authored test tree. The historical pytest layer contains a cache with 68
unique node IDs, including six parametrized node IDs. That cache is 6,057 bytes
with SHA-256
`90306f30b61a263d8a669ee2ba143cd43b67191c2c9658d8114697ee00ffd792`.

The legacy denominator `68` is therefore numerically coherent. It is still not
a production frozen collection because no final-verifier JUnit/node-ID record
or three-run stability evidence exists. The historical command also inherits
`--doctest-modules`, pytest-randomly, and coverage options from the image
`pyproject.toml`; candidate packaging/configuration can influence that direct
pytest process.

## Upstream Source Lock

Exhaustive path/blob comparison against all 1,151 commits reachable from the
fetched upstream heads, tags, and pull-request refs identifies this source
baseline:

- upstream: `https://github.com/faif/python-patterns`;
- full revision: `3c0725a9e667c76641d6c5899346fdda940b5bc1`;
- subject: `Servant pattern (#413)`;
- parent: `bee048e5eac8208ea74c51743d1564cc95adb483`;
- tree: `d4249c8cab7d867e3a8cc20cb8707baed55b9f91`;
- author date: `2025-07-18T19:16:39-05:00`;
- committer date: `2025-07-19T02:16:39+02:00`;
- tracked paths: 111; submodules: none;
- unprefixed `git archive --format=tar` size: 3,717,120 bytes;
- repeated archive SHA-256:
  `ef6b1889cfcf826ebcbee0b4b6a809b954dd0ecda96ef5ef310d73aa96bc2339`.

All 111 upstream paths occur in the image source copy. Content comparison finds
94 exact blobs and 17 modifications; all 47 implementation Python modules under
`patterns/` are byte-identical. The selected revision is the unique best
pre-image-build match. Commit
`f74a1c41c8b3d9ac38390b69406bbb796772730b` has the same tree but was created
on a pull-request ref on 2025-08-23, after the immutable image.

### Missing License

The selected revision contains no `LICENSE`, `COPYING`, or other license-like
path. Its `pyproject.toml`, package metadata, and README contain no license or
SPDX declaration. GitHub repository metadata reports `license: null`, and the
commit-specific license endpoint returns HTTP 404.

Commit `a47e4cb331853eea9a55041355bcbed03768f9fc`, titled `Create LICENSE`,
exists only on fetched pull-request ref `pull/360`; it is not an ancestor of
the selected revision or canonical branch. Its bytes cannot be retroactively
assigned to the frozen source. The source license is therefore **unresolved**,
which alone blocks redistribution/publication under the repository authoring
rules.

## Image Overlay Inventory

The image differs in content at exactly these 17 upstream-tracked paths:

| Path | Upstream Git blob | Image SHA-256 |
| --- | --- | --- |
| `pyproject.toml` | `dfac5da9c6555d6c7a4704b5ab4e5c20117e5269` | `b86c3d958e8a02dc6f868052ba3c1056b13af24a62f182012a45ecb411c2f9b6` |
| `tests/behavioral/test_observer.py` | `821f97a61aa7a46e2b10c705af230637a92179e0` | `7dafc835ee95e916ba4a6586e885a50527e2a6ad45939e1be21c5e5c2783012e` |
| `tests/behavioral/test_publish_subscribe.py` | `c153da5b59dc429812f4b8f22e86a163012be6b5` | `ee62dd7cd8698a4ce24dda0fedfdba24f0e8725008e37354421feae79e727fea` |
| `tests/behavioral/test_servant.py` | `e5edb70d15a6552d75db84ba3492b2f1f40943e2` | `6dd50b095f201ab184a1435ba69c0c0654f368e58447a8fc2f85fd6bfa5d99dd` |
| `tests/behavioral/test_state.py` | `77473f519b023549e089ff9dbc7879714e10e1de` | `3e17167108ea5642383b4e8358b29b1f6f55eaa2153e61230b876237d3663a6e` |
| `tests/behavioral/test_strategy.py` | `53976f389538af1e1ca1bad15a196fb4391caed9` | `3e69f7132ddd650ee4ca6c032340be47f0c2c69cd9d6db784e809746da680bb4` |
| `tests/creational/test_abstract_factory.py` | `1676e59d19a8622dd453532a534939e377f0bfc1` | `90f683ce5d236002954877a4f7e6ac4f7d8374d3e5cedc58bab082d157212520` |
| `tests/creational/test_borg.py` | `182611c3744c31e4d9d0a096fd7ad9913fce5aeb` | `4bb1579079aaa5d6e653a9cb8fb733d22770f08fc0115414395540fb7479ea34` |
| `tests/creational/test_builder.py` | `923bc4a5c0333836858d220e20b60ca018297e82` | `3105e38301aaf34b60201fe53be1c1c4ee1f67335e47bdd61d3f68f99bfb2b2a` |
| `tests/creational/test_lazy.py` | `1b815b609e5444bef14e1dfe8a89c70a1ec34c9a` | `710b33c7675d4f6c8de30cf21c0a65954c1153b0fb022210f7d3721a2d81dc36` |
| `tests/creational/test_pool.py` | `cd501db387672b015f980da540554414f5eafa35` | `4c74a4cfead326708c66f61ba01d02ba822b74aa32ad07b872140ebc89988176` |
| `tests/creational/test_prototype.py` | `758ac8722c9379ca9f267c0ce1a80f2d923314f0` | `275371b9d0f5288362446ac73c13482e4da27789e9f8828858e0f2e8e6c3c50d` |
| `tests/structural/test_adapter.py` | `0132307520b30ed591066bf37b85f70a2bc8099b` | `4201dff21044ef20ed953df3551dbb1e395f21cc921757419d1188dce65ddaf7` |
| `tests/structural/test_bridge.py` | `7fa8a27893be1ec2b3c24cb82315a641797ea5bc` | `d4396e085c7f3fb43e19e907fa095805b600098e0cf8ab829cdee07e9612d1a1` |
| `tests/structural/test_decorator.py` | `8a4154a9103cd9a4fd8ff20d709442610c3c906c` | `eca3e882eb505728c67dcbb9025675ba82a89945439f2d0debca6aa3d96bc619` |
| `tests/structural/test_proxy.py` | `3409bf0b5d986cf01282e0248fcfd8a6c83cf35a` | `4e1bb38030b8108163000c3074e66e6a8a031e9a8e8689b780aecc4acdb4a2a4` |
| `tests/test_hsm.py` | `f42323a92919b6174dca2e1029736926ae6f4060` | `7e29ac1d92c902a9f7f58d1563836e955d74877acf150f7b9ffcaddfd4419ec2` |

The canonical 17-file patch is 7,737 bytes over 259 lines, with 16 additions,
26 deletions, and SHA-256
`6dfee91b0f95c48573094d7ae7ce935327919cc8a57b3ee9e552d23892b7ab66`.
It removes `readme = "README.md"` and coverage `dynamic_context` from
`pyproject.toml`; each of the 16 nonempty test modules changes explicit
candidate imports to wildcard imports. Assertion bodies are unchanged. All 17
image Git blobs are absent from every inspected upstream object.

The copy process also sets every one of the 203 source-layer files to mode
`0755`. Upstream has only `lint.sh` at mode `0755`, so 110 tracked paths have a
mode-only `0644` to `0755` overlay in addition to the content changes. The 92
image-only source paths are generated/editor artifacts: 78 bytecode caches,
eight IDE files, five egg-info files, and one coverage database.

No owner-approved overlay manifest, overlay source revision, overlay license,
or rationale is recorded in the conversion-loop state or task-local legacy
files. Image immutability preserves the bytes; it does not establish their
licensing or authoring provenance.

## Dependency Closure Blocker

The image source declares no runtime dependencies, but its build system is:

```text
requires = ["setuptools >= 77.0.3"]
build-backend = "setuptools.build_meta"
```

The base image has `setuptools==65.5.1`, below that requirement. The historical
online `.[dev]` install leaves 40 non-candidate distributions in the final
filesystem. A name/version manifest for those distributions has SHA-256
`c21664e6e1c8d11a51ba427bd2cab19851e06df28f2f6646836c72a04a886d29`;
notable test/config packages include `pytest==8.4.1`, `pytest-cov==6.2.1`,
`pytest-randomly==3.16.0`, `coverage==7.10.4`, `black==25.1.0`,
`isort==6.0.1`, `mypy==1.17.1`, and `flake8==7.3.0`. Pylint is not installed.

The image contains an opaque pip HTTP cache and virtualenv-embedded setuptools
wheels, but no approved wheelhouse, lockfile, hash manifest, `--no-index`
install plan, or evidence that PEP 517 build isolation resolves offline. The
legacy `pip install -e .` also permits candidate-selected build requirements.
Reusing the networked historical install would violate the offline verifier
contract; silently using `--no-build-isolation` would not satisfy the image
baseline's declared backend constraint.

## Candidate Boundary Blocker

All 16 nonempty test modules directly import one of 16 candidate modules into
the pytest process. Assertions construct and mutate cross-call objects,
including shared Borg instances, object pools and context managers, observer
graphs and mocks, publisher/subscriber queues, prototype dispatchers, adapter
objects, drawing-API mocks, decorator wrappers, and state-machine instances.

The repository's generic `candidate_client` starts a fresh unprivileged process
for each operation and transports JSON-serializable arguments/results. It has
no persistent object-handle, callback, mock, context-manager, or shared-state
protocol for these assertions. Directly running the image tests against the
candidate would let candidate import hooks, `conftest.py`, packaging metadata,
pytest plugins, and in-process code reach the report-writing process. Moving
the tests and assertions into a candidate-owned subprocess would make the
report forgeable.

No reviewed task-specific RPC/driver exists to preserve the frozen behavior
while keeping tests and grading trusted. A direct-import Harbor wrapper would
therefore violate the production separate-verifier contract even though it
could hide test bytes in the immutable image.

## Public Specification Mismatch

The legacy instruction is not bidirectionally traceable to the frozen source
and assertions:

- It requires `patterns/__init__.py` to re-export a long unified API. The
  upstream and image file is empty (zero bytes, SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`),
  and no hidden test imports that package root.
- It calls for exact dependencies including `black==24.4.2`,
  `isort==5.13.2`, and `pylint==3.2.2`. The image metadata declares lower
  bounds for black/isort, installs black `25.1.0` and isort `6.0.1`, and
  neither declares nor installs pylint.
- Several documented APIs are not the image APIs. Examples include a
  register/create `Factory` class instead of upstream `get_localizer`, a
  `Component` composite instead of `Graphic`/`CompositeGraphic`, an `inject`
  function instead of the three injection classes, and a target-taking
  `Proxy` constructor instead of upstream `Proxy()`.
- The instruction advertises the broad pattern library and code-quality
  checks, but the 68 scored cases directly cover only 16 of 47 implementation
  modules. The legacy command does not run black, isort, pylint, or mypy.
- The instruction's phrase "65 test functions" matches static function
  definitions, while the metric denominator is 68 after parametrization. This
  distinction is not stated in the public contract.

Publishing the image tests with this instruction would reward behavior that is
not fully specified and omit material advertised behavior. Repairing the
instruction, source revision, dependency requirements, or test selection would
create a new task version rather than an immutable legacy projection.

## Reopen Requirements

Reopen only after all of the following are supplied as reviewed, versioned
inputs:

1. A source revision with explicit redistributable license evidence, or an
   owner/legal determination that identifies a valid SPDX expression and its
   exact evidence. Do not borrow the unmerged pull-request license.
2. An owner-approved, licensed manifest for all 17 content overlays and the
   mode transformation, or a rebuilt image using exact files from a declared
   licensed revision.
3. A corrected public instruction and assertion traceability record. Any
   incompatible contract correction must use a new task/version identity.
4. A hash-locked offline build/test dependency bundle that satisfies the
   selected PEP 517 backend and preserves the fixed install semantics.
5. A task-specific trusted candidate protocol for stateful objects and
   callbacks, or a separately reviewed replacement test contract.
6. Final-image structured collection followed by three independent valid
   Oracle runs and empty/stub/forgery/offline controls in an execution-enabled
   validation lane.

## Static Validation Scope

The audit used repository parsing/hashing, read-only conversion-loop lookup,
read-only OCI registry manifest/config/layer retrieval, temporary tar
extraction, GitHub metadata requests, a full upstream Git clone/ref fetch,
exhaustive path/blob/history comparison, repeated `git archive` hashing,
Python AST inspection, TOML/source inspection, and repository diff/status
inspection. One optional base-OS layer transfer timed out before completion,
so no Debian release/native-package claim is made here; all task-specific
test/setup/source and dependency layers listed above were fully retrieved and
digest-checked.

No Docker command, container process, Harbor command, candidate install,
pytest command, Oracle, or negative control was run. No test was added or
executed. Temporary hidden fixtures remain outside the repository and are not
part of this patch.
