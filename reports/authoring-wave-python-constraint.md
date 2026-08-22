# `python-constraint` Authoring-Wave Handoff

## Outcome

The existing `catalog/tasks/python-constraint/` pilot was independently
revalidated and remains **blocked**. The exact requested source is healthy in a
local compiled source baseline, but the task cannot safely advance to Harbor or
Oracle authoring from the current evidence.

The repair changed only:

- `catalog/tasks/python-constraint/blocker.md`
- `reports/authoring-wave-python-constraint.md` (this report)

The existing public `task.toml` and `instruction.md` were intentionally left
unchanged. No hidden/private bytes, Dockerfile, Harbor tree, Oracle solution,
private command/test artifact, shared index, or legacy projection was created.

## Source, license, and archive evidence

A public checkout at `/tmp/python-constraint-audit-src` was detached at
`d91ba03d1fd6acc30d64fd9d513dc0523f697b5b`.

- Resolved tree: `a2f6010080fc1518988e86bcbb8de1b4bfb233cf`
- Commit date: `2026-08-18T16:06:43+02:00`
- Subject: `Updated changelog before release`
- Submodules: none
- Three unprefixed `git archive --format=tar HEAD` runs were identical:
  - size `7,618,560` bytes
  - SHA-256 `c15171bf0b6e8271e099566d5acef4c322e2d2efa13dd1f92cb3370b5f4675ff`
- `LICENSE`:
  - Git blob `1551a23ae2154250683c4e52001ade66e147d5cd`
  - `1,335` bytes / `23` lines
  - SHA-256 `e5894c331ba462210b707470b25f61ccd46bdadec5ee8290e71482a74742b62c`
  - byte-identical to the pinned raw GitHub URL
  - matches the `BSD-2-Clause` declaration in `pyproject.toml`

Independent line/API inventory reproduced `3,235` package lines,
`4,148` package-plus-example lines, `5,819` tracked Python lines, and 43
non-underscore top-level definitions (30 classes and 13 functions).

## Build and dependency evidence

`pyproject.toml` declares distribution `python-constraint2` version `2.7.3`,
Python `>=3.11`, no runtime `Requires-Dist`, and a Poetry build backend with
build roots `poetry-core>=2.4.1`, `setuptools>=84.0.0`, and `Cython>=3.2.9`.
The test group has lower bounds for pytest, pytest-benchmark, pytest-cov,
nox, ruff, and pep440. The source has no `poetry.lock`, `uv.lock`,
hash-bearing requirements file, or offline wheelhouse.

On the audit host (Fedora 44, CPython 3.12.11), a temporary environment
resolved the exact roots used by the prior evidence record:

```text
poetry-core==2.4.1
setuptools==84.0.0
Cython==3.2.9
pytest==9.1.1
pytest-benchmark==5.2.3
pytest-cov==7.1.0
pep440==0.1.2
```

Its transitive resolution included coverage 7.15.4, iniconfig 2.3.0,
packaging 26.3, pluggy 1.6.0, py-cpuinfo 9.0.0, and Pygments 2.21.0. With
those roots preinstalled, this source install succeeded:

```text
python -m pip install --no-index --no-build-isolation --no-deps -e .
```

The installed metadata reported version 2.7.3, no runtime requirements, and
five Cython extension modules. A fresh empty-cache `uv pip install --offline`
probe intentionally failed because `poetry-core` was unavailable, confirming
that network resolution is not an offline dependency closure.

A temporary wheel metadata/content probe found no `examples/`, `tests/`, or
`README.rst` in the wheel (the license was present). The wheel was not kept as
a task artifact. Docker was not used, so the recorded Debian 13 image and
system-package pins were not freshly verified here; the local host is not the
final verifier environment. The current task metadata also says
`network_mode = "public"`, which remains a source-contamination risk.

## Collection and baseline evidence

Using the task's explicit `--no-cov` mode and cache-disabled collection:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --no-project \
  --with pytest==9.1.1 --with pytest-benchmark==5.2.3 \
  --with pytest-cov==7.1.0 --with pep440==0.1.2 \
  python -m pytest --no-cov --collect-only -q -p no:cacheprovider tests
```

- Pure source collection: 49 nodes
- Source node-list SHA-256:
  `7b03bcce47e67115e757dbf8916060e2696c1a592c4e1288f15f18d315216266`
- After the temporary editable build produced C extensions: 52 nodes
- Compiled node-list SHA-256:
  `284b59ee7eb251b9d876a9b2686d2ca49535867f8027c8310b460b3d2df2a110`

Three compiled direct-source runs each produced 52/52 passed, zero failures,
zero errors, and zero skips. JUnit testcase/status sets were byte-stable at
SHA-256
`205b619be74070c61efbdc6bacfacebf7d0dc18173928fb3f2a97640a576b233`.
These are source baselines, not Harbor Oracle results or `valid=true` records.

The intended no-extension branch (compiled files present but renamed by
`tests/setup_teardown.py`) produced 49 passed and one benchmark-module skip.
A completely source-only checkout with no extension files failed
`test_if_compiled` while the remaining tests passed. This exposes a real task
contract decision: the public instruction calls Cython optional, but the
compiled default suite includes one compilation test and three benchmark
nodes. The final verifier must freeze either a compiled mode or an explicitly
adapted pure-Python mode before `expected_total = 52` can be a denominator.

## Traceability and verifier findings

The existing instruction remains byte-identical (SHA-256
`c17404a568ba5400fc543f0d49b1c0dfc6297401b10ae329f5df87deb5f8a168`), but the
source/test audit found these gaps:

- Twelve collected tests import the upstream `examples/` modules, while the
  public specification names only the `constraint` package and does not require
  the example tree.
- `test_toml_file.py` reads `pyproject.toml` and `README.rst` and checks exact
  metadata fields beyond the instruction's generic packaging statement.
- Module and README doctests execute candidate code in process; the instruction
  does not require the README fixture or all code blocks.
- Parser tests inspect concrete specialized constraint types and the private
  `_maxprod` field, while the instruction describes only the broad parser
  result shape.
- The generic verifier protocol creates a fresh JSON child per operation and
  has no handles, session, callback transport, or task-specific driver.

A direct probe of the current `candidate_runner` showed:

| Operation | Observation |
| --- | --- |
| `check_if_compiled()` | JSON boolean response succeeds |
| `Problem()` | child exits while serializing a non-JSON `Problem` object |
| `parse_restrictions(...)` | string-only result can serialize |
| `compile_to_constraints(...)` | child exits while serializing a `FunctionConstraint` |

The frozen assertions need one live `Problem` across mutations, lambdas and
custom constraint/domain subclasses, forward-check state, lazy iterators,
module/README doctests, examples, and thread/process solver behavior. Direct
trusted pytest imports would violate the separate-verifier policy; moving tests
into a candidate-owned driver would make them forgeable. A reviewed stateful
child-side RPC/driver is therefore required before authoring can continue.

## Recommendation and reopen conditions

Keep lifecycle `blocked`; do not create a Harbor bundle or run Oracle. Reopen
only after:

1. an approved, versioned instruction or adapted-scope repair covers examples,
   packaging metadata, README/doctests, parser specialization, and the
   compiled-vs-pure-Python choice;
2. a task-specific child-side adapter preserves state, callbacks, subclasses,
   iterators, and process-mode semantics without trusted direct candidate
   imports;
3. a final immutable image/environment lock and hash-locked offline dependency
   bundle exist;
4. final-image collection, JUnit, denominator, skip/benchmark, and
   collection-mismatch semantics are frozen; and
5. private tests/commands/Oracle artifacts, Oracle x3, empty/stub/forgery/
   offline controls, and blind/spec review are completed.

No Docker, Harbor, Oracle, private-artifact materialization, or negative-control
execution was performed in this lane.

## Validation commands

The command-level evidence below is deliberately limited to public source,
local temporary environments, static/protocol probes, and catalog validation.

- `git clone --filter=blob:none --no-checkout ...` plus detached checkout of
  the requested SHA — passed; exact commit and tree resolved.
- `git archive --format=tar HEAD | sha256sum` (three runs) — passed; identical
  7,618,560-byte archives and recorded digest.
- `curl .../<SHA>/LICENSE`, `sha256sum`, and `cmp` — passed; remote and checkout
  license bytes identical.
- Temporary dependency resolution and
  `python -m pip install --no-index --no-build-isolation --no-deps -e .` —
  passed; metadata and five extensions verified.
- Empty-cache `uv pip install --offline ...` — expected nonzero observed and
  captured; no offline closure exists.
- Source and compiled `pytest --collect-only` — passed; 49 and 52 nodes with
  stable node-list digests.
- Three compiled `pytest --no-cov ... --junitxml=...` runs — passed; 52/52 each
  with stable JUnit testcase/status digest.
- No-extension source probes — expected mode mismatch observed; this is why
  the Cython/test-mode decision remains a blocker.
- Direct local `candidate_runner.py` JSON probes — passed as protocol evidence;
  object-returning operations failed closed without a result prefix.
- `uv run nl2repo task validate-source catalog/tasks/python-constraint` —
  passed; task remains `blocked`.
- `git diff --check` and staged-path inspection — passed; no staged files.

## Acceptance report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Revalidated and sharpened only the existing python-constraint pilot blocker; preserved task.toml and instruction.md, and created no Harbor, hidden/private, Docker, Oracle, or shared-index artifacts."
    }
  ],
  "changedFiles": [
    "catalog/tasks/python-constraint/blocker.md",
    "reports/authoring-wave-python-constraint.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git clone/fetch/checkout python-constraint at d91ba03d1fd6acc30d64fd9d513dc0523f697b5b; git rev-parse HEAD and HEAD^{tree}",
      "result": "passed",
      "summary": "Exact requested revision and tree resolved in a detached public checkout."
    },
    {
      "command": "git archive --format=tar HEAD | sha256sum (three independent runs)",
      "result": "passed",
      "summary": "All three 7,618,560-byte archives matched SHA-256 c15171bf0b6e8271e099566d5acef4c322e2d2efa13dd1f92cb3370b5f4675ff."
    },
    {
      "command": "curl pinned LICENSE; sha256sum; cmp against checkout LICENSE",
      "result": "passed",
      "summary": "BSD license bytes matched; SHA-256 e5894c331ba462210b707470b25f61ccd46bdadec5ee8290e71482a74742b62c."
    },
    {
      "command": "temporary CPython 3.12.11 dependency resolution and pip install --no-index --no-build-isolation --no-deps -e .",
      "result": "passed",
      "summary": "Build/test roots resolved; distribution metadata was 2.7.3 with no runtime dependencies and five extensions."
    },
    {
      "command": "UV_CACHE_DIR=/tmp/python-constraint-empty-uv-cache uv pip install --offline ...",
      "result": "passed",
      "summary": "Expected offline negative probe was captured and asserted nonzero because poetry-core was absent from the empty cache."
    },
    {
      "command": "pytest --no-cov --collect-only -q -p no:cacheprovider tests (source and compiled modes)",
      "result": "passed",
      "summary": "Collected stable 49-node source and 52-node compiled suites with recorded node-list digests."
    },
    {
      "command": "three compiled pytest --no-cov runs with JUnit and benchmark output",
      "result": "passed",
      "summary": "Each run passed 52/52 with zero failures/errors/skips and the same testcase/status digest."
    },
    {
      "command": "source-only and renamed-extension no-extension pytest probes",
      "result": "failed",
      "summary": "Expected mode distinction observed: bare source fails test_if_compiled; the intended renamed-extension branch passes 49 and skips one benchmark module."
    },
    {
      "command": "direct candidate_runner.py JSON probes for scalar, Problem, parse_restrictions, and compile_to_constraints",
      "result": "passed",
      "summary": "Scalar/string-only values serialize; Problem and Constraint objects fail at the JSON boundary, confirming the blocker."
    },
    {
      "command": "uv run nl2repo task validate-source catalog/tasks/python-constraint",
      "result": "passed",
      "summary": "Declarative catalog source parsed and remains lifecycle blocked."
    },
    {
      "command": "git diff --check && git diff --cached --name-only",
      "result": "passed",
      "summary": "No whitespace errors and no staged files."
    },
    {
      "command": "Docker, Harbor, Oracle, private artifact materialization, and negative controls",
      "result": "not-run",
      "summary": "Explicitly excluded by the assigned audit scope."
    }
  ],
  "validationOutput": [
    "Exact revision, tree, archive, license bytes, package metadata, source LOC, and public API inventory were revalidated.",
    "Compiled local source baselines are stable at 52/52; source/no-extension behavior exposes an unresolved test-mode contract.",
    "The public instruction omits the examples fixture tree and several packaging/doctest/compiled assertions; it was intentionally not changed.",
    "The generic JSON candidate boundary cannot preserve the frozen stateful/callback/subclass/iterator/process semantics.",
    "No final immutable image, offline dependency closure, private artifacts, Oracle, or controls exist in this lane."
  ],
  "residualRisks": [
    "No final verifier image or Debian/system-package validation was run; local baselines used Fedora 44 and CPython 3.12.11.",
    "No hash-locked offline build/test wheelhouse exists; the empty-cache probe fails before installation.",
    "The current public specification has untracked requirements for examples, README/doctests, exact packaging metadata, parser specialization, and compiled-vs-pure-Python mode.",
    "The current task metadata permits public network access, leaving source-contamination policy unresolved.",
    "A task-specific stateful child adapter and all Oracle/control/private-artifact gates remain absent."
  ],
  "noStagedFiles": true,
  "diffSummary": "Replaced the stale task-local blocker with a source/license/archive, dependency, collection, traceability, and candidate-boundary revalidation; added this handoff report. Public task.toml and instruction.md were not changed.",
  "reviewFindings": [
    "blocker: current JSON candidate boundary cannot preserve Problem state, callbacks, subclasses, iterators, doctests, examples, or process-mode semantics",
    "blocker: instruction.md does not specify the examples tree, exact packaging fixtures, README/doctest contract, or compiled-vs-pure-Python test mode",
    "blocker: no immutable final image or hash-locked offline dependency bundle exists",
    "blocker: expected_total=52 is only a local compiled-suite observation until final collection and metric semantics are frozen",
    "no additional scope files or artifacts were changed"
  ],
  "manualNotes": "Keep python-constraint blocked. Parent approval is required before changing instruction/task version, introducing a stateful adapter, or narrowing the measured suite. No routine Oracle or Harbor handoff was performed."
}
```
