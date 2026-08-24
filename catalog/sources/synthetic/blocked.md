# Synthetic Data Kit Conversion Audit

Status: **blocked**. This task-local record is static audit evidence only. It
does not contain a Harbor bundle, a copied upstream tree, hidden test bytes,
Oracle output, or control results. No Docker, Harbor, or pytest execution was
performed.

## Legacy Contract

- Task: `test_files/synthetic/`.
- Public instruction: `start.md`, 107,127 bytes, SHA-256
  `769069bf0cbd92664b54d84e0c1d2b46d4e83a21c561fce495ae4434ecdda522`.
- Declared denominator: `93`; `test_case_count.txt` is 2 bytes, SHA-256
  `6e4001871c0cf27c7634ef1dc478408f642410fd3a444e2a88e301f5c4a35a4d`.
- Commands: `pip install -e .` and
  `pytest --continue-on-collection-errors tests`; `test_commands.json` is 67
  bytes, SHA-256
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected test path: `tests`; `test_files.json` is 9 bytes, SHA-256
  `af7f0b2bd342822f2a8e6a9fda610570f911f30d3108379ea4184c0866727c3`.

## Upstream Provenance

The image fixture and image `pyproject.toml` are byte-identical to the
following reachable upstream revision:

- Repository: `https://github.com/meta-llama/synthetic-data-kit`.
- Full revision: `69db1a2d749d8c6aa1b467cd209b5b2930f053a2` (merge PR #72,
  2025-09-29T12:46:08-07:00).
- Tree: `1105dec0dbb012d1b3f424e7fc8f748e1be34f2b`.
- `git archive --format=tar <revision>` SHA-256:
  `6b1da69b1c2f44ee4924eb7d398b8c66ad85600a29e71e9c5b796153a3f28009`.
- License: MIT, from upstream `LICENSE` at that revision; 1,086 bytes,
  Git blob `aab621b4b2bdcb60759caca2ca3dff4667c1abf6`, file SHA-256
  `47d22e84f5cc964465173b1e803686bc3557762c0126ff65d788d7386f55b44e`.
- Upstream `pyproject.toml` SHA-256:
  `35d094343f14374554cea750737a95eeaeeef7916fba9320217412ab48fcee9f`.

The image fixture contains 27 non-cache files under `workspace/tests/`. Static
AST inventory finds 93 ordinary `test_*` functions, no parametrization, and no
skip/xfail decorators. Every one of those 27 files matches the corresponding
path at the locked revision; the image `workspace/pyproject.toml` also matches
the locked revision. The image therefore does not show an undocumented test,
setup, or source overlay once the revision is correctly locked to `69db1a2`.
The current upstream tip `27a5541b...` is not the image revision: its
`tests/unit/test_error_handling.py` has the later 11-line test change, while the
image retains the `69db1a2` blob.

## Immutable Verifier Image

The conversion-loop record assigns this `linux/amd64` image:

`ghcr.io/multimodal-art-projection/nl2repobench/synthetic@sha256:14e77546f0cfa817f1a01914bc4027ad6c82d7f09e45542a93b014012e1bdaaf`

Registry manifest-only inspection returned the same content digest. Its
manifest records config digest
`sha256:cf7b1cbd4de6b0f5af987cec0045050dcbcc0758b998951fb3c75dba5a321adf`
(10,012 bytes), a private-test layer
`sha256:60c4c9e4f20040b932dde04ee35d1f008916f63ed59a2ec7feaec402fd573850`
(100,583 compressed bytes), a setup layer containing `workspace/pyproject.toml`
`sha256:97ce31e3de3ea06ff967448f50026aa469e3d166ac26a75a409aadac6a147b92`
(1,646 compressed bytes), and a dependency layer
`sha256:a658eecbee166cef91dccd25adde2d2d99a475caf654a7d57979b6ce3ae6389a`
(218,490,815 compressed bytes). The downloaded layer bytes matched their
manifest digests.

**Blocker 1: the image config is not retrievable or verifiable.** A registry
GET of the manifest's config blob returned HTTP 400
`DIGEST_INVALID` for the manifest-declared config digest. Consequently the
image OS/base-image metadata, environment history, and config-level command
and platform claims cannot be independently validated. A digest-pinned image
whose config object fails digest validation is not a usable immutable verifier
boundary for publication.

## Dependency Closure

The image layer statically contains Python 3.13 site packages, including
`datasets 4.2.0`, `pdfminer.six 20250506`, `pydantic 2.12.0`,
`python-docx 1.2.0`, `python-pptx 1.0.2`, `pytube 15.0.0`, `PyYAML 6.0.3`,
`requests 2.32.5`, `rich 14.2.0`, `typer 0.19.2`, `openai 2.3.0`,
`Flask 3.1.2`, `Flask-WTF 1.2.2`, `beautifulsoup4 4.14.2`, `pylance 0.38.2`,
and `PyMuPDF 1.26.5`, plus their observed transitive distributions.

**Blocker 2: the installed closure is neither lock-described nor complete for
the declared project metadata.** The locked upstream/image `pyproject.toml`
declares `bootstrap-flask>=2.2.0`, but the image layer contains no
`bootstrap-flask` distribution or package. There is also no requirements lock,
hash-locked wheelhouse, or dependency manifest associated with the image.
The legacy `pip install -e .` command cannot therefore be proven to succeed
offline in the image-backed verifier, and candidate dependency resolution
would otherwise depend on an unavailable or mutable package index.

## Candidate/Verifier Boundary

**Blocker 3: the legacy test contract has no approved candidate subprocess
boundary.** The existing conversion path copies the candidate workspace and
then invokes `python -m pytest` in the verifier process. The frozen tests import
`synthetic_data_kit` directly and patch its modules; no `candidate_client`
adapter, trusted runner isolation, or separate candidate process is present.
This violates the production verifier contract requiring trusted hidden tests
to communicate with the candidate through a bounded subprocess API rather than
importing candidate code in the trusted verifier. The standard legacy
conversion script also uses editable pip installation without `--no-deps`,
which compounds the unresolved offline dependency closure.

## Decision

Do not create `task.toml`, `instruction.md`, or a Harbor 1.4 tree for this
candidate. Keep `synthetic` blocked until all of the following are supplied:

1. A retrievable, digest-valid immutable verifier image config, with its
   runtime/base image and build history recorded.
2. A complete offline dependency closure matching `pyproject.toml`, including
   `bootstrap-flask`, represented by a versioned lock/wheelhouse or equivalent
   immutable artifact.
3. A reviewed separate-verifier adaptation in which hidden tests do not import
   candidate code in the trusted process, followed by collection and Oracle/
   control gates in a later execution phase.

The source revision, MIT license, test provenance, and declared denominator are
otherwise coherent. No dataset/shared file or conversion-loop state was
modified.
