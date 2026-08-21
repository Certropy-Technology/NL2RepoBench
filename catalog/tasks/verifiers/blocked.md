# `verifiers` Static Conversion Audit

Status: **blocked**. This directory is an audit record only. It is not a
publishable Harbor task. It contains no `task.toml`, instruction copy, Harbor
bundle, grader, Oracle solution, hidden test bytes, source archive, dependency
wheel, or run result.

The immutable source/test image and its 171-item denominator are recoverable.
Publication is still blocked by public-spec version drift, an incomplete
offline build closure, and the absence of a candidate subprocess boundary.
No dataset, shared file, conversion-loop state, legacy artifact, or other task
directory is changed by this audit.

## Legacy Contract

- Task: `test_files/verifiers/`.
- `start.md`: 36,403 bytes; SHA-256
  `d811a2281c932452292c157109d1173eb1e1d2bd0605f08fdbb26a65cc5ff177`.
- Declared denominator: `171`; `test_case_count.txt` SHA-256
  `284de502c9847342318c17d474733ef468fbdbe252cddf6e4b4be0676706d9d0`.
- Commands: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests`; `test_commands.json`
  SHA-256
  `8e3fb7b291ad567ec29b6e5d4fe9d4c5493de0497fb8d9aaa77257977cd1e028`.
- Protected path: `tests`; `test_files.json` SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.

The count changed from `123` to `171` in commit
`781a1da1ee41fb8edb0bed22f586d69111610edf`; that commit changed only the count
file. `start.md` has not changed since initial task commit
`dbe72aad8828d83ecee8f623c96fc961b80654f6`.

## Immutable Verifier Image

The read-only conversion-loop record at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` identifies:

```text
ghcr.io/multimodal-art-projection/nl2repobench/verifiers@sha256:5ddcda0b6a45293828ebb24688a848d90abbb1f54e76b40fd3c1f53065f00e17
```

A registry request returned the same `Docker-Content-Digest` and raw-manifest
SHA-256. The Docker v2 manifest has 17 layers and config
`sha256:db070e22c21a64738825afa0a81fdc68b8e9d0a40c9939cf9705beebeeb48d1c`.
The config records `linux/amd64`, CPython `3.11.14`, working directory
`/workspace`, and creation time `2025-10-16T08:31:19.293040142Z`.

Relevant digest-verified layers are:

| Content | Compressed digest | Bytes |
| --- | --- | ---: |
| full Git checkout at `/project` | `sha256:00d638847bca0c6492dd117ce5cadfe5bb7c5baf3e78fa87c5c895907fc72d4c` | 3,990,894 |
| private `/workspace/tests` | `sha256:4e6ebed4f7d196860878235b816e92c3e6d322011dd28c9f0f293067ea3aa0d7` | 30,504 |
| `/workspace/pyproject.toml` | `sha256:77df30661c7b1058d5ed1a832b377fb552bb825f4588720d20330b2669d0c14f` | 1,813 |
| explicit test dependencies | `sha256:7a69c547677259c39775e93bb6136586774b48abaf3a6bb8533a521d109f800a` | 25,239,394 |
| editable project/dependencies | `sha256:be3e982ee75b89fde59fc618d49f56728784898cfedfb8acd7e90477dc21e13d` | 197,458,625 |
| historical pytest cache | `sha256:7e5f625b2202e304090aae7576691d75409b520d285bb65e39193b1b45e95416` | 946,521 |
| remove `/project` | `sha256:37cb0c8fd864339b33bfcd9386b085bb5c910930ba0574cbd552503ee8cbd422` | 77 |
| remove editable metadata/entry points | `sha256:a7cb2fcde28a054fccf5042b8e615f13c9afb9975c932718696ffb0e56ace86c` | 10,280 |

The final cleanup whiteouts remove `_verifiers.pth`, the `verifiers` dist-info,
and all five `vf-*` scripts. The final image therefore retains tests and
dependencies but not an importable reference implementation.

## Exact Upstream Provenance

The image checkout remote is `https://github.com/willccbb/verifiers`, which
GitHub redirects to `https://github.com/PrimeIntellect-ai/verifiers`. The
frozen revision is:

```text
dab14c0b1239882493c61d57b17f10b5a981293e
```

- Tree: `0864b6a76800a3523c5a64a2ca8ad7b8c5e51932`.
- Subject: `SGLang support for BadRequest prompt exception (#475)`.
- Commit time: `2025-10-15T22:19:11-07:00`.
- Package version: `0.1.5.post0`; the commit is 11 commits after tag
  `v0.1.5.post0` (`5c254e082fcc791eb48ca670ccb21142d33f5387`).

An independent fetch by full SHA returned the same commit and tree. The
unprefixed output of
`git archive --format=tar dab14c0b1239882493c61d57b17f10b5a981293e`
is 3,655,680 bytes with SHA-256
`d34ca81cba28954566cfc272963ca7ba6f07097fb7eb03d4746ba8e7ab828883`.

The frozen `LICENSE` is SPDX `MIT`, consistent with `pyproject.toml`. It is
1,069 bytes, Git blob `33e2703ad67592bb5a3a6e119ee14b05094aede8`, and
SHA-256 `361cdffc160c82544b228adf67e8422a147466dca5e50915bda962410d8b8a17`.
The image copy has only CRLF conversion: 1,089 bytes and SHA-256
`fe12301c96444a50e129368620e02c06ad2ef5702d954470bda5b722a11d3e35`.

## Source, Setup, And Test Overlays

The image checkout has 253 tracked paths and no untracked path. Git reports
216 modified text paths because of LF-to-CRLF conversion. After ignoring
end-of-line whitespace, the entire checkout differs only in `pyproject.toml`;
all implementation and test files match the frozen revision.

The image `pyproject.toml` is 4,583 bytes with SHA-256
`8b3f895f3fcb302247dfb4a679a8b12fe487afc91a3ad4e78a0efa9061a88cdc`.
The upstream file is 4,416 bytes, blob
`e29e4c2f6282340f2d4b64ca3a5195e5c9480c20`, and SHA-256
`2f7178de747c5573a69dc04fc00655350b8a7eebcf24dae19d07fcf2be7d5d15`.
After newline normalization, the build-only overlay replaces dynamic version
loading with `version = "0.1.5.post0"` and removes `readme = "README.md"`.
Its 590-byte unified diff has SHA-256
`f8bf3905c5cbbd31db2448dee001f245f47c089c8d08a2e28c0887660198854b`.
The separate `/workspace/pyproject.toml` is byte-identical to this overlay.

The private test tree contains 23 files totaling 180,314 bytes. A canonical
path/size/raw-SHA/upstream-blob manifest has SHA-256
`a70ad3bb11e9d9936e16b5f861265a2c99d3520ad59d9d88e28725d15ab8cba5`.
All 23 files match their paths in revision `dab14c0b...` after CRLF-to-LF
normalization, so there is no functional test overlay. The audited paths are:

```text
AGENTS.md                       test_environment_audio_modality.py
README.md                       test_environment_extra.py
__init__.py                     test_eval_cli.py
conftest.py                     test_imports.py
mock_client_guide.md            test_message_utils_audio.py
mock_openai_client.py           test_multiturn_env.py
test_env_group.py               test_parser.py
test_environment.py             test_rubric.py
test_rubric_group.py            test_singleturn_env.py
test_stateful_tool_env.py       test_think_parser.py
test_tool_env.py                test_tool_utils.py
test_xml_parser.py
```

Hidden bytes were inspected only under `/tmp` and are not included here.

## Denominator Evidence

The image-build cache file `.pytest_cache/v/cache/nodeids` is 13,991 bytes with
SHA-256 `93b15926f04ebf931d141dbdb68f55c84afab38314cb050b6c2fadd86eca522e`.
It contains 171 unique node IDs and has no `lastfailed` sibling. Independent
AST inspection also finds exactly 171 ordinary test functions, with per-module
counts identical to the cache:

```text
test_env_group.py=13                  test_parser.py=6
test_environment.py=19                test_rubric.py=23
test_environment_audio_modality.py=3  test_rubric_group.py=16
test_environment_extra.py=9           test_singleturn_env.py=16
test_eval_cli.py=2                     test_stateful_tool_env.py=2
test_imports.py=2                      test_think_parser.py=15
test_message_utils_audio.py=4          test_tool_env.py=3
test_multiturn_env.py=15               test_tool_utils.py=5
                                        test_xml_parser.py=18
```

No parametrization, collection hook, skip, skip-if, xfail, or `importorskip`
was found; the only pytest markers are `asyncio`. The image and declaration are
therefore numerically coherent at 171. This is static cache evidence, not a
fresh Harbor collection or JUnit gate.

## Dependency Closure Blocker

Metadata from the base and two install layers resolves 87 final distributions.
The sorted `name==version` manifest has SHA-256
`dc6ecaaae981031f043a420efe6658f6d151d288f0b144b3499a29aff2ca440f`.
Key versions include `datasets==4.2.0`, `numpy==2.3.4`, `openai==1.109.1`,
`openai-agents==0.3.3`, `pandas==2.3.3`, `prime-sandboxes==0.1.0`,
`pyarrow==21.0.0`, `pydantic==2.12.2`, `pytest==8.4.1`,
`pytest-asyncio==1.2.0`, `textarena==0.7.3`, `pip==24.0`,
`setuptools==79.0.1`, and `wheel==0.45.1`. Eighteen installed distributions
carry native wheels, including numpy, pandas, pyarrow, pydantic-core, rpds-py,
and aiohttp. They are transitively frozen by the image digest; no standalone
hash-locked wheelhouse exists.

Both upstream and overlaid `pyproject.toml` require:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

No `hatchling` module or distribution exists in the base, dependency,
editable-install, test-cache, or final layers. The image build used default pip
build isolation while network was available and discarded that temporary,
unpinned environment. A faithful no-network `pip install -e .` of the pinned
Oracle source cannot be reproduced from the final image. Adding a current
backend would invent a new dependency boundary.

The public instruction also requires `pip install -e .[all]`, but torch,
transformers, accelerate, deepspeed, trl, vllm, and liger-kernel are absent.
The legacy command installs only `-e .`, so this public requirement is neither
covered nor closed offline.

## Public Contract Drift

The frozen checkout is `0.1.5.post0` plus 11 commits and Python `3.11.14`.
The instruction declares Python `3.11.13`; its architecture ends at
`RELEASE_v0.1.3.post0.md` and omits later source/test modules. More importantly:

- it declares `async def evaluate` and `async def generate`, while frozen
  `Environment.evaluate` and `Environment.generate` are synchronous wrappers
  and the async method is named `a_generate`;
- it declares `RubricGroup.score_rollouts` with `def`, while the frozen method
  and tests use `async def`;
- frozen tests assert audio `modalities`, audio message cleanup,
  `sanitize_tool_calls`, and `vf-eval` sampling-argument precedence, while none
  of `audio`, `modalities`, `sanitize_tool_calls`, `vf-eval`, or
  `enable_thinking` appears in the instruction.

Changing only the count from 123 to 171 did not restore assertion-to-spec
traceability. Publishing this image would score behavior not derivable from the
public task.

## Candidate Boundary Blocker

Private `conftest.py` imports eight candidate classes at collection time.
Sixteen of 17 test modules also directly import candidate modules; the last
uses candidate-derived fixtures. The suite defines nine subclasses of
candidate environment classes, monkeypatches candidate CLI/module functions,
replaces candidate methods with `AsyncMock`, inspects `call_args`, and asserts
same-process object identity.

The image has no `candidate_client`, RPC protocol, subprocess runner, or
adapted tests. Merely running these tests in a separate verifier container
would still let trusted pytest import untrusted candidate code and execute
candidate build hooks. A compliant adapter requires a new serialization/RPC
contract and a newly frozen collection, which is outside this static
conversion.

## Decision And Reopen Conditions

Keep `verifiers` **blocked** and do not create a Harbor 1.4 bundle or dataset
entry. Reopen only after all of the following:

1. choose and review one public/source/test version boundary, fixing the
   sync/async, audio, CLI, and utility contracts;
2. approve the CRLF and packaging overlay or rebuild exact upstream inputs;
3. supply a hash-locked offline `hatchling` and native dependency closure;
4. adapt all assertions to a reviewed candidate subprocess contract;
5. freeze structured collection from that final adapter; and
6. in a later execution lane, pass three Oracle runs and empty, stub, forgery,
   and offline controls.

## Static Validation

Completed without Docker, Harbor, pytest, Oracle, or control execution:
legacy JSON/count parsing and hashing; read-only conversion-state inspection;
registry manifest/config/layer verification; temporary source/test/dependency
metadata extraction; exact-SHA Git fetch and archive/license hashing; normalized
source/setup/test comparison; AST/cache reconciliation; dependency/native-wheel
inventory; and direct-import/boundary inspection.
