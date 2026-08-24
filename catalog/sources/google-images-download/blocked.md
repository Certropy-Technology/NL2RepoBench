# `google-images-download` Static Provenance Audit

Status: **blocked**. This audit is paired with a parseable descriptor and
hash-bound production evidence. It contains no Harbor bundle, Oracle
solution, verifier script, grader, or hidden test bytes; no runtime exists at
`catalog/tasks/google-images-download/`.

## Legacy Contract

- Task identity: `test_files/google-images-download/`.
- Declared denominator: `30` (`test_case_count.txt`, SHA-256
  `624b60c58c9d8bfb6ff1886c2fd605d2adeb6ea4da576068201b6c6958ce93f4`).
- Commands: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests` (`test_commands.json`,
  SHA-256 `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`).
- Protected path: `tests` (`test_files.json`, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Public legacy instruction: 21,097 bytes, SHA-256
  `741982efaff9e00e90852078ddecd031d8e1c793f2bb193c921eb3c0f182695f`.

Static AST inventory of the image's three test files found exactly 30 ordinary
test functions: 17 methods in `test_advanced_features.py`, 12 functions in
`test_google_images_download.py`, and one in `test_sample.py`. No
`pytest.mark.parametrize`, skip/xfail marker, or `pytest_generate_tests` hook
was found. This agrees numerically with the legacy denominator but is not a
structured pytest collection record.

The hidden test files were not copied here. Their immutable image hashes are:

| Image path | Bytes | SHA-256 |
| --- | ---: | --- |
| `/workspace/test_advanced_features.py` | 14,237 | `8b66a7ce25f06632767c14ee5fe42e78167b6f00fde6e4ba1770b73b278988d1` |
| `/workspace/test_google_images_download.py` | 12,679 | `1f0378ed7630e98abcbe3c08b9c88cbbf27c198a48dd1506aa4738a502ed7d05` |
| `/workspace/test_sample.py` | 102 | `8b56f5a29342d3cc320af28fc7df6045734d24bab2f326b6eb1247086f115dba` |

## Pinned Verifier Image

The conversion-loop record pins this immutable `linux/amd64` reference:

`ghcr.io/multimodal-art-projection/nl2repobench/google-images-download@sha256:c09075194b5c1d42d719f5f25f00543507c96d6be1a5711314d0db77659d052c`

The requested tag is
`ghcr.io/multimodal-art-projection/nl2repobench/google-images-download:1.0`;
registry inspection returned the same manifest digest. Static image evidence:

- Config digest:
  `sha256:9d9a1dda2a11ba578660dc306898c584552729183d2feb1cc7ca4802e30fffbb`.
- Created: `2025-08-27T12:09:01.795530337Z`; runtime CPython `3.10.11`,
  `linux/amd64`; working directory `/workspace`.
- Test-copy layer: `sha256:68c05a2f7907d38a4ec8fec3dff29af2521b05c00f520093cd145732ad8eadc1`.
- Setup-copy layer: `sha256:05dce3040fc6a99305788bb0702c8a20b0dcd5d79c720191e0a22356c438b723`.
- Requirements-copy layer: `sha256:dff5b896f64128eb9fc8e4fedcb4874b39333fc6cc2ad96b4d5ed5b4b3de4b04`.
- Source-copy layer: `sha256:0de92b709d24a165a9b99755ba5787178fffb6ac33ef5136f8b55af09487fff8`.

Image history records installation from
`https://pypi.tuna.tsinghua.edu.cn/simple/`, an editable install, and a
build-time `pytest`. It also installs `json5==0.9.14`, `argparse==1.4.0`,
`Pillow==10.0.0`, `opencv-python==4.8.0.76`, `pytest==8.4.0`, and
`pytest-cov==4.1.0`; copied `requirements.txt` contains `selenium`. History is
provenance only, not a fresh collection, Oracle, or offline-control result.

## Upstream Source And License

The best immutable baseline found by comparing image source paths against all
170 reachable upstream commits is:

- Repository: `https://github.com/hardikvasa/google-images-download`.
- Full revision: `0d2bf8f17b5a8806d90df7258e7a172aa0cb7963` (2019-05-21,
  `minor changes after merging #213`).
- Revision tree: `4583dfdba02d3e54bbbc54751561c58212d76610`.
- Reachability: `master`; contained by tags `v3.0.0` and `v3.0.1` in the
  inspected clone.
- Archive command:
  `git archive --format=tar 0d2bf8f17b5a8806d90df7258e7a172aa0cb7963`.
- Archive size/hash: 194,560 bytes,
  `9c5932606c3e76509c45c908f5fb2b3c81ef65e0eb6068e330980ab099143a62`.

`Licence.txt` contains MIT text. Evidence: Git blob
`2aee473803a16d286513ceedea6c170a333278a8`, file SHA-256
`54ee19366219d75d235b1a54cd09afb4a511b8297167269bca715ced3d850ebc`.
GitHub's license endpoint identifies `Licence.txt` but returns no SPDX id;
`MIT` is therefore text-based SPDX mapping, not an API SPDX assertion.

## Overlay And Boundary Findings

At the selected revision, all 28 upstream-tracked paths are present in the
image source, but only 25 are byte-identical. The three tracked overlays are:

- `setup.py`: image comments out README long-description loading.
- `google_images_download/google_images_download.py`: image changes network
  failures to exceptions, adds filename sanitization, changes Selenium and
  URL-parameter behavior, and adds modern Google-page parsing. Its image blob
  is absent from inspected upstream history.
- `tests/test_google_images_download.py`: image expands the historical test
  with network, URL-building, filesystem, and integration checks and changes
  the original download assertion.

The image also contains `tests/test_advanced_features.py`, absent from every
inspected upstream commit, plus generated build/egg-info/cache content. The
source-layer tests and workspace tests are byte-identical to each other; that
does not make the overlay an upstream revision.

The task cannot pass the requested offline-boundary audit:

1. Tests call `similar_images()` for example URLs, reverse-image search, and
   `download_page()` for Google and invalid URLs. One case patches
   `urllib.request.urlopen`, but the rest encode live network/failure behavior.
   No fresh no-network collection or result is recorded.
2. The public specification advertises Selenium/Chrome automation, but the
   pinned image does not record a Chrome binary, chromedriver version, or
   native/browser dependency closure. `selenium` alone is not an offline lock.
3. Legacy tests directly import the candidate. There is no separate verifier
   candidate-client contract proving process isolation, hidden-test
   immutability, or resistance to candidate-written reward artifacts.

The denominator is numerically consistent but not sufficient to publish.
Source/test overlays, unresolved browser/native closure, and unproven
offline/candidate boundary are blockers.

## Decision

Keep `google-images-download` **blocked**. Do not create `task.toml`,
`instruction.md`, Harbor environment, Oracle script, verifier script, or
grader. Preserve the legacy task identity and declared count of 30; do not
change the denominator to disguise the overlay.

To reopen, record an owner-approved immutable overlay manifest (or rebuild
from exact upstream files), lock Selenium/Chrome/native dependencies, adapt
tests to a separate candidate subprocess boundary, collect in the final
no-network verifier image, and run three Oracle gates plus empty, stub,
forgery, and offline controls.

## Static Validation

- Passed: immutable registry manifest/config and layer inspection; image file
  extraction; upstream clone/ref enumeration; full-SHA reachability; Git tree
  and archive hashing; license text/hash inspection; exhaustive path compare;
  and AST inventory.
- Passed: AST parse of all frozen tests, exactly 30 ordinary functions, with
  no parametrization or skip/xfail hooks.
- Not run by design: Docker, Harbor, pytest execution, Oracle, controls, or
  network-dependent candidate behavior.
- Not applicable: catalog source validation, TOML parsing, and shell syntax,
  because no `task.toml` or Harbor shell files were created.
- The task-local patch is limited to this file; `git diff --check` must remain
  clean and no files are staged.
