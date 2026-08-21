# GraphNeuralNetwork Provenance Audit

Status: `packaged`; Oracle and negative controls remain pending the parent. This audit records the immutable image evidence without copying its tests, model file, or Cora fixtures into the public task tree.

## Legacy Contract
- Task identity: `test_files/graphneuralnetwork/`.
- Declared denominator: `4` (`test_case_count.txt` SHA-256 `4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a`).
- Legacy commands: `pip install -e .`; `pytest --continue-on-collection-errors tests` (commands SHA-256 `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`).
- Protected legacy test path: `tests` (`test_files.json` SHA-256 `af7f0b2bd342822f2a8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Legacy instruction SHA-256: `0445dbf713ce9499b3681935b9f4fb811efea3127e1a0d8a1f88773d2ab1e685`.

## Immutable Verifier Image
- Image: `ghcr.io/multimodal-art-projection/nl2repobench/graphneuralnetwork@sha256:6388582535fd9c56af5a69eef057a136c3ec4ae54ae26156b6db843286d62152`.
- Registry platform: `linux/amd64`; image config digest: `sha256:4bf78db2c2164145f5f5f209c5d29562edccb1cb1143f008cb0e61c324080304`.
- The image history copies `GraphNeuralNetwork/tests` to `/workspace/tests`, `setup.py` and `requirements.txt` to `/workspace`, then installs the source in editable mode and installs pytest.
- Test fixture layer: manifest digest `sha256:e75d7474147c2d4a80c724c5ba8bf4e9b725ae5210c1bdd1afd75b29d6c4141d`, size 1645 bytes.
- Setup layer: manifest digest `sha256:f9e58b073114994b27aa2bf1a7bdca48cb2e61e889644d6c022a9610b630eb53`, size 491 bytes.
- Requirements layer: manifest digest `sha256:0da08cd3e9079955e5945010c007eac4186dc37dbe5b0b7d44a0d7408c47f18c`, size 198 bytes.
- Source layer: manifest digest `sha256:d74121ad8dd6f287d37522a5ab026cf7bee843de8806bdcd7470c7b3545f36c9`, size 11474674 bytes.

## Upstream Source Lock
- Repository: `https://github.com/shenweichen/GraphNeuralNetwork.git`.
- Revision: `ff3ac3838287d28bee6f6ef0302584c4f4858528` (`improve compatibility`, 2022-06-27).
- The image contains the matching Git checkout, with `origin` pointing at the repository above and `HEAD` at this full commit.
- Reproducible source command: `git archive --format=tar ff3ac3838287d28bee6f6ef0302584c4f4858528 | sha256sum`.
- Git archive SHA-256: `87ed47cd36eb0c977d89a44a9d7b08c12f2c0817362e92401f152c3ed1e71183`.
- License evidence: upstream `LICENSE`, Git blob `b6a1807d27e3a116835a5b6b3e7fe4715656e4e5`, file SHA-256 `b826e46bface5f031f94f1538649960a03752d44f2b3db822654a21ce0acf764`; the text is the MIT License and `setup.py` declares `MIT license`.
- Upstream `setup.py` SHA-256: `4e437c64ac29bcdef2aea42a2233466ef26895b43bc66da97e0e81cab3535080`.
- Upstream `requirements.txt` SHA-256: `be64ac094dcd5c354fdbe061d50045c2e259ac6c30d470f8d2691cb1c6410144`.

## Frozen Collection Comparison
The image fixture contains `tests/__init__.py`, `tests/gat_test.py`, `tests/gcn_test.py`, and `tests/graphsage_test.py`.

| path | image raw bytes | normalized SHA-256 |
| --- | ---: | --- |
| `tests/gat_test.py` | 1689 (CRLF) | `7112a12251c5c1464d6dfdf9e794c09fd0be2dd94c1465cc1bffb263ed26a056` |
| `tests/gcn_test.py` | 2030 (CRLF) | `c0a13046549f1a078a1bfec4c6734dac19e0be33e4a7498c2f9318b13fed2f5d` |
| `tests/graphsage_test.py` | 2210 (CRLF) | `7eb0360c2cb8c6e89e8302408432d48bb397d1c6b6dd73279f1d43bf6848065b` |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

- After CRLF normalization, every frozen test file is byte-identical to the corresponding file at the locked upstream commit.
- AST inventory: one `test_GAT` item, two `test_GCN` parametrized items, and one `test_GraphSAGE` item, for a fixed effective total of `4` with no skips.

## Proven Image Overlay
- `.gitattributes` requests text normalization, but the image working tree retains CRLF; this changes raw hashes only and is explicitly normalized above.
- The image working tree `setup.py` removes only the upstream `README.md` read and `long_description` assignment. Its remaining package metadata and dependency declarations match the locked source.
- The image working tree `requirements.txt` is identical to the locked source after line-ending normalization.
- The setup overlay is recorded rather than silently presented as upstream source; the Oracle script materializes the exact Git revision.

## Native Dependency Audit
- Image config records `PYTHON_VERSION=3.10.11`; the verifier image is the immutable dependency boundary and is run without network access.
- Direct source requirements are `networkx`, `numpy`, `scikit-learn`, `matplotlib`, and `tensorflow>=1.12.0`; the frozen image evidence also includes SciPy and pytest for the test path.
- The observed image package set includes NetworkX 2.8.8, NumPy 2.1.3, SciPy 1.15.3, scikit-learn 1.7.1, Matplotlib 3.10.5, TensorFlow 2.19.0, and pytest 8.4.1.
- No standalone hash-locked wheelhouse is present in this public patch, so catalog dependencies remain explicitly `unknown`; parent Oracle runs must confirm that the pinned image can collect all four tests.

## Verifier Boundary
- `harbor/tests/Dockerfile` derives from the immutable image and copies `/workspace/tests` into the derived verifier image at build time; no hidden test or binary fixture is committed here.
- Runtime candidate files are copied to `/tmp/candidate`, frozen tests replace any candidate-created `tests` path, and a `.pth` override puts candidate package paths ahead of the removed image checkout.
- The verifier performs the legacy editable-install step offline with preinstalled image dependencies, then runs pytest as an unprivileged candidate user.
- `grade.py` reads only verifier-owned JUnit output, rejects collection mismatches against `4`, and writes `reward.json` and `grading.json` itself.
- The agent image is separate, digest-pinned Python 3.10.11; only the Oracle solve script has public network access to fetch the locked source.

## Decision
- Provenance, denominator, and candidate/verifier separation are coherent after documenting the CRLF and setup.py build overlays.
- Package the task at lifecycle `packaged`; do not claim Oracle validity or publication until the parent runs three Oracle trials and empty/stub/forgery/offline controls.

## Parent Gates
- Confirm three independent runs produce `valid=true`, collection `4`, and reward at least `0.80`.
- Treat TensorFlow import, Keras optimizer compatibility, native library failures, or runtime timeout as environment/infrastructure evidence rather than changing the denominator.
- Keep the verifier image reference and source revision immutable when recording results.
