# `frontmatter` Provenance Audit

Status: **blocked**. This directory is an audit record only. It is not a
publishable Harbor task. No `task.toml`, public instruction copy, Harbor
bundle, verifier code, Oracle solution, hidden test bytes, binary fixture, or
dataset entry is included.

## Preserved Legacy Identity

- Task id: `frontmatter`.
- Legacy source directory: `test_files/frontmatter/`.
- Public instruction file: `test_files/frontmatter/start.md`, 44,346 bytes,
  SHA-256
  `bbe70efdae51c6c917901b08151d3940a5ae60a2253ecc4934046370ceb0c235`.
- Declared legacy denominator: `55`, from
  `test_files/frontmatter/test_case_count.txt` (2 bytes, SHA-256
  `02d20bbd7e394ad5999a4cebabac9619732c343a4cac99470c03e23ba2bdc2bc`).
- Declared test path: `tests`, from `test_files/frontmatter/test_files.json`
  (9 bytes, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).
- Legacy commands, in order, from
  `test_files/frontmatter/test_commands.json` (78 bytes, SHA-256
  `7c51442c79c7435459f8005057cd4ed3750eb2019f17136f4ad73944f809c618`):

  ```text
  pip install -e .
  pytest --continue-on-collection-errors /workspace/tests
  ```

The command and protected path preserve the legacy packaging/test-path
contract, but they do not prove that an image copied the intended tests to
`/workspace/tests`, that editable installation succeeded, or that collection
produced exactly 55 runnable items.

## Missing Immutable Image Evidence

The required conversion-loop state file
`.nl2repo/conversion-loop/state.json` is not present in this worktree, and no
recoverable state record was found under the available temporary or data
directories. The checked-in image lock
`catalog/datasets/nl2repobench-harbor-pilot/legacy-images.lock.toml` has no
`frontmatter` entry.

Consequently, the following verifier facts are unresolved:

- immutable verifier image reference and manifest digest;
- image platform, config digest, and layer/file inventory;
- frozen test/setup copies and their hashes;
- image network mode and native dependency closure;
- image build history and the provenance of `/workspace/tests`;
- structured pytest collection and the frozen denominator.

An image reference was not inferred from the task name or sourced from an
external registry. No Docker, Harbor, image pull, or container process was
run in this lane.

## Upstream Provenance State

The project identity in the legacy instruction points to the canonical
upstream candidate `https://github.com/eyeseast/python-frontmatter`. A remote
lookup observed `main` at
`dc7c0af5466b104e0ba01ae3c5b2cd77edc27292`, but that is only the current
remote tip and is **not** adopted as the frozen source revision.

Without the missing image source/test inventory, the image-to-history match
cannot be performed. Therefore the task source lock remains unresolved:

- frozen upstream commit: **unresolved** (no full SHA is claimed);
- SPDX license evidence at that frozen commit: **unresolved**;
- deterministic `git archive` SHA-256 for that frozen commit: **unresolved**;
- overlay manifest, if any: **unresolved**.

The repository candidate and its current tip must not be substituted for the
missing frozen revision. In particular, a current upstream license or archive
hash would not establish provenance for the unobserved verifier image.

## Gate Decision

The task remains **blocked** because the image, source revision, license lock,
archive digest, frozen test inventory, and collection record cannot be tied to
the preserved legacy identity. The declared count of 55 is not a frozen
denominator. The `/workspace/tests` path and editable-install command are
also unverified against the candidate boundary.

To reopen this task, provide the conversion-loop state record or an approved
immutable image lock, then:

1. inventory the frozen `tests` and setup files without publishing hidden or
   binary bytes;
2. identify the unique upstream commit and record its SPDX license evidence
   and unprefixed `git archive` digest;
3. reconcile image collection with the preserved denominator of 55, including
   any overlay and packaging differences;
4. confirm network/native dependency requirements and adapt tests to a
   separate candidate subprocess verifier; and
5. only then create a Harbor 1.4 image-backed bundle and run Oracle/controls in
   the parent validation lane.

## Static Validation

The four legacy artifacts were parsed/hashed and their task id, count,
command sequence, and protected path were checked. No catalog source
validation was run because this blocked record intentionally contains no
`task.toml`. No shell, Python, TOML, Docker, pytest, Harbor, Oracle, or
negative-control execution was performed. Shared scripts, datasets,
conversion-loop state, legacy files, and other task directories were not
edited.
