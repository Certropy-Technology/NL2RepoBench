# `requests-html` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. It contains no
`task.toml`, public instruction projection, Harbor bundle, Oracle solution,
verifier script, grader, or hidden test bytes. No legacy artifact, dataset
file, conversion-loop state, or other task directory was changed.

The legacy denominator is numerically recoverable, and an upstream revision,
license, archive, and immutable verifier image can be identified. Publication
is nevertheless blocked by an undocumented functional source/test overlay,
live-network assertions, an unclosed dependency/native-browser lock, and the
lack of a reviewed separate candidate boundary.

## Legacy contract

| Artifact | Bytes | SHA-256 | Parsed value |
| --- | ---: | --- | --- |
| `test_files/requests-html/start.md` | 21,974 | `d0962405e29d987a413550fdf22d2b3e14d7213200c465483c46eae970ce17a4` | Public repository-generation instruction |
| `test_files/requests-html/test_case_count.txt` | 2 | `3d914f9348c9cc0ff8a79716700b9fcd4d2f3e711608004eb8f138bcba7f14d9` | Declared denominator `41` |
| `test_files/requests-html/test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; `pytest --continue-on-collection-errors tests` |
| `test_files/requests-html/test_files.json` | 9 | `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The command and path manifests parse successfully. The legacy pytest command
does not exclude the `internet` marker.

## Immutable verifier image

The conversion-loop record assigns this available `linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/requests-html@sha256:1bf7a654410b6ca33899bf2a37fabed66113f97d5f36c8e4d3374dd3cb09b45d
```

Read-only registry metadata returned the same manifest digest. The config
digest is `sha256:b8efce896fb4724e502910b62b7033f6759674a160c9ed66a7e1e66fd81ef6cb`;
the image is `linux/amd64`, uses CPython `3.12.4`, and was created at
`2025-09-04T09:51:42.606111924Z`. Relevant immutable layer evidence is:

| Image content/history | Compressed layer digest | Bytes |
| --- | --- | ---: |
| protected tests copied to `/workspace/tests` | `sha256:4f98bdb659135224227f10d9ea4e95e3e3c0e93c21824e32ab4d95bccfe6b210` | 11,941 |
| `setup.py` copied to `/workspace` | `sha256:99f572892c8c757676e281b09ff53f0821fc8e7806c0c9b7a3721677eae63c20` | 1,611 |
| source checkout copied to `/requests-html` | `sha256:1727142829ebd9831b4b0a8775ab0eb4ab2a7764ef372c8b62eccaae0032d610` | 5,587,576 |
| runtime dependency installation | `sha256:d54d2de707ba097e66cf4cdf74742e784d024654f16b2a94229585e41cd83c41` | 20,391,741 |
| development/test dependency installation | `sha256:60ab3748eb129b53a5ad3678e745d927a26f56cbdb069786a013603a71a68e78` | 80,757,432 |
| Chromium installation | `sha256:ae55fc2350fbdee3c8229606db00b6cdb09a5d741509050d2285152207330466` | 231,842,243 |
| historical `pytest` layer | `sha256:ef2d1b3f85130cc2892c92f5cae8561f77ae4bd02b1662ee3453ca28a732019a` | 271,214 |

The image history records `chromium` version
`139.0.7258.154-1~deb12u1`, `PYPPETEER_EXECUTABLE_PATH=/usr/bin/chromium`,
`PYPPETEER_SKIP_CHROMIUM_DOWNLOAD=true`, a historical `pytest` run, and then
removal of the source checkout. The historical run did not preserve a JUnit
or other structured collection artifact.

## Upstream source and license lock

The strongest exact GitHub source candidate is:

- Repository: `https://github.com/psf/requests-html`.
- Full revision: `075ac162dc62fc532037df0d98954ab840a97516` (reachable from
  `origin/master`, dated `2023-04-03T19:09:56+02:00`).
- Revision tree: `4b4ca29c28d798e031518d5a183e74f62d31f524`.
- Deterministic command: `git archive --format=tar 075ac162dc62fc532037df0d98954ab840a97516`.
- Unprefixed archive size/hash: `3,450,880` bytes,
  `8531f3f942267b8841c551d436e00c550b22566c815553cc7c39fac356756aca`.
- License: MIT, from `LICENSE` at that revision; Git blob
  `00bf847d1b55d4e63b5a3f73df3188ca9f8dad21`, 1,076 bytes,
  SHA-256 `6ae105e698fb5fa6dfa91c79a891a905c089b25efb9a162ca09e6f331d82afe4`.

This is a usable provenance candidate, but the image workspace is not a
byte-identical checkout of it after normalizing line endings.

## Source and test overlays

The source layer contains a Git checkout whose `HEAD` is the revision above,
but its working tree has meaningful files that are not upstream blobs. Image
and upstream hashes below use raw image bytes and normalized upstream/image
text where noted:

| Path | Image SHA-256 | Normalized image SHA-256 | Upstream SHA-256 | Finding |
| --- | --- | --- | --- | --- |
| `requests_html.py` | `b9eec20c5e89b6bc5fd5cd65712a88d66ab3266914e5382adc5f92878f18019a` | `b4a95de8b64d91447dc65c8dad8ca228ccd1c3aa98e990e48000266613c9d483` | `e51e2925de9357bfa6a1cd2c973c90580f9800f306a3e54106f686c000e64dbd` | **Functional overlay**: adds `os` and passes `PYPPETEER_EXECUTABLE_PATH` as pyppeteer `executablePath`. |
| `setup.py` | `47bca897eb5da037ebd21c8ca13d676e7f50c0c8a5b16037354164154c4fbe0f` | `fb7900b5a52a88a7b41d24d763651c371eb13e0fd7b7497652983c7890f8084e` | `c722056f615f7576639fca1c9803a38fe624eb92041ba4917a4b044ce03d3c08` | **Packaging overlay**: adds `lxml_html_clean` and comments out README long-description loading. |
| `tests/test_internet.py` | `f407d1add4c3113f60c6eebbf2011bca712ec8d7d048f7682145419dd80ba94f` | `46cc2f7fdf9dd83a8c22ac2cf5001796380832323b9cccbbdcd469c9e6ceacfe` | `5b32bdaf4d5acd33035669a18ec028e0ab069b265f9f472611938a8a92d4a66b` | **Test overlay**: removes two URLs, adds a timeout, and changes async fixture parameters. |
| `tests/test_requests_html.py` | `685db5eea055a81ba4932a2cea518ad1bd0e2c7431a828f400362026394a4534` | `deaac85770c8b141e0ad47552a12d0a8ab627fa174cef003371c19a545b784bd` | `6de425e537a11975b3a962c7271cd29390869f93dfff2982b5a34cb93c9254fd` | **Test overlay**: wildcard imports, a `pathlib` file URL, and a redesigned async fixture. |
| `tests/python.html` | `103f5cd252a4c0e5d74e44196cf2e889dca61ccf5d6b2847a007705c3807572a` | — | `103f5cd252a4c0e5d74e44196cf2e889dca61ccf5d6b2847a007705c3807572a` | Exact upstream fixture. |

The image also has line-ending-only changes across other tracked text files
and a generated `test.log`; those are not treated as behavioral evidence.
No owner-approved immutable overlay manifest, patch artifact, or overlay
license/source record was found in the repository or conversion-loop record.
Assigning the functional source and modified tests to the upstream commit
would fabricate provenance.

## Denominator audit

The static node shape agrees with the legacy declaration:

- `tests/test_requests_html.py`: 24 test functions plus one seven-case
  parametrization = 30 nodes.
- `tests/test_internet.py`: two five-URL parametrizations plus one ordinary
  test = 11 nodes.
- Image `.pytest_cache/v/cache/nodeids` contains 41 node IDs.
- No skip/xfail marker or custom collection hook was found.

Thus `41` is numerically coherent, but this is static/cache evidence only;
there is no fresh final-verifier collection/JUnit record. The denominator is
not the primary blocker.

## Publication blockers

### 1. Live network is part of the frozen test contract

The protected tests still request these external pages in both synchronous
and asynchronous pagination tests:

```text
https://xkcd.com/1957/
https://github.com/psf/requests-html/issues
https://discord.com/category/engineering
https://www.frontiersin.org/
https://azure.microsoft.com/en-us
```

`test_async_run` also fetches all five URLs. The legacy command does not select
`not internet`, and the tests contain no local replacement or deterministic
mock for these calls. A no-network verifier cannot execute the declared
suite, while a public-network verifier makes the score depend on remote sites.
The image's `test.log` is only a historical Windows run of 11 internet nodes,
not an offline or reproducible gate.

### 2. Dependency and native-browser closure is not frozen

The source `Pipfile.lock` pins an older closure (for example
`requests==2.28.2`, `pyquery==2.0.0`, `pyppeteer==1.0.2`, `lxml==4.9.2`, and
`w3lib==2.1.1`), while the image installs materially different versions,
including `requests==2.32.5`, `pyquery==2.0.1`, `pyppeteer==2.0.0`,
`lxml==6.0.1`, `lxml_html_clean==0.4.2`, `w3lib==2.3.1`, and
`pytest==8.4.1`. The image contains Chromium and its Debian runtime
libraries, but no standalone hash-locked wheelhouse, complete dependency
artifact, or independently versioned native/browser lock is recorded for a
new no-network Harbor verifier. The setup overlay also adds a dependency not
present in the upstream setup contract.

### 3. The legacy suite crosses the trusted candidate boundary

The tests import `requests_html` directly in the pytest process and exercise
candidate-created browser/session state. A simple editable install or
`sys.path` prepend would execute candidate imports in trusted pytest and let
candidate packaging/import behavior reach collection and reporting. No
requests-html-specific candidate-client/RPC adapter or reviewed isolated
report protocol exists in this repository. This does not satisfy the
production separate-verifier requirement without an unapproved verifier
redesign.

## Decision and reopen conditions

Keep `requests-html` **blocked**. Do not create a Harbor 1.4 bundle from the
current evidence, and do not change the denominator to hide the network or
overlay problems.

To reopen, obtain all of the following:

1. An owner-approved immutable manifest for the functional `requests_html.py`
and setup/test overlays, including source, license, purpose, and expected
behavior, or rebuild the verifier image from exact upstream files.
2. A deterministic offline test contract: replace the live URLs with an
approved frozen fixture/mocking boundary or explicitly version a new task
whose metric permits network and records that dependency.
3. A complete hash-locked Python and Chromium/native dependency artifact for
the final verifier image.
4. A reviewed candidate-client/subprocess adapter and trusted grader boundary
that prevents candidate imports, pytest plugins, test replacement, and forged
JUnit/reward files from affecting grading.
5. A fresh final-image collection record, followed by three valid Oracle runs
and empty, stub, forgery, and offline controls in a later execution lane.

## Static validation

Completed without Docker, Harbor, pytest, Oracle, or negative controls:

- Read `AGENTS.md` and `CONTRIBUTING.md` and audited all four legacy files.
- Read the conversion-loop image record and verified the immutable registry
  manifest/config and relevant layer digests via read-only metadata requests.
- Inspected only temporary image layers for path inventories, source/test
  hashes, Git metadata, package metadata, Chromium package version, and image
  history; no hidden test bytes were copied into the repository.
- Resolved the exact upstream full SHA, tree, MIT license evidence, and
  deterministic archive hash.
- Compared image source/setup/tests with the upstream tree and identified the
  functional and behavioral overlays.
- Parsed the frozen test AST and node-id cache; confirmed 41 static nodes and
  no skip/xfail/custom collection hook.
- Checked the task-scoped worktree diff and whitespace after writing this
  audit. No files are staged.

No task-local Harbor files were generated because the provenance, offline
network, dependency/native closure, and candidate-boundary gates are blocked.
