# Pandarallel Provenance Audit

Status: `packaged` for a task-local Harbor 1.4 conversion draft. This lane
performed static/image inspection only: it did not run Docker, Harbor, pytest,
Oracle, or any negative control. Keep the task out of a published dataset
until the parent validation lane records the required runtime gates.

No dataset file, shared index, conversion-loop state, legacy artifact, or other
task directory was modified.

## Legacy Contract

- Legacy task: `test_files/pandarallel/`.
- Declared denominator: `217`; `test_case_count.txt` SHA-256:
  `16badfc6202cb3f8889e0f2779b19218af4cbb736e56acadce8148aba9a7a9f8`.
- Setup and test commands, in order:
  `pip install -e .`, then
  `pytest --continue-on-collection-errors tests`.
  `test_commands.json` SHA-256:
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected path: `tests`; `test_files.json` SHA-256:
  `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public legacy instruction: `start.md`, SHA-256:
  `8ff6a3eb734cf72fd52e32fdac39947b56e81272295ef2a9540aa940ea2fe065`.
- The task-local Harbor instruction is a behavior-only rewrite. It retains the
  package-generation and editable-install contract without reproducing the
  private test file or its assertion text.

## Immutable Verifier Image

The conversion-loop state at `/root/NL2RepoBench/.nl2repo/conversion-loop/state.json`
records this available `linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pandarallel@sha256:f25336a4bdcab50fb33ef2cb008c10634915e98e7dcbe167750a5190fc46ed38
```

The corresponding mutable tag in the state record is
`ghcr.io/multimodal-art-projection/nl2repobench/pandarallel:1.0`; the Harbor
bundle never uses that tag. A manifest-only registry request returned the same
content digest and a Docker distribution manifest v2 with:

- Config digest:
  `sha256:0d88f6cd911699ae28babbe3845a6b902e39f3e3768df09e8ed4c3190981500b`.
- Platform: `linux/amd64`.
- Config creation time: `2025-08-22T14:02:02.7222893Z`.
- Image working directory: `/workspace`.
- Image command: `tail -f /dev/null`.
- Runtime base: CPython `3.10.18` on a Debian trixie-derived image.

Relevant manifest layers are recorded here so the image-backed fixture can be
revalidated without copying hidden bytes into the repository:

| Image operation | Compressed layer digest | Size (bytes) |
| --- | --- | ---: |
| `COPY ./pandarallel-master/tests /workspace/tests` | `sha256:9e1f6c6e824d7b754776931ad31696b1edae6c1893087ab42d15db5cd608ad96` | 1,752 |
| `COPY ./pandarallel-master/setup.py /workspace/` | `sha256:a93195ec9508a143e81b9f6e3cd0b5c4ee931e0a0bb00848a5e5e1c74b8814f5` | 170 |
| dependency installation | `sha256:b59b0e6bf7a7a8d3cd035db8b9ea244814d3fae7ac8302555ccd98b156071cfe` | 167,969,479 |

The image history installs `pytest==8.4.1`, then `pandas`, `psutil`, `dill`,
and `pyarrow` after upgrading pip. The public legacy instruction records the
resulting key versions as pandas `2.3.2`, NumPy `2.2.6`, psutil `7.0.0`, dill
`0.4.0`, pyarrow `21.0.0`, and pytest `8.4.1`. The verifier Dockerfile asserts
these versions at image build time and checks the fixture hash before copying
it into `/tests/fixture`.

The image intentionally contains only the setup file and protected tests, not
an upstream implementation. The Oracle solution fetches the pinned source
revision into the agent workspace; hidden tests remain in the verifier image
and are copied over any candidate-created `tests` directory at run time.

## Upstream Source And License Lock

The exact source baseline is:

- Repository: `https://github.com/nalepae/pandarallel`.
- Full revision: `261a652cddb219ac353ff803e81646c08b72fc6f`.
- Revision tree: `9b685611f02fe74c26a0c6a3f7017b58e56aac2e`.
- Subject: `Fix ValueError for Empty DataFrames: Ensure Process Count is at Least 1 (#245)`.
- Author date: `2024-02-16T13:37:34+05:30`.
- Commit date: `2024-02-16T09:07:34+01:00`.
- Deterministic archive command:
  `git archive --format=tar 261a652cddb219ac353ff803e81646c08b72fc6f`.
- Archive size: `593920` bytes.
- Unprefixed archive SHA-256:
  `e6248ba2a30d551242e03df5b83d71ff4ff63c4b9ada2ab8c3ba82b051e1b5cd`.

The revision's `LICENSE` is the BSD 3-Clause license:

- Size: `1511` bytes.
- Git blob: `67c4dd95f31eef2e48283dc7fea82db7998033bc`.
- File SHA-256:
  `d9077963f80e6e900ef465d3b5d3b2e7fd5d03dfc25ea42270f936d4436d55f7`.
- SPDX mapping: `BSD-3-Clause`, consistent with `setup.cfg`'s BSD license
  metadata and classifier.

The source revision is the current immutable `master` tip returned by the
upstream Git remote during this audit. The Oracle script verifies both the
resolved full SHA and the archive digest before materializing it.

## Frozen Test Inventory And Overlay

The image contains one protected test file:

| Path | Bytes | Image SHA-256 | Image Git-blob-format hash |
| --- | ---: | --- | --- |
| `tests/test_pandarallel.py` | 11,168 | `94c75928f37417101654b14bd9598951e82c462fb0120b040c804229aaacbbe5` | `461aab2c07df667443619375853d0a5e5d6f0dc7` |

The image also contains `setup.py` (38 bytes, SHA-256
`843ac26c38a41abae578250bc0f9419194b320a0f67327d941037a4268f6cfe7`), which
is byte-identical to the pinned upstream `setup.py`. Both image copies are
mode `100755`, whereas the upstream blobs are mode `100644`; the mode changes
are packaging-only overlays.

The upstream test at the pinned revision is 11,163 bytes, SHA-256
`426bcf1ee148ec10b39abb7f0f7313212818438268a0789b6bc58a3514145485`, and Git
blob `0f91c325b8d807c1b6be999d06e6e10a8dee97c1`. The image test is an explicit,
small benchmark overlay rather than an unqualified upstream claim:

1. It moves `from pandarallel import pandarallel` from module scope into the
   `pandarallel_init` fixture. This lets test collection complete before the
   candidate editable install is exercised; no assertion or test behavior is
   changed.
2. The image test copy has executable mode `100755` instead of the upstream
   `100644`; pytest does not use that mode to define collection. The copied
   `setup.py` has the same mode-only `100755` overlay.

The canonical combined unified diff for `setup.py` and the test file
(including both mode changes) is 711 bytes over 26 lines and has SHA-256
`7b1b445e14c9338f7bbb5119a2d72b798877b71a7441a0494e911a651149aa93`.
No image test path was found outside the protected `tests` tree. The overlay is
preserved by the image digest and fixture hash, not copied into this public
repository.

## Denominator Audit

The legacy declaration `217` agrees with an independent AST/fixture expansion
of the immutable image test:

- 18 ordinary `test_*` functions;
- fixture cardinalities include `df_size=2`, `progress_bar=2`,
  `use_memory_fs=2`, `exception=3`, and named/anonymous callable pairs;
- the `pandarallel_init` fixture expands to four combinations through its
  progress-bar and memory-filesystem dependencies;
- the resulting per-test expansion totals exactly `217`;
- no `pytest_generate_tests` or collection hook is present;
- no skip, skip-if, xfail, or parametrization marker is present.

Thus the expected effective denominator is 217 with zero skipped cases under
the pinned test file. This is static collection evidence, not a fresh pytest
collection result; the catalog retains `expected_total_source =
"legacy-file"` until the parent lane collects the final verifier image.
The grader additionally requires `collected == 217`, `skipped == 0`, and
`effective_total == 217`, so a pandas/pytest/plugin drift becomes an invalid
verifier result rather than a silently changed denominator.

## Multiprocessing And Pandas Risk Review

This task is coherent as an image-backed package draft, but its runtime risk is
higher than a serial Python library:

- Every parametrized operation initializes a two-worker process pool, and the
  test matrix exercises both memory-filesystem and pipe transfer paths.
- The source uses pandas internal GroupBy/Rolling/Expanding classes and must
  remain compatible with the pinned pandas `2.3.2` runtime.
- Empty frames and empty Series are deliberately covered by the pinned source
  revision's recent fix; a zero-size chunk regression can otherwise hang or
  raise before a JUnit report is written.
- The verifier limits BLAS/NumExpr thread fan-out to one thread per worker,
  provides 2 CPUs and 4 GiB memory, and bounds installation/test phases at 120
  and 600 seconds. It runs the candidate as UID 10001 and freezes hidden test
  bytes read-only before pytest.

No runtime stability claim is made here. Parent validation must run three
independent Oracle trials and inspect process cleanup, collection stability,
JUnit output, and the empty/stub/forgery/offline controls.

The frozen upstream test also has a small coverage caveat: the complex
DataFrame GroupBy and GroupBy-expanding cases call `.equals(...)` without an
`assert`. They still exercise those code paths, but those two comparisons do
not contribute a correctness assertion. This is recorded as a test-quality
risk, not silently repaired in the hidden fixture.

## Dependency And Verifier Boundary Notes

The immutable image contains the test/runtime dependency closure, but the image
build history installs several packages without a standalone hash-locked
wheelhouse. The catalog therefore records dependency status as `unknown`
rather than claiming a portable offline artifact. The verifier uses
`--no-index --no-deps` for the unprivileged editable install and relies only on
those image-provided versions.

The current Harbor adapter preserves the legacy direct-import test contract in
an isolated verifier container and unprivileged candidate process. It does not
yet provide a task-specific `candidate_client` subprocess/RPC boundary for
all pandas object behaviors. This is acceptable for a task-local conversion
draft but remains a production-publication review item under the separate
verifier policy.

## Static Decision

The source URL, full revision, BSD license evidence, archive digest, immutable
image reference, setup/test overlay, legacy command shape, and denominator are
coherent. A task-local packaged Harbor draft is therefore appropriate. The
recommendation is:

- **Complete for this lane:** keep the files under
  `catalog/tasks/pandarallel/` as the task-local image-backed Harbor 1.4
  package.
- **Blocked for publication:** do not add it to a dataset or call it
  `oracle-passed`/`published` until runtime collection and three Oracle runs
  are valid and stable, the required controls pass, and the candidate-boundary
  decision is reviewed.

## Static Validation

Completed without starting Docker, Harbor, or pytest:

- Read `AGENTS.md` and `CONTRIBUTING.md`, then audited all four legacy files.
- Resolved the immutable image reference from the conversion-loop state and
  verified its registry manifest digest, config digest, platform, relevant
  layer digests, and image history using manifest/blob metadata only.
- Extracted only the setup/test layers to a temporary directory for hashes,
  AST inventory, and upstream comparison; no hidden bytes were copied into the
  repository.
- Cloned the upstream Git history, resolved the full revision, computed the
  deterministic archive and license hashes, and compared the image test/setup
  files to the source blobs.
- Parsed the test AST and recursively expanded fixture dependencies to 18 test
  functions and exactly 217 cases; confirmed no collection hooks or skip/xfail
  markers.
- Ran TOML parsing, Python syntax checks, shell syntax checks, catalog source
  validation, hash/instruction consistency checks, `git diff --check`, and a
  task-scoped diff review after writing the package.

Not run by lane policy: Docker build, Harbor execution, pytest collection or
execution in the verifier image, Oracle, empty/stub/forgery controls, and any
network-dependent candidate behavior.
