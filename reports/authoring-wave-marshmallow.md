# Marshmallow Authoring Wave Handoff

## Outcome

The marshmallow candidate was audited in the isolated worktree
`/tmp/pi-worktree-d05862bd-0109-4c63-8c79-e0970adf570f-0` and remains **blocked
for production authoring**. The only task-local worktree change is
`catalog/tasks/marshmallow/blocked.md`.

The pinned upstream checkout resolves exactly to
`c7b559a1fa3aba57ca6dba0ab336841c5038a782` with tree
`09ef226dec750308a6d2e8819487432a61b43aa4`. The unprefixed source archive
SHA-256 is
`c531024b6b6cf15be06fd2205f9304265524a3b1958e3e6c09793bc9b9f35728`; the MIT
`LICENSE` SHA-256 is
`906b5d9051e426144cb173ad911667b8ebd05a9c584c2c26c135b32a3ed12001`.

## Audit Findings

- API surface: root `__all__` has 14 names; `marshmallow.fields.__all__` has
  37 names. `Schema` supports bound field instances, nested schemas, `many`,
  partial/unknown handling, dump/load and dumps/loads through a configurable
  render module. Fields include callbacks, validators, nested classes or
  callables, generators/iterables, enums, UUID, Decimal, date/time, IP, and
  custom objects. `ValidationError` carries structured messages, raw data, and
  valid data.
- Collection: 12 test modules collect 1,188 unique nodes (652 static test
  definitions after parametrization). The pinned direct source suite passed
  `1188/1188` three times with pytest 9.1.1 and simplejson 4.1.1. The suite
  imports `simplejson` from `tests/base.py` during conftest collection; a clean
  collection without it exits 4 with `ModuleNotFoundError`.
- Dependencies: runtime metadata requires Python >=3.10, flit_core >=3.12,<4
  for builds, and conditional `backports-datetime-fromisoformat` plus
  `typing-extensions` below Python 3.11. Tests require pytest and simplejson;
  the source `uv.lock` is not an offline wheelhouse. No task-authorized
  dependency bundle, final image lock, private test bundle, command plan, or
  Oracle bundle is present.
- Optional integrations: `Schema.Meta.render_module` accepts stdlib json,
  simplejson, or a custom object with dumps/loads. Tests also use
  contextvars-based `experimental.context.Context`, timezone data for
  `America/Chicago`, callbacks, generators, and rich Python domain values.
- Determinism: three baselines have identical collection and pass/fail sets,
  but UUID/current-time fixtures are dynamic, set serialization follows input
  iteration order, and unknown-field error insertion order changes with
  `PYTHONHASHSEED` because the implementation iterates `set(data) - fields`.
  A verifier comparing serialized error bytes must pin the hash seed or
  normalize mappings.
- Candidate boundary: the generic Python `candidate_client.call` accepts one
  JSON module/attribute call per fresh UID-10001 child and JSON-serializes the
  result. It has no object handles, callback transport, persistent session,
  or marshmallow CLI. The frozen suite constructs fields/schemas, custom
  classes, callbacks, enums, dates, UUIDs, context scopes, nested caches, and
  structured exceptions in-process. Direct import from trusted pytest would
  violate the separate-verifier policy; flattening the suite requires an
  approved task-specific child adapter that does not exist.

The task-local evidence records the full API/serialization details, collection
shape, exact commands, source hashes, dependency caveats, determinism probe,
subprocess limitation, and reopen requirements without copying tests or other
private bytes.

## Validation

- `git -C /tmp/nl2repo-marshmallow-source rev-parse HEAD`: passed; exact
  requested SHA.
- `git archive --format=tar HEAD | sha256sum`: passed; archive hash recorded
  above.
- `sha256sum LICENSE`: passed; MIT license hash recorded above.
- `uv build --wheel --out-dir /tmp/marshmallow-dist`: passed; temporary wheel
  built outside the worktree.
- Pytest collection with pinned source/test extras: passed; 1,188 nodes.
- Three direct source baseline runs: passed; 1,188 passed each.
- Collection without simplejson: failed as intentionally probed; exit 4 at
  conftest import, establishing the required test dependency.
- Hash-seed determinism probe: passed as an audit probe; observed differing
  unknown-error mapping insertion order across seeds.
- Task diff check: passed; no whitespace errors.
- Staged-file check: passed; no staged files.
- Docker, Harbor, Oracle, private-artifact resolution, and negative controls:
  not run by lane policy.

## Acceptance

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Added only the requested task-local audit artifact catalog/tasks/marshmallow/blocked.md; no shared catalog, dataset, verifier, Docker, private test, or Oracle files were changed."
    }
  ],
  "changedFiles": [
    "catalog/tasks/marshmallow/blocked.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git -C /tmp/nl2repo-marshmallow-source checkout --detach c7b559a1fa3aba57ca6dba0ab336841c5038a782 && git -C /tmp/nl2repo-marshmallow-source rev-parse HEAD",
      "result": "passed",
      "summary": "Detached checkout resolved to the exact requested revision."
    },
    {
      "command": "git -C /tmp/nl2repo-marshmallow-source archive --format=tar HEAD | sha256sum",
      "result": "passed",
      "summary": "Produced the recorded source archive digest."
    },
    {
      "command": "uv build --wheel --out-dir /tmp/marshmallow-dist",
      "result": "passed",
      "summary": "Built the temporary marshmallow 4.3.1 wheel outside the worktree."
    },
    {
      "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src uv run --no-project --with pytest==9.1.1 --with simplejson==4.1.1 python -m pytest --collect-only -q -p no:cacheprovider",
      "result": "passed",
      "summary": "Collected 1,188 unique test nodes."
    },
    {
      "command": "for run in 1 2 3; do PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src uv run --no-project --with pytest==9.1.1 --with simplejson==4.1.1 python -m pytest -p no:cacheprovider -q --junitxml=/tmp/marshmallow-baseline-${run}.xml; done",
      "result": "passed",
      "summary": "Three direct source runs each passed 1,188 tests."
    },
    {
      "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src uv run --no-project --with pytest==9.1.1 python -m pytest --collect-only -q -p no:cacheprovider",
      "result": "failed",
      "summary": "Expected dependency probe: exit 4 because tests/base.py imports missing simplejson during conftest loading."
    },
    {
      "command": "git diff --no-index --check /dev/null catalog/tasks/marshmallow/blocked.md",
      "result": "passed",
      "summary": "No whitespace errors in the task-local artifact."
    },
    {
      "command": "git diff --cached --name-only",
      "result": "passed",
      "summary": "No staged files."
    }
  ],
  "validationOutput": [
    "Source HEAD c7b559a1fa3aba57ca6dba0ab336841c5038a782; archive SHA-256 c531024b6b6cf15be06fd2205f9304265524a3b1958e3e6c09793bc9b9f35728.",
    "Direct source collection: 1,188 unique nodes; baseline-1/2/3: 1,188 passed, 0 failed, 0 errors, 0 skipped each.",
    "No task.toml, instruction.md, harbor/, private test bundle, command plan, dependency wheelhouse, or Oracle bundle was created.",
    "Worktree status contains only untracked catalog/tasks/marshmallow/; no staged paths are present."
  ],
  "residualRisks": [
    "No final image/environment lock or hash-locked offline build/test dependency bundle is available.",
    "The generic JSON subprocess client cannot preserve marshmallow's in-process schema, field, callback, context, nested-cache, rich-exception, or domain-object semantics.",
    "The three passing baselines ran against the direct frozen source, not a final separate verifier image or Harbor Oracle."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added one task-local blocked.md audit; no implementation, shared metadata, Harbor bundle, tests, Docker asset, or Oracle artifact was added.",
  "reviewFindings": [
    "blocker: production publication is not safe until a task-specific child adapter and offline dependency/artifact closure are provisioned.",
    "no blockers in the task-local evidence artifact itself."
  ],
  "manualNotes": "Keep marshmallow blocked. Reopen only after final-image collection, private artifact resolution, adapter review, three valid Oracle runs, and empty/stub/forgery/offline controls."
}
```
