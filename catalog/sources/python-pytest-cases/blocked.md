# `python-pytest-cases` Static Conversion Audit

Status: **blocked**. This directory is a task-local audit record only. It does
not contain a catalog task, public instruction copy, Harbor descriptor, Oracle
solution, verifier code, dependency bundle, or hidden test bytes. No dataset,
shared script, conversion-loop state, or legacy file is changed by this audit.

## Legacy Contract

- Legacy task: `test_files/python-pytest-cases/`.
- Declared denominator: `1372`; `test_case_count.txt` SHA-256:
  `a2144767f33525b47ccdbeb90311911fc7966c0975d14ae1df69712264d9ad47`.
- Commands, in order: `pip install -e .`, then
  `pytest --continue-on-collection-errors`; `test_commands.json` SHA-256:
  `0bd1b3d8d819a9bc29dce9aa35222ac4c7042dbf780304a6e34126f7e1d2dd3b`.
- Protected path: `tests`; `test_files.json` SHA-256:
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public instruction SHA-256:
  `15c3d7c423a6e66ad7ecd755520ed3ef72b16a2c83d1e4b1cd34af97852908dd`.
- Legacy difficulty: `Hard`, from `test_files/task_difficulty.csv`.

These files establish the historical identity, but the manually maintained
count is not a frozen collection record.

## Immutable Verifier Image

The canonical conversion-loop state at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` records the available
`linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/python-pytest-cases@sha256:327e70a15c0c033f5186e9b3e8575ddd16c7ae999e6d3b692d29e7384d90b68b
```

Static registry inspection returned the same Docker manifest digest. The
manifest is 4,932 bytes, its config digest is
`sha256:2dec18f68f216edeb298b250acf1d69ad2521b7b26ed7bc760be3e700a9c6198`,
and the config records CPython `3.12.4`, working directory `/workspace`, and
an idle `tail -f /dev/null` command. Relevant compressed layers are:

| Content or build step | Layer digest | Bytes |
| --- | --- | ---: |
| Frozen `/workspace/tests` copy | `sha256:bbefbbdc931ae6a84b06b21e31d75f85d0640b8edb8d2ccf06f47386c17fcfaa` | 48,618 |
| `/workspace/pyproject.toml` | `sha256:ff4a5d13e48683e8f262dcff8eb2710fef34073e1f15c0204a0ba40aaafa2d1f` | 327 |
| `/workspace/noxfile-requirements.txt` | `sha256:4e51219d350285ebf148338d3426d0070b59af1db6727942efd8943a1682ee18` | 264 |
| `/workspace/setup.py` | `sha256:d8d4ccc49accb35ff4eb9323ab042fd3fe595bd81bf84da68a5da61129f3cbf8` | 777 |
| `/workspace/setup.cfg` | `sha256:9d7e2a585f95c61ccbe99d74fa05953229367b2bda0357950f7b96f97238f525` | 2,153 |
| Full source checkout | `sha256:6b19b800ca16d1c8c008fc67e971709f32bd32c326ccedac6e96632f7803ca60` | 16,821,189 |
| Historical successful `pytest` step | `sha256:964a777cdb1fbb9052497660ba143770d05454961af5b0d0e6f2271d41964055` | 1,046,657 |

The registry manifest, config, and selected layers were inspected without
starting a container. Extracted bytes remained under `/tmp` and are not part
of this task directory.

## Upstream Source And License Lock

- Repository: `https://github.com/smarie/python-pytest-cases`.
- Full revision: `f030486cd5d9c05417c91d272b2afdc80d3dfc08` (`Add
  with_case_tags decorator (#361)`, committed `2025-08-25T08:35:13+02:00`).
- Git tree: `d440ff46d84b4d470352fb57bec242248298415d`.
- Revision position: `3.9.1-1-gf030486`; image `origin/main` and `HEAD` both
  resolve to this full revision.
- Archive command:
  `git archive --format=tar f030486cd5d9c05417c91d272b2afdc80d3dfc08`.
- Archive size: `2,048,000` bytes; SHA-256:
  `8dbc7cde28a6b0ac1b6f5ad16e0223f3bf1e29ce4de6b3afdb1d997f9dc6323e`.
- License: **BSD-3-Clause**, evidenced by the revision's root `LICENSE` and
  BSD classifier/metadata in `setup.cfg`.
- Upstream `LICENSE`: Git blob
  `dc9c045ae5a74c260cc3900eac312dacbc23f562`, 1,558 bytes, SHA-256
  `612c0cca8f6accec769ef7b2d0fee578a2a95bbbaef912f74c541364a38ef0e2`.
- Image `LICENSE`: identical text with CRLF endings, 1,587 bytes, SHA-256
  `c0062b3d50e1f3840c0dcab117eab7d99f46802766c47b4be7502201649057f8`.

The archive identifies the clean upstream baseline, not the overlaid image
working tree described below.

## Source, Setup, And Test Overlays

All tracked text in the image source copy uses CRLF instead of upstream LF.
After line-ending normalization, exactly six tracked paths differ from the
locked revision.

Three are packaging-only overlays:

1. `pyproject.toml` removes the `setuptools_scm` build requirement. Image
   SHA-256: `24a413600b28cb5e7ff81519dffc88162a23a9fcf59c7d7af503b58931363383`.
2. `setup.py` removes the `setuptools_scm` requirement, generated version
   file, dynamic version lookup, and versioned download URL. Image SHA-256:
   `b14b4143ba718f05e186603b4f8db5a8eed9ab896f524798b730581d76d02d75`.
3. `setup.cfg` removes `description_file`, long-description fields, and the
   `setuptools_scm` setup requirement. Image SHA-256:
   `f1319d56e0a6f23733428fb4824a22a9cfeeb0e971f929c41b7632520e3a2781`.

The four setup files copied separately to `/workspace` are byte-identical to
the corresponding source-copy files, so there is no second setup overlay.

Three frozen tests have behavioral overlays. Each imports `pytest` and adds an
unconditional `@pytest.mark.skip` to one fixture-closure assertion:

| Path | Image SHA-256 | Upstream Git blob |
| --- | --- | --- |
| `tests/pytest_extension/doc/test_doc_fixture_graph_union.py` | `3925a04dca551f4e3035d7972816e8d5820de3d0a25b571e521640ba573bf042` | `a718022fcbd1d33a670aa2d4411e634c6b7a0c45` |
| `tests/pytest_extension/fixtures/fixture_unions/test_fixture_closure_edits.py` | `2cf838319ae83033e54b8845feadc3f88a19bfd6baf91a0b7babdce29a5fa044` | `b0d8b2aa9ebfa714a9e684368d429e2220eb5d3f` |
| `tests/pytest_extension/fixtures/fixture_unions/test_fixtures_union_2hard.py` | `a3472c75e17ff5588dfba73a2ed3a7e3f01ca857be4155950324f226d7763ccd` | `a5262cd1925bffad24a63240ec642a4103cb8912` |

The frozen `/workspace/tests` copy is byte-identical to the overlaid source
test tree: 194 files, 254,338 bytes. Its canonical
`path<TAB>size<TAB>sha256` manifest has SHA-256
`0f3e075c482d95268bba27d6e07216e71d3457c6f95ff44c9c3fd2fea5085ea6`.
No image test is copied into this repository.

## Denominator Blocker

The source-copy layer has no pre-existing pytest cache. The image history then
records a successful plain `pytest` step. It creates a fresh
`.pytest_cache/v/cache/nodeids` containing **1,491 unique node IDs** across 140
test files. The cache is 153,310 bytes with SHA-256
`3963fb252696feed92ed00efdf03e4c1e4cf59bf5f85ccee0b439f322046651c`.

This differs by 119 from the legacy declaration of 1,372. The three test
overlays also deliberately skip fixture-closure assertions. The image retains
no JUnit, structured collection report, skipped-node manifest, or evidence
proving an effective `collected - skipped` value of 1,372. Its historical step
also uses plain `pytest`, not the legacy `--continue-on-collection-errors`.

The cache is strong collection-drift evidence, but not a safe replacement
denominator. Retaining 1,372 is unsupported; changing it to 1,491 would change
the legacy metric and still mishandle skipped cases.

## Dependency Closure Blocker

Image history installs the editable package, `noxfile-requirements.txt`, and
an ad hoc async/plugin test set from a public PyPI mirror. Candidate metadata
leaves `decopatch`, `packaging`, and `pytest` unpinned and only lower-bounds
`makefun`. Nox requirements are unpinned except for `setuptools<72`; the ad hoc
test dependencies have no pins. No hash-locked wheelhouse, native dependency
manifest, offline install transcript, or allowlisted command-plan artifact is
recorded. The immutable image does not prove that an arbitrary candidate
editable install is reproducible without network access.

## Candidate Boundary Blocker

Static inventory finds 152 test files directly importing `pytest_cases`, 111
files exercising parametrization, fixture unions/graphs, or pytest hooks, and
zero `candidate_client` references. The suite passes live functions, fixtures,
marks, requests, plugin state, closures, async behavior, and dynamically
generated pytest objects in-process.

No task-specific subprocess/RPC adapter exists. Prepending candidate paths
would import candidate code into the trusted pytest/report process; the
generic JSON adapter cannot preserve these pytest object interactions.

## Decision

Keep `python-pytest-cases` **blocked**. Do not create `task.toml`,
`instruction.md`, a Harbor 1.4 bundle, private fixture copies, or an Oracle
solution. Provenance is recoverable, but the fixed denominator, dependency
closure, test-overlay approval, and candidate boundary are not publication
coherent.

To reopen, approve and version the source/test overlays, build a no-network
hash-locked dependency closure, implement a task-specific candidate adapter,
and collect a structured stable effective denominator in the final verifier.
Oracle and controls belong to a later lane after these blockers are resolved.

## Static Validation Scope

This audit read `AGENTS.md`, `CONTRIBUTING.md`, the legacy contract, immutable
loop image record, registry metadata/history, selected layers, and pinned Git
objects. It compared all frozen test and tracked source paths, generated hashes
and static inventories, and inspected the existing pytest cache. It did not
run Docker, Harbor, pytest, candidate installation, Oracle, or controls.
