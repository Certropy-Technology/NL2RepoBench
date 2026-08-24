# Flasky Provenance Audit

Status: `packaged` for task-local Harbor conversion. This is static evidence
only: no Docker build, Harbor run, pytest, Oracle, or control run was done.
Keep this task out of published datasets until those gates complete.

## Legacy Contract

- Legacy task: `test_files/flasky/`.
- Public instruction SHA-256: `ea3afc5869896c2ac86dee75b5c5e32f3642cb13a7160721127ae6bd4b4d46af`.
- Declared effective denominator: `34`; count file SHA-256:
  `86e50149658661312a9e0b35558d84f6c6d3da797f552a9657fe0558ca40cdef`.
- Command: `pytest --continue-on-collection-errors tests`.
- `test_commands.json` SHA-256:
  `20608bcd217e53ccad3bc43910ba91961259017b78c76266debf93c9d74f7a74`.
- `test_files.json` SHA-256:
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Both task-local instruction copies are byte-identical to legacy `start.md`.

## Verifier Image Lock

The loop assigned this immutable image and platform:

```text
ghcr.io/multimodal-art-projection/nl2repobench/flasky@sha256:dd7c1ab35038eb22f5637d7fb8d210d2a6bf080d65ca72c89b4ac31af3e0c342
linux/amd64
```

The registry manifest is Docker distribution manifest v2. Config digest:
`sha256:adbb6db2aef17de54935b5d8be2d6d2e823d3507baddb7d836ee2a8e1f2474c5`.
The config reports CPython `3.9.23`, working directory `/workspace`, and
Debian trixie base construction. The final image copies tests and requirements,
then installs `requirements/dev.txt` and pytest.

Relevant layers:

| Purpose | Manifest digest | Size |
| --- | --- | ---: |
| `COPY ./flasky-master/tests` | `sha256:433574e8d40f7f48f38f6c80c4c7052b886aac8634b10764440cb40d9282f071` | 4,221 |
| `COPY ./flasky-master/requirements.txt` | `sha256:2670d9a43cb688bb0e08a8464def97c010b5764ee65bd6e22f719eeafb1d44a7` | 235 |
| `COPY ./flasky-master/requirements` | `sha256:866b533922c154848b194b2962521d48dda813563a47f229911b9e76b5ebf39f` | 752 |
| dependency installation | `sha256:18494f2db9c96a24f1693b30ec2e85b000ecec48c693c282a1c4005fd87a78ab` | 17,567,480 |

Hidden tests remain in the pinned image. The task directory contains no hidden
test bytes; the verifier Dockerfile copies `/workspace/tests` into its private
fixture during image build.

## Source Lock

- Upstream: `https://github.com/miguelgrinberg/flasky`.
- Full revision: `3beedd640b9146b0bd65c8c2ecf402b01798bc33`.
- Subject: `Chapter 17: Traditional hosting (17g)`.
- Author date: `2017-07-18T07:55:57-07:00`.
- Commit date: `2025-04-06T19:52:44+01:00`.
- Git archive SHA-256: `d70278ce85aadc6127ef9f997c0410076488b744c01631a45499dc03bcd698d6`.
- Archive size: `194560` bytes.
- License: MIT, from `LICENSE` at this revision; size `1083` bytes and
  SHA-256 `b6bd501a2351ac4735d95f6904e67b7c9dd03568f9ed8d62b01c7d2c53aa3886`.
- `harbor/solution/solve.sh` resolves this full SHA and verifies the archive.

## Test Overlay And Counts

The image contains 35 AST-discoverable `test_*` methods. The legacy effective
count is 34 because `SeleniumTestCase.test_admin_home_page` is skipped when the
image has no Chrome/chromedriver: `setUp()` calls `skipTest`. This is static
count evidence, not fresh collection.

| Path | Bytes | Image SHA-256 | Upstream blob | Result |
| --- | ---: | --- | --- | --- |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | exact |
| `tests/test_api.py` | 10589 | `d45d5ffc8e05844cf2cdefc3c44710f79bdce461b1a474db879599173c1f07e8` | `666d3c707eb8248b86224f7bb38b839ea9a66609` | overlay |
| `tests/test_basics.py` | 540 | `f0c1ff49a91f2e677e421793fa0df86515e1905c56b65442183a5148cc8e7c1c` | `0fdf4983b03e755239aca1ef4a5dc29079b3850f` | overlay |
| `tests/test_client.py` | 2245 | `421fcbba7a1b8148f4cabf030298d3c2b9a4b5b1b18ad54463848d478bc383b3` | `bc6f5ca75312c4237ef3017a44daf2602026e564` | overlay |
| `tests/test_selenium.py` | 3194 | `95be8206326b64e524bb6216e291ba7dc597e64b4d99a70478633f0f5d0cdd28` | `f0eb00ffce369b5660dc3ee47f9649a8e037556e` | overlay |
| `tests/test_user_model.py` | 8356 | `7c0ead17f8b367e15be40b3cb9088c7d1fa196f870a4db572a4a31c2528ec76c` | `526abdbddf4353820f962f8237a410f5fcb1c5a1` | overlay |

The five non-identical image files are absent from all upstream Git history.
The unified overlay diff has SHA-256
`6ae85e2ecca1212921fb19cebf746eca3279bcc5472d6884e69fa0657c8c898c` and
5,381 bytes. It changes wildcard imports, stable relative URL assertions, one
raw regex string, and timezone-aware datetime comparisons only.

## Requirements Overlay

Root `requirements.txt`, `dev.txt`, `docker.txt`, `heroku.txt`, and `prod.txt`
match the pinned source. `requirements/common.txt` is a compatibility overlay:
`Flask-SQLAlchemy` changes `2.2` to `2.5.1`, and `SQLAlchemy` changes `1.1.11`
to `1.4.46`. The verifier uses the image closure and does not install candidate
dependencies; no standalone hash-locked offline wheelhouse is claimed.

## Static Validation And Recommendation

Completed without Docker, Harbor, or pytest: authoring-rule reads; legacy file
hashes; registry manifest/config/layer inspection; source clone and full-SHA
resolution; archive and license hash checks; test/requirements comparisons;
overlay-history search; AST inventory; TOML parsing; shell syntax; Python
grader syntax; catalog source validation; and instruction/hash checks.

Keep lifecycle at `packaged` for parent orchestration, but do not publish yet.
Collect in the final verifier image and confirm `35 collected, 1 skipped, 34
effective` with stable node IDs. Then run three independent Oracle trials and
empty, stub, forgery, and offline controls. Reclassify as an environment or
verifier blocker if collection differs or source installation fails.
