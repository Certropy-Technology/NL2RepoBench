# `icecream` Static Provenance Audit

Status: **oracle-passed remediation; historical blocker retained below**. The
current task has a pinned source/instruction, private dependency/verifier/Oracle
bundles, a generic compiled `20/20` Oracle and empty/stub/forgery controls. The
legacy 40-case terminal/platform contract below is historical context only.

## Legacy Identity

- Task: `icecream`.
- Legacy test denominator: `40` (`test_files/icecream/test_case_count.txt`,
  SHA-256 `d59eced1ded07f84c145592f65bdf854358e009c5cd705f5215bf18697fed103`).
- Legacy commands: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests` (`test_commands.json`,
  SHA-256 `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`).
- Protected test path: `tests` (`test_files.json`, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Legacy public instruction SHA-256:
  `bec5562e635e5b1bb39d391207ac56ff39dc6032c596491354206670e1419afe`.

The legacy identity is preserved in this audit. Shared datasets, legacy files,
conversion-loop state, and other task directories were not edited.

## Verifier Image Revalidation

The conversion-loop record observed for this task reports an available
`linux/amd64` image:

`ghcr.io/multimodal-art-projection/nl2repobench/icecream@sha256:dde2856313cf8fb3bf009ae690aa06d23fd25a14fd52e12c7f5f801903942243`

The corresponding tag is `ghcr.io/multimodal-art-projection/nl2repobench/icecream:1.0`.
The state record is `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json`;
it records `status = "available"` and platform `linux/amd64`. A manifest-only
registry request returned all of the following:

- HTTP `Docker-Content-Digest`:
  `sha256:dde2856313cf8fb3bf009ae690aa06d23fd25a14fd52e12c7f5f801903942243`.
- Raw manifest SHA-256: the same digest.
- Media type: `application/vnd.docker.distribution.manifest.v2+json`.
- Config digest:
  `sha256:df2be703bbce1e6700843553d189c1b96fbed6fa6d85b93b13d1cac5e058336a`.
- Layer count: `8`.

This revalidation fetched only the registry token and manifest metadata. It did
not pull image layers and did not run Docker or Harbor. The earlier missing-tag
result is therefore treated as a transient infrastructure event, not as the
current image identity.

## Upstream Source Lock

The exact GitHub repository resolved from the image/source contents is:

`https://github.com/gruns/icecream`

The unique best matching upstream revision is:

`816e6c6bbac50f16fda8f801c658fe5ebcfd50bc`

This is the upstream commit `migrate setup.py to py3`, dated
`2025-02-26T12:00:28-08:00`, with tree ID
`de71548ff94dcc2698f26c8fea118b3d3608c795`. An exhaustive comparison of the
23 non-generated files in the extracted source copy against every reachable
upstream revision produced this unique maximum:

- revision `816e6c6b...`: 21 exact files out of 23;
- next-best reachable revision: 20 exact files out of 23;
- missing files: 0.

The deterministic unprefixed archive command was:

`git archive 816e6c6bbac50f16fda8f801c658fe5ebcfd50bc | sha256sum`

It produced 143,360 bytes and SHA-256
`cf563c74849444da66c3e3914346d1f89086da3565980876f037f542daf5367c`.

License evidence is the upstream `LICENSE.txt` at this revision. It is 1,054
bytes, Git blob `9809d45604ca225d691b2592a42e9db80d18353e`, and SHA-256
`ed22ae7c29d18ad952a4d75c0fbe95f99e89e170d3c83cc178d4519f5add4554`. Its
standard permission, warranty, and liability text establishes SPDX `MIT`.

## Image Fixture Comparison

The image fixture inventory was inspected by path, byte count, SHA-256, and
Python AST. Fixture bytes are intentionally not copied into this repository.

| Image path | Bytes | SHA-256 | AST test methods |
| --- | ---: | --- | ---: |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `tests/install_test_import.py` | 182 | `85088eee152b898b293df62927d56244301076d51ab3d98b87f174ea7a8f2b3e` | 0 |
| `tests/test_icecream.py` | 23,657 | `b240ad45a01ea57d74d3f95f0f9d8a580a14ea83f062f19c7f66f93309ba0925` | 38 |
| `tests/test_install.py` | 995 | `e35a0996735d156c105b44378c6959b95a397674a59f4ed8a4355b807ad950ad` | 2 |

The static image total is 40 test methods and therefore agrees numerically
with the legacy denominator. This is not a frozen pytest collection result.

At the resolved upstream revision, the image setup and two support files are
exact matches:

- `setup.py`: image SHA-256 `76c55a727c6df7863305917becab8c8593d75aa125e5ccd9d256ccebc1af6ae7`,
  upstream Git blob `078bb91c8179e5be0c898a6396f97883fd556a5d`;
- `tests/__init__.py`: exact empty file;
- `tests/install_test_import.py`: exact match.

The two test modules are not upstream blobs:

- `tests/test_icecream.py`: image Git blob
  `d55f02eb6699824c9346a04984c1051681e377cc`; upstream revision blob
  `394eef47dc45c379868d47002662db29bf5786a8` and SHA-256
  `f61e7e2c62ba90d0d24d2dea5e5623eb4f93412048e90e41b964512a7de6dd97`;
- `tests/test_install.py`: image Git blob
  `dfdc6b40ca53a6ba05dbf024510f5a8089802184`; upstream revision blob
  `6860fd781ae94ae7c59b3323eaf52281d1377388` and SHA-256
  `fe4f79b1c11a4f4b96abbb59eeb833fe971da0f242a3fe806a20d117c8ba5e2c`.

Neither image test blob occurs in any commit reachable from the inspected
upstream refs. The image-to-upstream diff is 63 additions/14 deletions for
`test_icecream.py` and 7 additions/2 deletions for `test_install.py`. The
observed overlay changes imports and relative-import behavior, adds a
multiline-string test, changes Windows path parsing, changes expected output
assertions, and relaxes a color assertion. These are behavioral test changes,
not harmless packaging metadata.

The upstream revision has 37 test methods in `test_icecream.py` and 2 in
`test_install.py`, for 39 total. The legacy denominator reaches 40 only with
the image overlay. No owner-approved immutable overlay manifest is recorded.

## Decision And Reopen Conditions

Keep `icecream` **blocked**. Creating a Harbor task from the current image
would present the modified image tests as tests from the pinned upstream
revision and would fabricate provenance. Creating a public fixture copy would
also violate the hidden-test boundary.

Before conversion can reopen, obtain one of the following:

1. An owner-approved immutable overlay manifest that declares the two modified
   test files, their source, license, and behavioral intent while preserving
   the legacy denominator of 40; or
2. A replacement verifier image whose 40-test fixture is byte-identical to a
   declared upstream revision.

The reopened task must additionally record a frozen runtime collection of 40,
the offline dependency closure and native-dependency result, a pinned agent
environment, and a separate candidate/verifier boundary before Oracle and
negative controls are run. None of those artifacts are claimed by this audit.

## Static Validation

Commands and outcomes:

- `git status --short --branch`: passed; no pre-existing user changes were
  modified.
- `python3 -m py_compile /tmp/icecream-image/setup.py /tmp/icecream-image/tests/*.py`:
  passed.
- Python AST inventory over the four image test files: passed; 40 test methods
  (38 + 2).
- Upstream reachable-ref/blob comparison and unique-maximum search: passed;
  revision `816e6c6b...` is the unique best source match and both image test
  blobs are absent from reachable history.
- `git archive <revision> | sha256sum` and `LICENSE.txt` hashing: passed; the
  archive and MIT evidence hashes above are reproducible.
- Manifest-only registry request for the recorded immutable image: passed; the
  returned content digest exactly matches the conversion-loop record.
- Docker/Harbor execution: not run by lane policy.
