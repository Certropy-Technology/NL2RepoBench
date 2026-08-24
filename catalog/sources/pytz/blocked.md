# `pytz` Static Provenance and Verifier Audit

**Status: oracle-passed remediation; timeout, review and pilot pending.** The
original blocked evidence below is retained as historical provenance. The
task-local remediation adds a pinned source freeze, generated timezone closure,
offline wheelhouse, private custom-json-v1 verifier and generic compiled Oracle
evidence. The current public instruction documents a 15-case stable API slice;
legacy 235-node statements below are historical only.

## Historical Decision

Do not create a Harbor 1.4 bundle from the current evidence. The source lock,
frozen test fixture, generated timezone data, runtime dependency boundary, and
candidate/verifier boundary do not describe one coherent task:

1. The catalog source lock is revision `661bca921e29dc3eedd4430bac70816c9154c05e`,
   while the immutable verifier image contains a checkout at
   `82e0891730a38fdcf8c9c680af34712d45a97fde` and tests assert version
   `2025.2`/IANA `2025b`.
2. The legacy contract declares four test paths and 235 collected nodes, but
   the final image exposes only three of those paths in `/workspace`; the
   generated conversion recipe also copies only those three paths. Its cached
   collection therefore cannot be reproduced with the declared fixture.
3. A clean upstream archive has only a symlink at `src/pytz/zoneinfo`; the
   image's successful build generated 604 zoneinfo files, a generated package,
   and `zdump.out`. Those outputs are not in the source archive or task-local
   package, and the final image deletes the source/build tree.
4. The final verifier image retains a complete `pytz-2025.2` reference egg.
   The frozen tests import `pytz` directly in-process, and no task-specific
   candidate-client or clean-environment contract exists. An empty candidate
   can consequently resolve the preinstalled reference unless the verifier
   explicitly removes and isolates it.
5. The task declares Python 3.12 and an empty/unknown dependency list, while
   the public instruction and immutable verifier use Python 3.10.18 and an
   unpinned `pip install pytest pytest-xdist` closure. There is no standalone
   hash-locked offline dependency bundle.

These are task/environment/verifier blockers, not model results. Do not lower
the denominator, replace the source revision silently, or copy generated or
private test artifacts into the agent image to make the conversion appear
complete.

## Legacy contract

The four legacy artifacts were read without modification:

| Artifact | Bytes | SHA-256 | Parsed meaning |
| --- | ---: | --- | --- |
| `test_files/pytz/start.md` | 27,296 | `986a8594ad31d3d9bff50286577e64630aa0192c920c92d6cfe3808fa683caee` | Public repository-generation instruction |
| `test_files/pytz/test_case_count.txt` | 3 | `0a2d643bfd24a028cd236e76575d828424ccffbfa47392bd09d8ca9dc85e2f8d` | Declares `235` |
| `test_files/pytz/test_commands.json` | 45 | `5a982a7dd0169d20187d318a3d35c2ce7ffb71942304590e6f80c35583add88d` | `pytest --continue-on-collection-errors -v` |
| `test_files/pytz/test_files.json` | 109 | `335706fd1e2fc4ee38bd1660a213bcf55d9f041c1a98cb716a880ff4e5230480` | Four protected paths |

The protected paths are exactly:

```text
src/pytz/tests/test_docs.py
src/pytz/tests/test_lazy.py
src/pytz/tests/test_tzinfo.py
test_zdump.py
```

`test_case_count.txt` contains `235` without a trailing newline. The historical
catalog instruction was byte-identical to `start.md`; the current remediation
intentionally replaces that broad legacy prompt with the bounded 15-case
contract documented in `instruction.md`.

The legacy command is rooted at the candidate workspace. It is not the same
as the image build command (`cd /pytz && pytest -v`), which ran after a source
build, package installation, generated `zdump.out`, and generated zoneinfo
materialization.

## Immutable verifier image

The conversion-loop record at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` assigns this available
`linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pytz@sha256:c331cc311b7112b55f66e0eaa505f6a6e63fc97a40e963c5a4b21900341477fc
```

The recorded tag is
`ghcr.io/multimodal-art-projection/nl2repobench/pytz:1.0`. Read-only registry
inspection returned the same Docker Distribution manifest digest. The
manifest body is 4,515 bytes and hashes to the requested digest. Its config
is:

- config digest: `sha256:30b2ac165aa7a0127ca9567b7fd4c94633ef025261d57d819eb8c79a28524ec6`;
- config JSON size: 9,480 bytes;
- platform: `linux/amd64`;
- Python: `3.10.18`;
- working directory: `/workspace`;
- command: `tail -f /dev/null`;
- environment timezone: `Asia/Shanghai`;
- base history identifies Debian `trixie`.

Relevant immutable layers are listed below. The layers were downloaded,
digest-checked, and inspected under `/tmp`; none is copied into this
repository.

| Image content/history | Compressed layer digest | Bytes |
| --- | --- | ---: |
| `COPY ./src/pytz/tests /workspace` | `sha256:8ddc398444fce229e28da93647cdb97673f421e850838998ca04792863191c8a` | 8,700 |
| `COPY ./src/setup.cfg /workspace` | `sha256:1b31355aca05065427097b579fac0c7652a848d38d359e1e8a6f75ed63dcefcf` | 217 |
| `COPY ./src/setup.py /workspace` | `sha256:a152b981781cb486e1271db19731bb61e4b8d1066baaf00eda1b3af5c71c6a24` | 971 |
| `COPY . /pytz` | `sha256:35f7f190b123371e98e79e0a5363c531609d214bec4dc86a6ff6b57040e4cb1c` | 11,442,060 |
| generated zoneinfo/build output (`make build`) | `sha256:efab6f83edbf51dc0d555cac024698d91fd5ae99fa5d380b9924b601440b7b66` | 2,128,513 |
| installed `pytz-2025.2` egg | `sha256:f79a678237d0d09c9a8499e30a80210d8448d2d7988d50ba4d84017ad03f6f52` | 2,878,976 |
| pytest/xdist dependency install | `sha256:19e79b72cb36e9ae7ba79da44f3a6f6ee78c9142b763d826b19a155205ec016d` | 7,329,250 |
| generated `zdump.out` | `sha256:340757bb534825c2d5bb778120f574a89f50996d9aa4cd4af12d68d40cfda3b8` | 659,932 |
| image pytest cache | `sha256:0e0141acfee693cb18d14b10eaecc8979e6e37e846a0381b2553e4c8fdece8e7` | 198,603 |
| final deletion of `/pytz` | `sha256:aa8aa1cea38a9ef160a049729caa9542964b97f90d8e866418ae9eb610d03a23` | 124 |

The final deletion layer contains `.wh.pytz`. Thus the final image no longer
has the source checkout, generated `zdump.out`, or the build tree in its
merged filesystem, even though those artifacts are visible in lower layers.
A derived verifier cannot recover them with an ordinary `COPY` from the final
image without a separately approved source-freeze artifact.

## Upstream source and license lock

The immutable image's `/pytz/.git` resolves to:

- upstream: `https://github.com/stub42/pytz`;
- full commit: `82e0891730a38fdcf8c9c680af34712d45a97fde`;
- peeled tag: `release_2025.2`;
- tree: `3b75b495875301bd2620a8f4d40c653bc5509721`;
- parent: `277b33cd8482780a8e79694d4c2c13033cd121aa`;
- commit date: `2025-03-25T12:51:52+11:00`;
- subject: `Bump version numbers to 2024.2 (2024b)`.

The reproducible image-source archive is:

```text
git archive --format=tar 82e0891730a38fdcf8c9c680af34712d45a97fde
size: 2,078,720 bytes
sha256: 5baef3d6b8b35c4b2c0f0bbd75c94aba5b306825a77a0915c2debf25d643b013
```

The revision's `LICENSE.txt` is MIT:

- size: 1,088 bytes;
- Git blob: `5f1c11289f6a54cb07ebdbf31d02e8e81b18b07f`;
- SHA-256: `be8b1a37ebe26c592a90f6c0eb33103a7f383ce2f4d7498c0af9a526990a07b8`.

GitHub's license endpoint for `stub42/pytz` reports `MIT` and the same
license blob SHA. License provenance is therefore coherent; it is not the
blocker.

The current catalog source lock is different:

```text
revision:    661bca921e29dc3eedd4430bac70816c9154c05e
source tree: fa70d134d0ebb07994b0ce6ef0aa74294063a209
archive:     2,140,160 bytes
archive sha: f46f66a141c36c377205ac76b122c04b9727b8edae3a4cbaed856ac209eb3e1b
```

That is the `release_2026.3.post1` revision, not the image's `release_2025.2`
revision. Both revisions happen to carry the same MIT license bytes, but 54 of
84 common tracked paths differ. The differences include functional files
`src/pytz/__init__.py`, `src/pytz/tzinfo.py`, `src/pytz/tzfile.py`,
`src/pytz/tests/test_tzinfo.py`, `test_zdump.py`, and `src/setup.py`. The image
test explicitly expects `pytz.__version__ == '2025.2'` and
`pytz.OLSON_VERSION == '2025b'`, so the catalog revision and image/test pair
cannot be claimed as one frozen source boundary.

## Test, setup, and source overlay audit

The image source checkout was compared path-by-path with every regular file
at image commit `82e089...`: all image-present tracked files matched exactly;
there was no functional source or test overlay relative to that commit. The
image build context did contain a non-upstream Dockerfile and generated
artifacts:

| Path/artifact | Bytes | SHA-256 | Provenance |
| --- | ---: | --- | --- |
| image build-context `Dockerfile` | 718 | `d741d070aeb34d5cc9f44f6103e4e989366c6a3612e207f8bbb2af2c99aee675` | benchmark/build overlay, absent at image commit |
| `/workspace/test_docs.py` | 842 | `21dbb12a9fb9399c3dae5fc35f6adebfff77e3a2386a7670ea97d08e92028b09` | exact `src/pytz/tests/test_docs.py` at `82e089...` |
| `/workspace/test_lazy.py` | 9,798 | `e24085c8387a724d26f63c90efc4794162d967fb081dbe2f0ee35def7ae37098` | exact `src/pytz/tests/test_lazy.py` at `82e089...` |
| `/workspace/test_tzinfo.py` | 28,068 | `02c1d9eabdb1094a450694a9e7c8b85481c4b917492f843d13096226f607f279` | exact `src/pytz/tests/test_tzinfo.py` at `82e089...` |
| `/pytz/test_zdump.py` lower-layer copy | 5,244 | `1dcacdb95cee001afebd9cf89be0e85a151be9de16452433b2fa4a8539d30a93` | exact `test_zdump.py` at `82e089...`, deleted from final merged image |
| `/workspace/setup.py` | 2,455 | `25b7f54c77662f1fb7c306822bea5460b65c081f32c548999fd3dab19716dac2` | exact `src/setup.py` at `82e089...` |
| `/workspace/setup.cfg` | 70 | `f4246b309aa94d5f178a89ecab8facf4c970606f5e9a968cf31bcdc1a88e8b97` | exact `src/setup.cfg` at `82e089...` |

The Dockerfile's meaningful build overlay is:

```text
COPY ./src/pytz/tests /workspace
COPY ./src/setup.cfg /workspace
COPY ./src/setup.py /workspace
RUN apt-get install -y rsync
COPY . /pytz
RUN cd /pytz && make build
RUN cd /pytz/build/dist && python setup.py install
RUN pip install pytest pytest-xdist
RUN cd /pytz && python gen_tests.py
RUN cd /pytz && pytest -v
```

This explains why the workspace test files are flattened while the actual
image collection used `src/pytz/tests/...` and `test_zdump.py` from the source
checkout. It is not an approved Harbor verifier contract.

## Denominator and fixture audit

The image's build-time pytest cache is static evidence, not a fresh test run.
Its node-id cache is 17,493 bytes with SHA-256
`05266c1f7d01effdb6c4ffe5f1a48c58d65a97bbae83b0d8faa3665e6eade2eb` and
contains 235 node IDs, distributed as:

| Collected path | Cached nodes |
| --- | ---: |
| `src/pytz/tests/test_docs.py` | 2 |
| `src/pytz/tests/test_lazy.py` | 39 |
| `src/pytz/tests/test_tzinfo.py` | 193 |
| `test_zdump.py` | 1 |
| **Total** | **235** |

Static AST inspection found no skip/xfail/parametrize or custom collection
hook in the three workspace test modules. `test_tzinfo.py` and `test_zdump.py`
construct unittest suites dynamically, so the cached node IDs—not a naive
function count—are the relevant image collection evidence.

The conversion recipe in `scripts/gen_harbor_from_legacy.py` currently lists
only:

```text
paths = ["test_docs.py", "test_lazy.py", "test_tzinfo.py"]
expected = 235
```

It omits the legacy-protected `test_zdump.py`. With the fixture paths that the
recipe can copy from final `/workspace`, the image's one `test_zdump.py` node
is absent and the expected collection is 234, not 235. Conversely, adding the
missing source test requires the generated `zdump.out` input and original
relative path; those are not present in final `/workspace`. The catalog also
records `expected_total_source = "unknown"`, so no frozen denominator artifact
exists in the task directory.

There is a second path-shape problem. `test_docs.py` computes its README path
two directories above `__file__`. In the original tree,
`src/pytz/tests/test_docs.py` resolves `src/README.rst`. A generic flattening
copy to `/tmp/candidate/test_docs.py` resolves `/README.rst` instead. A
verifier must preserve the original path or use an explicitly reviewed adapter;
changing the test path or denominator would change the legacy contract.

## Generated zoneinfo and source-freeze blocker

At both the image revision and the current catalog revision,
`src/pytz/zoneinfo` is a symlink to `../../build/etc/zoneinfo`, not a checked-in
zoneinfo tree. The source archive therefore has no compiled timezone files.
`src/setup.py` walks `pytz/zoneinfo` and asserts that more than ten resources
were found. The image's `Makefile` first compiles the bundled `tz/` source with
`make -C ./tz`, then `gen_tzinfo.py` copies generated data and expands the
package metadata.

Static layer inspection found:

- 604 generated files under `build/dist/pytz/zoneinfo` after `make build`;
- installed egg `pytz-2025.2-py3.10.egg`, 518,493 bytes,
  SHA-256 `d38ed947e958d46895953888d9210d3396eadc24727d867a4399ec79152e96d2`;
- the egg contains 621 ZIP entries, including 604 zoneinfo entries;
- generated `/pytz/zdump.out`, 7,790,640 bytes, SHA-256
  `838edae6185ab51f72d0ed08be889a631485915e73c0814c4b263208196cc247`;
- the final image removes `/pytz`, so neither `test_zdump.py` nor
  `zdump.out` is available from the merged verifier filesystem.

No task-local source-freeze artifact, generated-zoneinfo manifest, compiler
lock, or offline build/install proof exists. Reusing the installed egg would
leak the reference implementation and would not reconstruct the protected
`test_zdump.py` contract.

## Dependency and environment closure

The immutable image's installed distributions, read from the image layers,
are:

```text
pytz             2025.2       (zip egg with generated zoneinfo)
pip              23.0.1
setuptools       65.5.1
wheel            0.45.1
exceptiongroup   1.3.0
execnet          2.1.1
iniconfig         2.1.0
packaging        25.0
pluggy            1.6.0
Pygments         2.19.2
pytest            8.4.2
pytest-xdist     3.8.0
tomli            2.2.1
typing_extensions 4.15.0
```

The image history records `pip install pytest pytest-xdist` without version
pins or hashes. The actual versions above are frozen by the image digest, but
there is no standalone wheelhouse or dependency lock in `catalog/tasks/pytz`;
its `[dependencies]` section is `status = "unknown"` with `packages = []`.
The catalog environment declares Python `3.12`/Debian 12 and a
`python:3.12-slim` base (`base_image_digest =
sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`),
while the public instruction and verifier image use Python `3.10.18` and the
image history identifies Debian trixie. No separate agent/verifier environment
lock resolves this discrepancy.

This is insufficient for the required offline dependency-closure and
reproducible-install publication gate, even though the pinned image can serve
as static evidence for the versions above.

## Candidate/verifier boundary

The frozen tests import candidate code directly in the pytest/unittest process:
`test_lazy.py` imports `pytz.lazy`, `test_tzinfo.py` imports `pytz`,
`pytz.reference`, `pytz.tzfile`, and `pytz.tzinfo`, and `test_zdump.py` imports
`pytz`. No candidate-client subprocess or RPC contract is present in the
legacy task or current task directory.

The final verifier image also retains this complete reference package:

```text
/usr/local/lib/python3.10/site-packages/pytz-2025.2-py3.10.egg
bytes: 518,493
sha256: d38ed947e958d46895953888d9210d3396eadc24727d867a4399ec79152e96d2
easy-install.pth: ./pytz-2025.2-py3.10.egg
```

The egg includes the package modules and all 604 zoneinfo files. A verifier
that merely prepends candidate paths or runs pytest with the image's system
site-packages can let an empty workspace import this reference package. That
would invalidate the required empty/stub controls and makes the candidate
boundary non-coherent. The generic legacy conversion recipe does not create a
clean candidate environment or remove this egg; it only copies `/workspace`,
adds a path override, and starts pytest.

This historical audit predates the remediation. The current private
custom-json-v1 bundle uses a candidate-site subprocess boundary and trusted
report generation; the statements in this section describe the superseded
legacy conversion only.

## Historical Reopen Conditions (Superseded)

Reopen this task only after all of the following are versioned and reviewed:

1. Choose one source boundary: rebuild the immutable image/tests for
   `661bca...`, or change the task source lock to `82e089...` and record its
   archive/license evidence. Do not mix the two revisions.
2. Add a dedicated offline source-freeze stage that records the exact
   generated zoneinfo tree, generated package output, `zdump.out`, build tools,
   and hashes, or replace the test contract with an approved deterministic
   fixture. Preserve the original relative test paths.
3. Reconstruct all four protected paths, including `test_zdump.py` and its
   generated input, then collect in the final verifier image and freeze the
   denominator from structured collection. Do not silently change `235` to
   `234`.
4. Remove/isolate the preinstalled `pytz-2025.2` egg for candidate grading and
   implement a reviewed candidate-client or equivalent separate-verifier
   boundary that keeps candidate imports and report generation out of trusted
   grading.
5. Record a complete hash-locked offline dependency/environment closure with
   authoritative Python/OS versions and image digest.
6. The historical record did not run the formal Oracle/controls; the current
   remediation evidence is recorded in `provenance/oracle.md`.

## Historical Static Validation Record

Completed without starting Docker, Harbor, pytest, Oracle, or a negative
control:

- read `AGENTS.md` and `CONTRIBUTING.md` and checked the neighboring audit
  conventions;
- parsed and SHA-256 hashed all four legacy artifacts and verified instruction
  parity;
- read the conversion-loop record without modifying it;
- resolved the registry token, manifest, config, platform, history, and
  relevant layer digests via read-only HTTP requests;
- downloaded and digest-checked only selected image layers under `/tmp`, then
  inspected their file lists, metadata, generated artifact counts, and
  dependency metadata;
- cloned `https://github.com/stub42/pytz`, resolved both the image checkout and
  catalog revision, reproduced both deterministic `git archive` hashes, and
  verified the MIT license blob and GitHub license metadata;
- compared image source, setup, and test paths byte-for-byte with the image
  revision and inventoried generated/build overlays;
- parsed the cached node-id JSON and all test modules with Python `ast`, without
  running pytest; and
- inspected the clean worktree and task-local diff.

No hidden test bytes, image layers, source archive, Oracle result, or control
result are present in this task directory.

## Remediation Evidence (2026-08-24)

The original blocker was repaired within this task directory. The source boundary
is the catalog revision `661bca921e29dc3eedd4430bac70816c9154c05e`, whose archive,
tree hash, and MIT license hash are recorded in `source-freeze/manifest.json`.
The generated closure uses the upstream `Makefile` and checked-in `tz/` data at
that revision. Because the git archive omits the generated `tz/version` file,
the build stage explicitly materializes it as `2026c`; this is an environment
input, not a source change.

Commands and outcomes:

| Command | Exit | Evidence |
| --- | ---: | --- |
| `git clone https://github.com/stub42/pytz.git` and checkout `661bca...` | 0 | exact revision, tree `fa70d134...`, and MIT license hash in `source-freeze/manifest.json` |
| `git archive --format=tar.gz --prefix=pytz-661bca/ 661bca...` | 0 | `source-freeze/pytz-661bca.tar.gz`, SHA-256 `c4f2284211649716dc246972b68039da7d73e839938277ae6af32d7e871c5a8d`, 688647 bytes |
| First Docker closure without libc headers/version input | 2 | missing `time.h` and `tz/version`; remediation added `libc6-dev` and explicit version input |
| `docker build --platform linux/amd64 --no-cache -f source-freeze/Dockerfile` | 0 | image `sha256:7630b19d8d7adab34f1459e5af1ae00f0e1a0b07e06f73a303d39f45e163159c` |
| `source-freeze/rebuild.sh` | 0 | `generated_zoneinfo_files=604`; `zone.tab` SHA-256 `7cc78ea166261b3dedf951cdd721051460851e6fcd96c12b8e3194cf25677f21` |
| offline wheelhouse install with `--require-hashes` | 0 | setuptools `75.8.0`, wheel `0.45.1`; archive SHA-256 `492ad8f74160bd9490340e9116a579be55cfcdba2feaeeac02106d0ba71b1d07` |
| `docker build --platform linux/amd64 -f harbor/tests/Dockerfile` | 0 | verifier image `sha256:71d53d33e837d61a3a6454870fcff76f76dcf7a36764b28ee031c500802b8926` |
| separate verifier against generated reference workspace, `--network none` | 0 | `valid=true`, `collected=15`, `passed=15`, `failed=0`, reward `1.0` |
| separate verifier against empty workspace, `--network none` | 0 | `valid=false`, install exit `1`, `collected=0`, reward `0.0` |
| `uv run --no-sync nl2repo task validate-source catalog/tasks/pytz` | 0 | status `packaged`, source digest `sha256:e45e971413cb925a76e847cc823c8a7069095301476d53051a40b6ee48f3b5b7` |

The verifier does not import candidate code in the trusted process. It copies and
installs the candidate with `--no-index --no-deps`, launches `client.py` with
`python -I -S`, inserts only the candidate target directory, accepts one JSON
response per case, and writes `/logs/verifier/reward.json` itself. The 15 cases
cover metadata, UTC, three named zones, DST offsets, ambiguity/nonexistence,
normalization, conversion, fixed offsets, and unknown-zone errors.

## Remaining Gate State

This remediation is `packaged`, not `oracle-passed` or `controls-passed`. The
reference smoke and empty-workspace checks above are not the campaign Oracle or
full control suite. No model was run. The local Harbor executable is version
`0.15.0`, while the repository's locked compiler target is Harbor `0.21.0`; no
Harbor execution claim is made from the local CLI. The task is eligible for a
later Oracle, stub, forgery, and offline campaign in a pinned Harbor 0.21.0
runner.
