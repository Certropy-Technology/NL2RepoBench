# `docstring-parser` Authoring Blocker

Status: **blocked**. No Harbor bundle is present in this directory.

## Revalidated provenance

- Candidate record: `reports/github-package-candidates.v1.json` entry
  `docstring-parser`.
- Upstream: `https://github.com/rr-/docstring_parser`.
- Revision: `8347d8fb347bd66e4bf5711d3df586357166944a`.
- Revision verification: detached checkout resolved to the requested full
  commit SHA.
- Git archive digest:
  `sha256:2cb59707c20099e0f8b61ab9eeb6faeb7fea370a03b3468c822f84c0ac21f3e9`.
- License: `LICENSE.md`, SPDX `MIT`; 1,084 bytes, ending in a newline;
  byte digest
  `sha256:dfe514a337ae8417abd31a8af707bbd6172b03e5430bb083e145899ea97a3eea`.
- Package metadata: distribution `docstring_parser`, version `0.18.0`,
  `requires-python >=3.8`, Hatchling build backend, no runtime dependencies,
  optional test dependency `pytest`, optional docs dependency `pydoctor >=25.4.0`.
- Built wheel evidence: `docstring_parser-0.18.0-py3-none-any.whl`, 22,475
  bytes, digest
  `sha256:a128370304b5cadbb02856daf5d3572457c6b3cca0b7cbed8400cc2dd3dbf0ed`.
- Measured implementation size: 9 package Python files, 2,163 physical
  lines and 1,818 nonblank lines. The 9 test Python files add 4,041 physical
  lines; package plus tests total 6,204 physical lines. Under the repository's
  original LOC bands, the implementation is above the Easy `<=1500` boundary;
  catalog metadata records `medium` rather than repeating the candidate's
  `easy` label without measurement.

## Frozen test evidence

The pinned source contains 9 test Python files. With pytest 9.1.1, four
independent source-baseline runs were made; the first three are the requested
stable baseline evidence:

| Run | Collected | Passed | Failed | Errors | Skipped | Pass rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-1 | 254 | 254 | 0 | 0 | 0 | 1.0000 |
| baseline-2 | 254 | 254 | 0 | 0 | 0 | 1.0000 |
| baseline-3 | 254 | 254 | 0 | 0 | 0 | 1.0000 |
| Python 3.12 collection check | 254 | n/a | n/a | n/a | n/a | n/a |

These are direct frozen-source pytest baselines, not Harbor rewards: there is
no valid Harbor task or separate verifier to produce `grading.json`. The pinned
`python@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
image reports Python 3.12.14 and collected 254 tests.

## Why Harbor is blocked

1. The production separate-verifier protocol currently exposes JSON request /
   response calls and module/console execution only. The upstream assertions
   exercise rich in-process Python objects (`Docstring` and metadata subclasses,
   enums, parser instances), exact composition strings, decorators that mutate
   `__doc__`, `inspect.getsource`, and `unittest.mock.patch`. These behaviors
   cannot be preserved through the existing JSON-only candidate boundary.
   The upstream tests directly import the candidate package, so copying them
   into a trusted verifier would violate the repository's separate-verifier
   policy. No approved task-specific RPC adapter exists.
2. There is no authorized private `tests.test_bundle`, command-plan artifact,
   Oracle bundle, or content-addressed dependency artifact for this task. The
   task source intentionally leaves dependency provenance `unknown` and does
   not embed hidden tests or Oracle bytes.
3. The locked Python 3.12 base image has neither `hatchling` nor `pytest`. The
   package's `pip install .` build therefore fails in a no-network container
   with `BackendUnavailable: Cannot import 'hatchling.build'` unless a complete
   hash-locked offline build/test wheelhouse is supplied. The repository's
   verifier lock is not that candidate build closure.

Because these are verifier and dependency-closure blockers, generating a
`harbor/` directory, copying the public upstream tests into it, or claiming
three Harbor Oracle rewards would be misleading. The catalog task records the
verified source, behavior specification, frozen collection, and explicit
blocked state only.

## Commands and evidence

```text
GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none https://github.com/rr-/docstring_parser /tmp/docstring-parser-source
git -C /tmp/docstring-parser-source checkout --detach 8347d8fb347bd66e4bf5711d3df586357166944a
git -C /tmp/docstring-parser-source archive 8347d8fb347bd66e4bf5711d3df586357166944a | sha256sum
sha256sum /tmp/docstring-parser-source/LICENSE.md
uv run --no-project --with pytest==9.1.1 python -m pytest --collect-only -q
for run in 1 2 3; do uv run --no-project --with pytest==9.1.1 python -m pytest -q --junitxml="/tmp/docstring-parser-baseline-${run}.xml"; done
uv build --wheel --out-dir /tmp/docstring-parser-dist
uv run --frozen nl2repo task validate-source catalog/tasks/docstring-parser
uv run --frozen nl2repo harbor compile catalog/tasks/docstring-parser --output /tmp/docstring-parser-harbor-blocked
```

The JUnit files, wheel, and temporary source checkout are validation artifacts,
not task files and are not included in this worktree. Docker work was stopped
once the host-load steering arrived; the already-observed pinned image facts
and no-network build failure are retained above.

## Recommendation

Keep the task blocked. To reopen it, first approve and implement a
task-specific subprocess adapter that can represent the parsed object model,
composition, decorator, and source-inspection assertions without importing the
candidate in the trusted process. Then create private content-addressed test,
command, Oracle, and complete offline build/test dependency artifacts, rerun
collection in the final image, and run three independent valid Harbor Oracle
jobs before considering controls or publication.
