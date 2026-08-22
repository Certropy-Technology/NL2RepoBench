# cachetools authoring-wave handoff

## Implemented

Audited the exact candidate revision `01af8e5b7ce44432b357e26c7d67eb7fa055ae72`
from `reports/python-package-candidates.v1.md` and added only the task-local
catalog source under `catalog/tasks/cachetools/`:

- `task.toml`: declarative metadata with exact source lock, MIT license,
  provisional collection observation, dependency status, and lifecycle
  `blocked`;
- `instruction.md`: public behavior specification for the 18-name cache,
  decorator, convenience-decorator, and key-function API;
- `audit.md`: source/archive/license/LOC/API/packaging/collection/
  determinism/separate-verifier evidence and unblock conditions.

No Harbor tree, hidden test bytes, private artifact references, Oracle bundle,
Docker asset, shared index, dataset manifest, or legacy projection was created.

## Candidate evidence

- Detached public checkout resolved to the requested SHA; tag `v7.1.7`, commit
  date `2026-08-01T23:18:21+02:00`, tree
  `5a355d8586540978257589b42d6c6cb2c964bc12`, no submodules.
- Repeated unprefixed `git archive --format=tar HEAD`: 276,480 bytes,
  SHA-256 `67fe3a54397f9d1437464dfd149bdf54520a0c5a894eb4ab66eb1f37ea100449`.
- `LICENSE`: 1,085 bytes, SHA-256
  `28c000b52b0ee27138a68ef778227e4057046e86b65f62f1cacb99b0cc49e0d2`;
  source, GitHub license endpoint, and wheel metadata all identify MIT.
- Five implementation `.py` files: 1,637 physical / 1,325 nonblank /
  1,261 noncomment lines, reproducing the discovery report's SLOC.
- Public API count independently reproduced as 9 top-level + 5
  `cachetools.func` + 4 `cachetools.keys` names = 18.
- PyPI 7.1.7 hashes and source/wheel metadata are recorded in `audit.md`, but
  the benchmark source lock remains the immutable Git archive rather than the
  publicly downloadable distribution.
- Collect-only probe (CPython 3.14.6, pytest 9.1.1) exited 0 with no collection
  errors and observed 312 unittest items. Two runs were byte-identical. The
  candidate report's 132 statistic is the `test_`-prefix source-definition
  count; one collected method is named exactly `test`. `312` remains
  `expected_total_source = "unknown"` until a final verifier freezes it.

## Validation

- Parsed `catalog/tasks/cachetools/task.toml` with `tomllib`.
- `nl2repo task validate-source catalog/tasks/cachetools` passed; it reports
  task `cachetools`, version `0.1.0`, status `blocked`.
- Static source/test AST and import scans passed.
- Public source `compileall` passed; no full test body execution was performed.
- Task-local text/TOML check passed: no CR bytes or trailing whitespace.
- Git status shows only the intended untracked task-local directory; the index
  has no staged files.

## Lifecycle and residual blockers

The task is intentionally **blocked**, not publishable. Before advancing it,
parent orchestration must provide and review:

1. a final Python/OS/base-image lock and hash-locked offline build/test
   dependency bundle (the source has no runtime deps, but build and tox deps are
   unpinned);
2. private hidden tests, an allowlisted verifier command plan, and an Oracle
   bundle in the authorized visibility-separated store;
3. a cachetools-specific child-side adapter for callbacks, mutable/stateful
   caches, timers/`ttu`, custom subclasses, pickling, and threaded behavior;
4. final-environment collection and structured denominator/skip/xfail policy,
   followed by Oracle and empty/stub/forgery/offline controls; and
5. a reviewed no-network/contamination policy because `cachetools==7.1.7` is
   publicly available on PyPI.

No Docker, Oracle, hidden-test materialization, candidate/private-test cache or
artifact bytes, secret use, or shared-file mutation was performed.

## Acceptance report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only catalog/tasks/cachetools/task.toml, instruction.md, and audit.md were added; no shared index, generated Harbor asset, hidden test, Oracle, or unrelated source file was changed."
    }
  ],
  "changedFiles": [
    "catalog/tasks/cachetools/task.toml",
    "catalog/tasks/cachetools/instruction.md",
    "catalog/tasks/cachetools/audit.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "GIT_TERMINAL_PROMPT=0 git clone --filter=blob:none --no-checkout https://github.com/tkem/cachetools /tmp/cachetools-audit; git fetch --depth=1 origin 01af8e5b7ce44432b357e26c7d67eb7fa055ae72; git checkout --detach 01af8e5b7ce44432b357e26c7d67eb7fa055ae72",
      "result": "passed",
      "summary": "Detached checkout resolved to the exact requested revision and remained clean."
    },
    {
      "command": "git archive --format=tar HEAD | sha256sum (repeated)",
      "result": "passed",
      "summary": "Both archives matched: 276480 bytes, sha256 67fe3a54397f9d1437464dfd149bdf54520a0c5a894eb4ab66eb1f37ea100449."
    },
    {
      "command": "tomllib parse of catalog/tasks/cachetools/task.toml",
      "result": "passed",
      "summary": "Declarative task source parsed successfully."
    },
    {
      "command": "/root/NL2RepoBench/.venv/bin/nl2repo task validate-source catalog/tasks/cachetools",
      "result": "passed",
      "summary": "Source validator accepted task cachetools and preserved blocked lifecycle."
    },
    {
      "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/cachetools-audit/src /root/NL2RepoBench/.venv/bin/pytest --collect-only -q -p no:cacheprovider tests",
      "result": "passed",
      "summary": "Collect-only exited 0 with no collection errors and 312 items; repeated output matched."
    },
    {
      "command": "python3 -m compileall -q /tmp/cachetools-audit/src/cachetools /tmp/cachetools-audit/tests",
      "result": "passed",
      "summary": "Public source and tests compiled without syntax errors; no test bodies were run."
    },
    {
      "command": "task-local TOML/text validation and staged-file check",
      "result": "passed",
      "summary": "No CR bytes/trailing whitespace; no staged files."
    }
  ],
  "validationOutput": [
    "Source archive and MIT license hashes are recorded in catalog/tasks/cachetools/audit.md.",
    "Source SLOC is independently 1261 noncomment lines; public API inventory is 18 names.",
    "Collection observation is 312 items in one probe environment and is explicitly not frozen.",
    "Lifecycle is blocked with explicit dependency, verifier-adapter, private-artifact, and Oracle gates."
  ],
  "residualRisks": [
    "No hash-locked build/test dependency bundle or immutable verifier image exists.",
    "312-item collection has not been frozen in the production verifier; the candidate report's 132 is only a static naming count.",
    "Generic JSON candidate_client cannot represent callbacks, descriptors, timers, custom mappings, pickling, or threading without a child-side adapter.",
    "Default RR/LFU/time/thread behavior requires explicit determinism and resource policy.",
    "Public PyPI cachetools 7.1.7 creates source-contamination risk unless network policy is enforced."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added a blocked, task-local cachetools declarative source, public instruction, and static audit; no generated Harbor or shared catalog artifacts.",
  "reviewFindings": [
    "No task-local format or provenance blockers remain in the authored files.",
    "Publication blocker is intentional and documented: final environment, private artifacts, Oracle, and separate-verifier adapter are absent."
  ],
  "manualNotes": "Parent should preserve the blocked lifecycle. The exact source lock is the Git archive hash above; 312 is a collect-only observation, not an Oracle denominator or pass result."
}
```
