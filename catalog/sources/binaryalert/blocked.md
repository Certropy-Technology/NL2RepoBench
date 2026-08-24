# `binaryalert` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. No Harbor task
descriptor, public instruction, Oracle bundle, verifier script, hidden test,
or binary fixture is included.

## Legacy Identity

- Legacy task: `test_files/binaryalert/`.
- Declared denominator: `77` (`test_case_count.txt`, SHA-256
  `a88a7902cb4ef697ba0b6759c50e8c10297ff58f942243de19b984841bfe1f73`).
- Declared test path: `tests` (`test_files.json`, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Legacy command file SHA-256:
  `6bbedac497ddfcade9e2dcfc2240e73391cefd560d5e8b2cc86b67863c90e79e`.
- Commands are exactly `set AWS_DEFAULT_REGION=us-east-1` and
  `pytest --continue-on-collection-errors tests`.
- Public legacy instruction SHA-256:
  `7d9463d69157d6773422cd61db55b89bbef981cb880191d26713d3c78756d0cb`.

Static AST inventory of the image test tree finds 77 test functions, matching
the upstream base tree: `cli/config_test.py` 15, `cli/enqueue_task_test.py` 2,
`cli/manager_test.py` 20, `lambda_functions/analyzer/analyzer_aws_lib_test.py`
7, `file_hash_test.py` 4, `main_test.py` 3, `yara_analyzer_test.py` 11,
`lambda_functions/build_test.py` 1, `lambda_functions/downloader/main_test.py`
1, `rules/clone_rules_test.py` 5, `compile_rules_test.py` 4, and
`eicar_rule_test.py` 4. Pytest collection was not run in this static-only
lane.

## Upstream Source

The repository resolves to `https://github.com/airbnb/binaryalert`. GitHub
identifies its license as `Apache-2.0`; the pinned revision's `LICENSE` is the
standard Apache License 2.0 text.

- Candidate revision:
  `a9c0f06affc35e1f8e45bb77f835b92350c68a0b`.
- Revision: `Upgrades terraform modules to Terraform 0.12.9`
  (`v1.2.0-8-ga9c0f06`).
- Archive command: `git -C /tmp/binaryalert-source-static archive
  --format=tar a9c0f06 | sha256sum`.
- Unprefixed archive SHA-256:
  `b2041bbabf5432941bc46def3ff033185ec64dc13f3a80b08e734e4fb18e1bf0`.
- Archive size: `9134080` bytes.
- `LICENSE`: `11357` bytes, SHA-256
  `b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1`.

This is the nearest clean upstream base, not an exact source lock for the
frozen image: the image contains an unapproved overlay that no upstream commit
can account for.

## Immutable Verifier Image

The conversion-loop record supplies this immutable linux/amd64 reference:

`ghcr.io/multimodal-art-projection/nl2repobench/binaryalert@sha256:63d558916bbd258b98507ad99bcab5022dfc38f92e1b39eb66e3cb265f4dd392`

Registry evidence collected without starting Docker:

- Manifest JSON SHA-256:
  `63d558916bbd258b98507ad99bcab5022dfc38f92e1b39eb66e3cb265f4dd392`.
- Config digest:
  `sha256:628adc219f6bca88134480dc65c4d24c896a7750cac8c1b562955909fd036c8e`.
- Config reports Python `3.7.9`, pip `21.0.1`, `/workspace`, and
  `AWS_DEFAULT_REGION=us-east-1`.
- Test/fixture layer:
  `sha256:c2932b363ed818c0a3bdc4d6b162c538cdb10f7b4d2cbe44e38bbd6a1a84e84e`
  (`190808` compressed bytes).
- Requirements layer:
  `sha256:fe0f1125dc57db15e188b60add032030eb0ea91db94ae6eb92a7a794c8cee471`
  (`738` compressed bytes).
- Source layer:
  `sha256:f212e978e40a136cb66ca919828dbf47f99c04175078202382e4971e8bfdfd5e`
  (`8787577` compressed bytes).
- Source deletion layer:
  `sha256:78fa379438e97c4f22c45e4b3a68650fa0922eb5317988e51350c45f5d63840a`
  (`81` compressed bytes).

Image history copies tests and requirements to `/workspace`, copies a source
tree to `/binaryalert`, installs requirements from
`https://pypi.tuna.tsinghua.edu.cn/simple/`, sets the AWS region, upgrades
`yara-python`, runs plain `pytest`, and removes `/binaryalert`. This setup does
not match the legacy command contract: it adds an install step and omits
`--continue-on-collection-errors tests`.

## Frozen versus Upstream

The image workspace has 27 non-cache test/fixture files totaling 171703 bytes.
Twenty-four match upstream test blobs at the candidate revision; three do not:

| Image path | Image SHA-256 | Upstream SHA-256 | Overlay |
| --- | --- | --- | --- |
| `lambda_functions/analyzer/main_test.py` | `3fcced8e67eb59f99d938aed7525be8467da1f6716f64d7aad2a96e6c1750632` | `d51e1fcb42c6d0472ea42169efcc2c58fdcf363d630c7590eee8917f00eaafac` | Byte-write mock and hard-coded/recomputed expected values. |
| `rules/clone_rules_test.py` | `9a9abaf946fe72a65ca88e8a106764bafca7f21205ab1b54a99592ffef2dbb4b` | `15be219e0f25038cb2ad195b5939f4b3ea41843c6f618043e758a40c75cac0e7` | `os.path.join` path assertions. |
| `rules/compile_rules_test.py` | `c73af292bf4da3c5217e3a0506fc3600b5acafa7fd7269942c8d1a9575ec9b05` | `b5bf7cbe012b9b952d15716287425c13109e7fe3d735d5258ad70c0bab96958a` | Removes one assertion. |

The source layer contains 181 tracked upstream paths: 175 match and six are
modified. No `git log --all` revision contains these image blobs:

| Tracked source path | Image SHA-256 | Upstream SHA-256 |
| --- | --- | --- |
| `cli/exceptions.py` | `84a33fabc05408a2f22c3b1968d40d10252b3ac93e6a5433c0f38695cdc468b5` | `1fe8e6138ae70a2bb2bd0d43123efec64ee225b93a9087981b861b1205519d20` |
| `lambda_functions/analyzer/yara_analyzer.py` | `4d40c63786c24775a30e085d8fea6484b3a248332bb85d7b021b9005be7d038b` | `2c1117cdd9651f7f256db641d810258e7ba0178c71e3818f33cc8c1a8a741cd9` |
| `requirements.txt` | `aba5d034a09f9bfc9e87d07f304dc8c35a9f260e6522cb7dac4967944b0eb792` | `fda18e6b887d4bd6d2b51e3353e024d990b472901204aa5e2f5853b58c8ad028` |
| `tests/lambda_functions/analyzer/main_test.py` | `3fcced8e67eb59f99d938aed7525be8467da1f6716f64d7aad2a96e6c1750632` | `d51e1fcb42c6d0472ea42169efcc2c58fdcf363d630c7590eee8917f00eaafac` |
| `tests/rules/clone_rules_test.py` | `9a9abaf946fe72a65ca88e8a106764bafca7f21205ab1b54a99592ffef2dbb4b` | `15be219e0f25038cb2ad195b5939f4b3ea41843c6f618043e758a40c75cac0e7` |
| `tests/rules/compile_rules_test.py` | `c73af292bf4da3c5217e3a0506fc3600b5acafa7fd7269942c8d1a9575ec9b05` | `b5bf7cbe012b9b952d15716287425c13109e7fe3d735d5258ad70c0bab96958a` |

The image's source manifest lists 23 test paths and the workspace contains
four binary fixtures. Both remain inside the pinned image evidence and are not
copied into this patch.

## AWS, Native, and Offline Risks

- Unit-test modules patch or fake boto3/cbapi. `live_test.py` contains real S3,
  Lambda, and DynamoDB calls, but no functions there are pytest tests. Offline
  collection is plausible but unproven without final-image collection.
- `lambda_functions/build_test.py` expects native artifacts such as
  `libarchive.so.13`, `libyara.so.3`, `yextend`, `upx`, and shared libraries.
  No standalone offline wheelhouse or native dependency lock is recorded.
- Image history upgrades `yara-python` after `yara-python==3.8.0`; its
  requirements overlay comments out upstream pins and uses a public mirror.
  This is not a reproducible offline dependency lock.
- Tests directly import and patch candidate modules in one process. No
  task-specific `candidate_client` adapter or separate-process contract is
  present, so the required candidate/verifier boundary is unproven.

## Decision

Keep `binaryalert` **blocked**. The denominator is numerically consistent with
the AST inventory, but provenance and verifier boundaries are not coherent:

1. Three test files and three source/dependency files are unapproved overlays
   with no matching upstream commit.
2. Image setup uses a different collection command and networked, partly
   unpinned dependency installation.
3. AWS/native/offline behavior has no final-image collection evidence.
4. Direct-import tests have no separate candidate boundary adapter.

Do not create `task.toml`, `instruction.md`, Harbor Dockerfiles, private test
references, or an Oracle solve script. To reopen, obtain an owner-approved
overlay manifest or rebuild from exact upstream test blobs, freeze collection
with the legacy command, provide offline dependency/native locks, implement a
task-specific candidate boundary, and run the three Oracle and control gates.

## Static Validation

No Docker, Harbor, pytest, Oracle, or control run was executed. Static checks:

- Resolved the GitHub repository, full revision, GitHub SPDX license evidence,
  `LICENSE` hash, and unprefixed `git archive` hash.
- Resolved the conversion-loop image record and inspected its manifest, config,
  relevant layer digests, history, and workspace inventory.
- Compared every non-cache image test file and all 181 source paths; checked
  path histories for all six image hashes and found no matching commit.
- Parsed extracted Python with `ast.parse` and counted 77 test functions.
- Checked the extracted shell file with `bash -n` without running it.
- `git diff --check` passed for this patch; no files are staged.

Shared scripts, datasets, loop state, and legacy task files were not edited.
