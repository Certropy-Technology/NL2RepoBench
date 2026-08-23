# Pyperclip Conversion Evidence

## Status And Recommendation

**Record recommendation: BLOCKED.** Keep this task out of every published dataset. The task-local Harbor 1.4 bundle is a conversion draft, not an Oracle-gated publication record. The current Package campaign Oracle gate has not been run, the offline candidate dependency closure is not locked, and the frozen effective denominator covers only two unavailable-backend exception checks.

The revision and verifier image are freezeable and the frozen environment does not require a GUI service. The blocker is therefore task/verifier quality and missing gate evidence, not an unresolvable source revision or an unavailable desktop session.

## Legacy Projection

The four legacy inputs were inspected without modifying them:

| File | Bytes | SHA-256 | Meaning |
| --- | ---: | --- | --- |
| `test_files/pyperclip/start.md` | 42,203 | `a217b18cf981606d5b16b759d8f1b8cde939f121ecc929d5899a5d07344b1a0c` | Legacy public prompt |
| `test_files/pyperclip/test_case_count.txt` | 1 | `d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35` | Fixed effective denominator `2` |
| `test_files/pyperclip/test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`, then `pytest --continue-on-collection-errors tests` |
| `test_files/pyperclip/test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The Harbor verifier preserves the editable installation, exact protected test path, `--continue-on-collection-errors`, collection stdout/stderr, pytest stdout/stderr, JUnit, raw collected count, skipped count, effective denominator, exit codes, validity, failure class, and numeric reward.

## Verifier Image Lock

- Requested tag: `ghcr.io/multimodal-art-projection/nl2repobench/pyperclip:1.0`
- Immutable manifest digest: `sha256:a3cac678d154fc68b673495484f834c92daa4aa3db42e0008264a49c3f7d2769`
- Pinned verifier reference: `ghcr.io/multimodal-art-projection/nl2repobench/pyperclip@sha256:a3cac678d154fc68b673495484f834c92daa4aa3db42e0008264a49c3f7d2769`
- Image creation timestamp reported by Docker: `2025-11-17T09:25:19.215121776Z`
- Runtime: Debian GNU/Linux 11 (bullseye), CPython 3.10.11, pytest 9.0.1
- Frozen test path: `/workspace/tests/test_pyperclip.py`
- Frozen test bytes: 4,903
- Frozen test SHA-256: `4e4570c598bece8cc307fa1f52966063b1d23d5e466218720c76a6ddf3437963`
- Frozen test Git-blob-format hash: `2cce343a7852345f45005b17e28f049169a819f9`
- Frozen image `pyproject.toml` SHA-256: `d79cfe8fe6c06be3bd07bd0a2a1d1cbac94951c3fc4d66421bc560c083ca051c`

The separate verifier Dockerfile checks the frozen test SHA-256 while building. The agent Dockerfile is based on the repository's pinned Python image and contains neither the verifier image nor test bytes.

## Source And License Lock

- Upstream: `https://github.com/asweigart/pyperclip`
- Full revision: `f5326bfd7c5448b40051dd261a7304657977b838`
- Revision date: `2025-09-26T10:41:20-04:00`
- `git archive --format=tar HEAD` SHA-256: `4e80effb92cd84116a2541bb5aa4df7d7832761c04600322f558265ba73c0275`
- SPDX license: `BSD-3-Clause`
- License evidence: `LICENSE.txt` at the frozen revision, Git blob `799b74c5bf39adf1b6df285374890056fb4c48eb`
- Upstream test blob at the revision: `cf31b56891eff3c9ec9483e5ff7019c879aedab8`
- Upstream test SHA-256 at the revision: `86ebc72f9c9e612c37d6551851275b9a6f7aa7c3a43a289f331101e4cad3db4d`
- Upstream `pyproject.toml` blob at the revision: `c8c591896b22a2f32f1ab2806978506776fb8ba6`

The frozen image test is not byte-identical to the upstream test blob. Inspection of the upstream master history and 114 fetched pull-request refs found no commit containing image blob `2cce343a...`. The image test is a benchmark overlay on the full revision: it changes imports, supplies a `HAS_DISPLAY` fallback, and marks the non-string test skipped. Its patch against the frozen upstream test has SHA-256 `db6aac34025836739d01ee9d162697b403c1b2e8fa86412b2d85a1f747c96c06`. Source provenance is therefore the full upstream SHA plus archive digest; hidden-test provenance is the immutable verifier image plus exact test hash. They must not be represented as one unmodified upstream blob.

## System Boundary And Effective Coverage

The frozen image has no `DISPLAY` or `WAYLAND_DISPLAY`, no `/dev/clipboard`, and none of these executables on `PATH`: `xclip`, `xsel`, `wl-copy`, `wl-paste`, `klipper`, or `qdbus`. PyQt5, QtPy, PyObjC, and desktop-session services are also absent. The tests therefore exercise no real clipboard backend and need no clipboard-related system package.

The frozen result is:

| Raw collected | Skipped | Effective denominator | Passed | Exercised behavior |
| ---: | ---: | ---: | ---: | --- |
| 92 | 90 | 2 | 2 | The two callables from `init_no_clipboard()` each raise a `RuntimeError`-compatible exception |

All Windows, macOS, Cygwin, WSL, Qt, XClip, XSel, Wayland, and Klipper cases skip in this environment. Their names must still import successfully for collection, but their copy/paste behavior is not scored. The explicitly skipped non-string test is also excluded. The public specification describes the frozen source behavior but does not promise a usable desktop clipboard in the grader.

An image-compatible baseline using the frozen source revision plus the exact image test overlay completed with `92 collected, 90 skipped, 2 passed`, giving an effective reward of `1.0`. This was a direct legacy-image compatibility probe, not a Harbor Oracle trial.

## Gate Record

| Gate | Result | Evidence |
| --- | --- | --- |
| Image pull and digest resolution | Passed | Docker reported manifest digest `sha256:a3cac678...d2769` |
| Source full-SHA fetch | Passed | `git rev-parse HEAD` returned `f5326bfd...7b838` |
| Source archive lock | Passed | Repeated local `git archive --format=tar HEAD` returned `sha256:4e80effb...c0275` |
| License identification | Passed | Frozen `LICENSE.txt` is BSD 3-Clause text |
| Frozen backend audit | Passed | No GUI/session variables, helper commands, or `/dev/clipboard`; only unavailable backend is effective |
| Image-compatible baseline | Passed | Install exit `0`; pytest exit `0`; `2 passed, 90 skipped`; effective reward `1.0` |
| Shell syntax | Passed | `bash -n` accepted `solution/solve.sh` and `tests/test.sh` |
| Grader syntax | Passed | `python3 -m py_compile harbor/tests/grade.py` |
| TOML parsing | Passed | Python `tomllib` parsed both task descriptors |
| Instruction parity | Passed | Public catalog and Harbor instructions are byte-identical |
| Catalog CLI validation | Incomplete | `uv run nl2repo task validate-source catalog/tasks/pyperclip` timed out after 120 seconds while creating/building the local environment; a 30-second offline retry and 10-second direct `.venv/bin/nl2repo` retry also timed out, so no validation verdict was produced |
| Harbor schema/conversion-loop validation | Not run | Stopped before any additional long build/run operation |
| Harbor Oracle gate | Not run | No Harbor result artifact; the current Package campaign requires one valid run with collection matching and reward at least `0.80` |

## Residual Risks

1. The denominator of two does not score `copy`, `paste`, automatic selection, manual selection, Unicode handling, CLI behavior, or any real platform backend. A stub that imports the required names and raises from the unavailable backend can receive full reward.
2. The frozen tests are benchmark-modified rather than an exact upstream Git blob. The image digest and file hash preserve them, but this weakens upstream-only provenance claims.
3. The conversion draft runs the exact legacy pytest file in an unprivileged candidate process. It isolates hidden bytes from the agent image, but it is not the hardened `candidate_client` subprocess contract required for production publication and does not yet have forgery-control evidence.
4. The candidate dependency closure remains `status = "unknown"`; no offline wheelhouse artifact is locked in the catalog.
5. The agent image uses the repository's pinned Python 3.12 base while the frozen verifier uses Python 3.10.11. The source supports both, but model-environment parity has not been demonstrated.
6. No Harbor Oracle gate result, empty/stub/forgery controls, or offline network proof has been recorded.

## Task-Local Repair

- The verifier creates `/tmp/candidate-results/junit.xml` before the candidate
  test process starts and uses a sticky report directory. The candidate cannot
  replace the report inode with a symlink or another file before grading.
- The existing agent image already installs `ca-certificates` and `git`, matching
  the Oracle solution's pinned-revision fetch requirement.

To unblock, adapt the behavior checks to the hardened candidate subprocess boundary, add deterministic mocked-backend coverage sufficient to measure the public contract, lock the offline dependency closure, run conversion-loop validation, then record one valid Harbor Oracle gate run with collection matching and reward at least `0.80`. If preserving the historical denominator is mandatory, exclude this task from the publishable benchmark because its two effective assertions do not measure the advertised clipboard API.
