# Autojump Provenance Audit

Status: `packaged`; Oracle and control runs remain pending the parent
orchestrator. This task-local package contains the public specification and
Harbor scripts only. It does not contain hidden test bytes, binary fixtures,
run artifacts, or a copied upstream source tree.

## Legacy Identity And Contract

- Legacy task: `test_files/autojump/`.
- Declared denominator: `23` (`test_case_count.txt`, SHA-256
  `535fa30d7e25dd8a49f1536779734ec8286108d115da5045d77f3b4185d8f790`).
- Commands: `python install.py`, then `pytest
  --continue-on-collection-errors tests` (`test_commands.json`, SHA-256
  `8812b117616441d90e4786ef205dcccfa678f88302293654a0af435382bb75db`).
- Protected path: `tests` (`test_files.json`, SHA-256
  `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Public legacy instruction: `start.md`, SHA-256
  `6229221b75405bfe2759f0e21eaf73db2e21493d9ddd6e04c8b3f1202b242eb0`.
- The Harbor instruction is a behavior-only rewrite; it retains the legacy
  repository-generation identity and the manual `python install.py` entry
  point without copying hidden assertions.

## Pinned Verifier Image

The conversion-loop record at `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json`
recorded this immutable image for `autojump`:

`ghcr.io/multimodal-art-projection/nl2repobench/autojump@sha256:85f4553300641c5771c1853dcf827857a7cde366f391383ba682d809f826a4e5`

Static registry inspection resolved a Docker distribution manifest v2 with:

- Platform: `linux/amd64`.
- Config digest:
  `sha256:c92eed7b060698f903f6f639c9998a9df1b21cef91457f67fad519d660030130`.
- Config runtime: CPython `3.13.4`, working directory `/workspace`, command
  `tail -f /dev/null`.
- Test-copy layer: compressed digest
  `sha256:df48dfd3e64b91617f9149bedc171fbd4d4d757d7726f2ef9e50555bacb58f73`.
- Source-copy layer: compressed digest
  `sha256:53ff41d7143f729a99460df13dbd783b37575a7efbc190f9fee67a1591b4e7e6`.
- Image history copies `/workspace/tests` and `/project`, runs
  `cd /project && python install.py`, installs `pytest==8.4.1`, `mock`,
  `coverage`, and `ipython`, then runs `pytest /workspace/tests`.

The task verifier pins the image by digest and checks the frozen test files
again at build time. Hidden tests and binary fixtures remain inside that
image and its private `/tests/fixture` copy; none are tracked here.

## Frozen Test Inventory And Denominator

The image contains five test files under `/workspace/tests`, totaling 9,327
bytes. Their SHA-256 values are:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/integration/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/unit/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/unit/autojump_match_test.py` | 5,200 | `5f550d554877d587e8941307723db6eb70e7c434c28270a3f2987f6151a9022c` |
| `tests/unit/autojump_utils_test.py` | 4,127 | `094a924a8aaf56c7cf24b77a1cf69ba50d4ddb495b39e484813abbf2922b927b` |

The image pytest cache records 32 collected node IDs. Five Python-3
`skipif` tests are excluded, and four Windows/path `xfail` tests are also
excluded by the fixed metric even if a candidate unexpectedly XPASSes. Thus
the verifier requires a collected total of 32 and computes the fixed
frozen effective denominator as `32 - 5 - 4 = 23`. Any collection mismatch is
invalid and receives reward zero. The grader discovers the four `xfail` markers
from the private fixture at runtime, so their node names are not committed to
the public task.

The source fixture and test fixture are byte-identical to the pinned
upstream revision after normalizing the image's CRLF text checkout. No
assertion or test overlay was detected. The test cache manifest used for this
count is 2,189 bytes with SHA-256
`04e5cfef30cf0c1a6c48d36d4c3d699595bb20d9c97970fd36839eb6b83590d6`.

## Upstream Source And License Lock

- Upstream repository: `https://github.com/wting/autojump`.
- Full revision: `ee21082751da739c65fe0ec2d02ca95d4266aebc`.
- Revision tree: `6e4d10a1f4a6254a92ef7b776ba8f05fd1090bf8`.
- Revision author date: `2023-02-01T14:38:48+06:00`.
- Revision committer date: `2025-02-27T08:03:22-08:00`.
- Deterministic command:
  `git archive --format=tar ee21082751da739c65fe0ec2d02ca95d4266aebc`.
- Unprefixed archive size: 245,760 bytes.
- Git archive SHA-256:
  `a91e88d3d72b8abd2328d1f990d6e360d27736b49375e5c1e3fd8db576752cd9`.
- License: `GPL-3.0-or-later`, evidenced by the frozen `LICENSE` file's GNU
  General Public License version 3 text and the README's explicit
  `GPLv3+` statement.
- License Git blob: `cb5b2e16fa5c0ac5d3fed69c9fe4d2f4c072a5b5`.
- License bytes: 33,103; SHA-256
  `e536867c1175b819d8a746df72ff979c007cecf85ad085e1a808bc498e2d7b51`.

The image's `/project/.git` points at the same full revision and remote
`https://github.com/wting/autojump`. Exhaustive comparison of all 41 tracked
paths found no source difference after CRLF normalization; `install.py` and
both retained test modules are exact source blobs under that normalization.
The only non-text asset, `bin/icon.png`, is byte-identical without
normalization.

## Boundary And Dependency Audit

The legacy install script is executed as the unprivileged `candidate` user in
the verifier, with `HOME` and `SHELL` set explicitly. Its stdout/stderr are
captured before the frozen tests are installed. The test directory is replaced
from the private image fixture, integrity-checked, owned by root, and made
read-only before pytest. The grader is copied by the verifier image and writes
`/logs/verifier/reward.json` and `grading.json` itself.

The candidate environment is public-network by Harbor task convention, while
the separate verifier is `no-network`. Autojump's runtime implementation uses
only the Python standard library; the image's test-only packages are
`pytest==8.4.1` and `mock==5.2.0` (with image-provided transitive tooling).
There are no native runtime dependencies, database services, GUI services, or
binary fixtures required by the frozen tests.

Dependency closure is intentionally recorded as `unknown` in the catalog:
the immutable image provides the test runtime, but no standalone
hash-locked wheelhouse artifact is committed by this task. This leaves the
lifecycle at `packaged` pending the parent Oracle and control gates.

## Static Decision

The source URL, full SHA, GPL evidence, archive digest, image digest, test
inventory, legacy command shape, and fixed denominator are coherent. A
publishable bundle is therefore appropriate as a task-local packaged draft.
Do not promote it to `oracle-passed`, `controls-passed`, or `published` until
three independent valid Oracle runs and empty/stub/forgery/offline controls
are recorded by the parent.

No Docker, Harbor, pytest, Oracle, or negative-control process was run in this
lane. Static work used registry manifest/config/layer inspection, private
layer extraction under `/tmp`, Git revision/tree/archive/license hashing,
exhaustive path/blob comparison, AST/cache inventory, TOML parsing, shell
syntax checks, and repository diff inspection. Shared scripts, datasets,
conversion-loop state, legacy files, and other task directories were not
edited.
