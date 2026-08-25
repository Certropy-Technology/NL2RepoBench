# Pandarallel Production Blocker

Status: `blocked` before production compilation.

## Evidence

- The existing Harbor runtime used the immutable legacy verifier image and ran
  pytest in the candidate process. It therefore did not meet the production
  requirement that trusted tests and report writing remain outside the process
  importing candidate code.
- The prior attempt at
  `.nl2repo/runs/oracle/vendor-audit-pandarallel/2026-08-24__21-31-21/`
  was invalid. Its `grading.json` recorded `valid=false`, `collected=0`,
  `reward=0.0`, and `reason=installation-failed`; the Oracle had no source-host
  authorization and left `/workspace` without `setup.py` or `pyproject.toml`.
- The pinned source was independently fetched and archived during this lane.
  The archive was 593,920 bytes and reproduced the catalog digest
  `sha256:e6248ba2a30d551242e03df5b83d71ff4ff63c4b9ada2ab8c3ba82b051e1b5cd`.
- A task-specific JSON subprocess adapter was drafted for the frozen 217-case
  inventory, but it was not executed in the compiled verifier environment.
- Hash-lock generation under Python 3.12 resolved the package set, but the
  generated file warned that setuptools was omitted from hash mode. The input
  was tightened, but the lock was not regenerated or validated before this
  lane was stopped. No dependency bytes were vendored.

## Runtime Decision

No production bundle was compiled with `--allow-incomplete` disabled. No
official Oracle was run, and the empty, stub, forgery, and offline controls were
not started because the Oracle gate was not valid with reward at least 0.80.

The stale generated Harbor runtime was removed. The pre-existing untracked
`catalog/tasks/pandarallel/environment/docker-compose.yaml` is intentionally
preserved byte-for-byte; its baseline SHA-256 is
`17ceef0a82e7dfb63d9f5ce974350f392dd8a323eac174ec69d28a90c7de8388`.

## Unblock Requirements

1. Regenerate and validate a complete Python 3.12 `requirements.lock.txt` with
   hashes for every requirement, including setuptools.
2. Package the task-specific verifier and pinned offline Oracle source as
   private content-addressed tar artifacts.
3. Compile without `--allow-incomplete`, then run exactly one official Oracle.
4. Proceed to empty, stub, forgery, and offline controls only if grading is
   valid, collection is exactly 217, and Oracle reward is at least 0.80.
