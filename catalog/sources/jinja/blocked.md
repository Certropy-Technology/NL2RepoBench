# `jinja` Legacy Conversion Audit

Status: **blocked**. This audit is paired with a parseable descriptor and
hash-bound production evidence. It does not contain a Harbor runtime, Oracle
solution, hidden tests, binary fixtures, or a dependency bundle;
`catalog/tasks/jinja/` remains absent.

## Legacy Identity

- Legacy task: `test_files/jinja/`.
- Declared denominator: `911`, from `test_case_count.txt` (SHA-256
  `a5ccb1c538e34663a658b1be28b16455ee5285efb10e6f1d4caba1f69ec9782b`).
- Protected test path: `tests`, from `test_files.json` (SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Legacy setup and test commands, from `test_commands.json` (SHA-256
  `aa16a75a1e0aedfc90d2371026091acb174a0269697cc7862080c3b76403346e`):

  ```text
  echo 'This is sample license text.' >> LICENSE.txt
  echo 'This is sample README text.' >> README.md
  pip install  -e .
  pytest --continue-on-collection-errors tests
  ```

- Public instruction source: `test_files/jinja/start.md` (SHA-256
  `54795b9e1054579eee2ba29e474bc035a4fde5f96be925b738d1c30f6e062c0e`).

The legacy task identity and declared denominator are preserved. A new task
version would be required for any source revision, test selection, setup
command, or denominator change.

## Immutable Image Record

The conversion-loop state records this immutable verifier image for `jinja`:

- Reference:
  `ghcr.io/multimodal-art-projection/nl2repobench/jinja@sha256:4143726f46dd7cd8a24f9894d665b4f4fbc7233787713fb5696810a60a8efe8c`.
- Platform: `linux/amd64`.
- The registry manifest resolves to the requested digest and records config
  digest `sha256:77095ffd8ac50c6bfda70873d3396f5c211f6ee2bae940f0b1099a8c4b19aaf6`.
- Static manifest inspection also recorded source/test-related layer digests
  `sha256:689d7b7e1e645677289b6303379755904020c1682446d8cdf28bc1e94de9e6cb`,
  `sha256:6b5ceb81026917b0f7303987dfe31d3ef23f0ddcdf66eaed9ca3cc09b7f6e8ff`,
  and
  `sha256:55c93b314e57aab5b7ed9e2a47882a64c247a6e84583673ef9a6483ea6e14cf0`.

The digest and manifest metadata establish an immutable image reference, but
they do not by themselves prove the contents of the test, setup, cache, or
dependency layers. Docker and Harbor execution are intentionally out of scope
for this lane, and no private layer extraction or hidden test bytes are added
to the repository.

## Upstream Source Lock

- Repository: `https://github.com/pallets/jinja`.
- Full revision: `5ef70112a1ff19c05324ff889dd30405b1002044`.
- Revision date: `2025-06-14T13:34:58-07:00`.
- Reproducible archive command:
  `git archive --format=tar 5ef70112a1ff19c05324ff889dd30405b1002044`.
- Archive size: `1,249,280` bytes.
- Git archive SHA-256:
  `61082a25b5f6e7c49a0e4c12d9aa6be8e684489e0d613dc14512e8ea0c001421`.

The detached checkout's `pyproject.toml` declares `BSD-3-Clause`, and the
root `LICENSE.txt` is 1,475 bytes with SHA-256
`3b49dcee4105eb37bac10faf1be260408fe85d252b8e9df2e0979fc1e094437b`.
The source requires Python `>=3.10`, runtime `MarkupSafe>=3.0`, and uses the
PEP 517 backend requirement `flit_core<4`.

The pinned upstream tree contains 107 files totaling 1,146,887 bytes, 25
Python files under `src/jinja2` totaling 14,351 physical lines, and 31 files
under `tests/` totaling 276,004 bytes. These are upstream-history inventory
facts, not claims that the same files and bytes are present in the immutable
verifier image.

## Image/Test/Setup Comparison

The legacy files establish the intended setup sequence and the fixed value
`911`, while the detached upstream revision establishes the source tree and
its `tests/` history. The conversion-loop state exposes only the immutable
image reference and platform; it does not contain a signed test manifest,
setup transcript, collected-node manifest, dependency lock, or content
address for the image's private test bundle.

Consequently, this lane cannot prove all of the following without
materializing private image content or running the prohibited infrastructure:

1. The image's `/workspace` source overlay is byte-identical to the pinned
   upstream revision, including any image-only packaging changes.
2. The image's frozen `tests/` paths and binary/resource fixtures are exactly
   the upstream paths at that revision, with no additions, omissions, or
   generated overlays.
3. The image's setup sequence reproduces the legacy license/readme writes,
   editable install, and pytest configuration without dependency or plugin
   drift.
4. The image actually collects `911` effective test cases, with skipped cases
   handled according to the legacy metric contract.

The upstream inventory is therefore useful provenance evidence, but it cannot
replace image-backed collection evidence. Treating the legacy number as a
verified frozen denominator would be a misleading publication claim.

## Blocking Findings

### Candidate build and native dependency closure

The pinned project builds through `flit_core<4`. No hash-locked, offline
candidate build/test dependency artifact is recorded for this task. The
runtime dependency `MarkupSafe>=3.0` may use its optional native speedups, but
there is no recorded wheel/source/compiler closure proving that the candidate
editable install works under the final verifier's no-network boundary. The
legacy `pip install  -e .` command is not sufficient evidence of a reproducible
offline install.

### Candidate/verifier boundary

Jinja's upstream tests directly import the candidate and exercise rich
in-process objects and behavior: `Environment` and `Template` instances,
loaders and resources, parser/compiler nodes, async rendering, extensions,
sandbox behavior, callbacks, and exception objects. The production verifier
contract requires trusted tests to call a candidate subprocess/API boundary;
there is no approved Jinja-specific adapter that preserves these assertions.
Copying the upstream tests into a trusted verifier or importing the candidate
from the grader would violate that boundary.

### Overlay, denominator, and network boundaries

- **Overlay:** the exact image source/test overlay and replacement rules are
  not proven from the state record; candidate-created tests could not be
  safely replaced by an unverified fixture copy.
- **Denominator:** `911` is the legacy declaration, not an independently
  verified image collection result in this lane.
- **Network:** the verifier must be offline, but candidate build dependencies
  and the editable install have no recorded offline closure. Enabling network
  access to make the install work would invalidate the intended verifier
  boundary.
- **Native dependencies:** the image record does not prove a compatible,
  hash-locked MarkupSafe build path for the candidate environment.
- **Candidate boundary:** no task-specific subprocess/RPC adapter exists for
  the direct-import test contract.

## Decision

Keep `jinja` **blocked** and leave the lifecycle at audit-only. Do not create
`task.toml`, `instruction.md`, `harbor/`, or any private test artifact in this
lane. Do not claim Oracle, empty, stub, forgery, offline, or collection-gate
results.

To reopen this task, provision all of the following as versioned, auditable
inputs:

1. An image-backed private test/setup manifest that can be compared against
   revision `5ef70112a1ff19c05324ff889dd30405b1002044`, including fixture
   hashes and the collected effective denominator.
2. A complete hash-locked offline build/test dependency closure, including
   `flit_core` and a compatible MarkupSafe path, or an approved replacement
   install plan with equivalent provenance.
3. A reviewed Jinja-specific candidate adapter that keeps private tests and
   trusted reports outside the candidate process.
4. A fixed command plan preserving the legacy task identity and setup
   semantics, followed by three independent Oracle runs and the required
   controls in a later execution lane.

## Static Validation Scope

The audit uses only repository files, detached Git source history, SHA-256
checks, and immutable registry metadata. No Docker container, Harbor job,
pytest run, candidate install, private test extraction, or network-dependent
candidate behavior was run. No tests or private fixtures were added.
