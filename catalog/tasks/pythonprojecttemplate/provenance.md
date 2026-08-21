# `pythonprojecttemplate` Static Conversion Audit

Status: **packaged; Oracle and controls pending**. This task uses the
immutable legacy verifier image as the source of its private test fixture.
The catalog contains no hidden test bytes, no Oracle output, and no Docker
run artifacts.

## Legacy contract

- Legacy directory: `test_files/pythonprojecttemplate/`.
- Declared denominator: `36`; `test_case_count.txt` SHA-256
  `76a50887d8f1c2e9301755428990ad81479ee21c25b43215cf524541e0503269`.
- Commands: `pip install -e .`, then `pytest --continue-on-collection-errors tests`;
  `test_commands.json` SHA-256
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected path: `tests`; `test_files.json` SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public instruction SHA-256:
  `a0047c55aad89b5bb62223e44a9e35d480af2d63a0d107ed615acf4e6dc5781c`.

## Immutable verifier image

- Image reference:
  `ghcr.io/multimodal-art-projection/nl2repobench/pythonprojecttemplate@sha256:a5623b41263e82ee18f602b1cb5b2d511720dfcfd8c8db26d07ebbef97eb8f71`.
- Registry platform: `linux/amd64`; image config digest:
  `sha256:9d57fb8deff180b0b97c7424d249bb888e7d618a46699c7a00ec902a38d8874b`.
- Config records CPython `3.10.18`, working directory `/workspace`, and
  image creation time `2025-09-10T09:00:49.667952896Z`.
- Relevant immutable layers (manifest digest, compressed bytes):

  | purpose | digest | bytes |
  | --- | --- | ---: |
  | `COPY ./tests /workspace/tests` | `sha256:7929b2554ae1f530751c3e90afaca5fe484760b7178b72ccc9555c8cb4cdf9a7` | 4513 |
  | `COPY ./pyproject.toml /workspace/` | `sha256:8f3912f7a2c8bafce47ffc12c237801b009c56898531fb80d74f6e308b08c0b2` | 2515 |
  | `COPY ./ /project/` source overlay | `sha256:29def251875e08aae7b79b2a2a897b5494ba206322b42c87029db4d28bc1cf2a` | 1049379 |
  | `pip install /project` | `sha256:1ea7209ed3ce25f3a6472cf3ef624750ef1fe03bb9063c6d0455adcd7a25e315` | 40770077 |
  | `pip install pytest` | `sha256:5a7de648732d4b6714a719d593e3881342085b9a7e0bd96d5cf910b2dbc84525` | 5237895 |
  | successful-build pytest cache | `sha256:5639cf86fa9471525e2426d966c4ec343f37e18ac5982a2d93a724ff6d64f04b` | 113406 |
  | removal of `/project` | `sha256:37cb0c8fd864339b33bfcd9386b085bb5c910930ba0574cbd552503ee8cbd422` | 77 |

The source checkout is not copied into the catalog. The verifier Dockerfile
copies only `/workspace/tests` from this immutable image into its own private
fixture at build time.

## Upstream source lock and license

- Repository: `https://github.com/franneck94/PythonProjectTemplate`.
- Full revision: `f1c116379eb485c17fb1b6cd3e2454712e4e0585` (`Update README.md`,
  2024-04-22T07:31:40+02:00). `git ls-remote` resolves this exact object on
  `refs/heads/master` at audit time.
- Deterministic archive command:
  `git archive --format=tar f1c116379eb485c17fb1b6cd3e2454712e4e0585`.
  Archive SHA-256: `c47d5545686d207763d3c21aafd6eb26b575dcc02ef62159fa21011ccde9413c`.
- `LICENSE` is MIT. It is 1059 bytes/19 lines, Git blob
  `0af99f98500da8cfb827272883bdd8568e92c513`, and file SHA-256
  `046b708c8fa8970b1676fea33c5d782839e22e82eb1806d6d9a26d7d75fcbcf2`.

The Oracle script fetches this full revision, not a tag or branch. The image
source checkout has the same revision in `.git/HEAD`.

## Test/setup/source overlays

The image build context was inspected from its immutable layers without
copying private bytes into this repository:

- The final `/workspace/tests` fixture has three source files plus three
  interpreter cache files. Source-file SHA-256 values are: `tests/__init__.py`
  = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, `tests/conftest.py` =
  `91fbdc972b466aefae09409240c6d1a61adf8f3b5a65965246892a39b4f8e2e5`, and
  `tests/test_vector.py` =
  `cf606fa7e9b1c93a80e08daf43412aa87fb80174ded649525a2c84080841e10f`.
- The image's `/workspace/pyproject.toml` overlay is byte-identical to the
  source checkout's `pyproject.toml` (raw SHA-256
  `549a81d84e69bd50efb9c79a1a922883d6076f96cfc2e6f68f65d64b0b37ff06`).
  Its runtime requirement is NumPy; the build backend is setuptools.
- The source overlay's Git checkout is clean at the locked revision except
  for one formatting-only edit to `tests/test_vector.py` (2 insertions, 1
  deletion; diff SHA-256
  `e5e64b4d3984fdee94940677d4bfcdb2d1f7abd2ea5c7b0247f25a97e83517f9`).
  The upstream tracked blob is `d83b0a28ce14fdd85bd3c549adaa8cec31d1cc02`;
  the image fixture and modified working-tree file are byte-identical.
- The build context also contained untracked `Dockerfile`,
  `PythonProjectTemplate.md`, `test_commands.json`, and `test_files.json`.
  Their raw SHA-256 values are respectively
  `473bacf96f423c03534433feadf3f1bcc9cb6babbee283255ff388f05c7d6a13`,
  `0b3154a7a5746662da6504b94ce42d5141af3e7119d6438e4f65761a53dda0d6`,
  `e522215b7d500e3f93f12b1b00a29e051dd3b68cefc9194ff44677946803c760`,
  and `d264871900f5c637eb23f6f07c49b9a82728b84ffa55e0b7c03f3c3bba2d6e96`.
  They are not used as hidden assertions; the copied source tree is removed
  before the final image, and the Oracle uses a clean upstream archive.
- The source copy also included ignored build products (`.coverage`,
  `.pytest_cache`, `reports/`, `__pycache__/`, `fastvector.egg-info/`, and
  `build/`). No functional source file other than the explicitly recorded
  test-formatting edit was changed.
- Image build history records `pip install /project`, then `pip install
  pytest`, and a successful `pytest /workspace/tests -v` layer. The resulting
  frozen cache contains 36 nodeids and no skip/xfail marker was found by the
  static AST inventory. The effective denominator therefore agrees with the
  legacy declaration: `36`.

## Dependency closure and candidate boundary

The immutable verifier image contains NumPy `2.2.6`, pytest `8.4.1`, and the
pytest runtime closure observed in the image (`exceptiongroup 1.3.0`,
`iniconfig 2.1.0`, `packaging 25.0`, `pluggy 1.6.0`, `Pygments 2.19.2`, and
`tomli 2.2.1`). The FastVector install metadata in the image declares only
NumPy runtime dependency markers, satisfied by NumPy 2.2.6 on Python 3.10.18.
The verifier runs with `network_mode = "no-network"` and does not resolve
candidate dependencies from PyPI.

The agent environment is a separate digest-pinned Python 3.10.18 image:
`python@sha256:e501e3982f1b1363dc3a010affe949eb55c3a058bc6614a095bb71d8203b2951`
(the `linux/amd64` child manifest for the official `python:3.10.18` image).
Its immutable image history includes `git`, and it contains no test fixture or
preinstalled FastVector checkout. The verifier image is the only consumer of
the private fixture. At test time it copies the submitted workspace, replaces
only the protected `tests` path with the fixture, and prepends candidate source
paths through a `.pth` file. The final reward and grading reports are written
by the grader under `/logs/verifier`.

This is a static packaging decision only. No Docker build, Oracle run,
pytest run, or candidate behavior execution was performed.
