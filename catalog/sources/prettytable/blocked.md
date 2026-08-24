# prettytable candidate audit

Status: `blocked`

This evidence-first candidate targets `prettytable/prettytable` at a verified
immutable commit. It is audit-only, not a publishable task, Harbor bundle, or
legacy projection. No runtime exists at `catalog/tasks/prettytable/`.

## Candidate

| Field | Value | Evidence |
| --- | --- | --- |
| task id | `prettytable` | task-local candidate identity |
| upstream | `https://github.com/prettytable/prettytable.git` | `git ls-remote` resolves the commit as `HEAD` and `main` |
| revision | `3c80d392d32f48b0ab1e368793ddb751dbe41807` | full immutable commit SHA |
| tree | `26a1c631968582723400fc47f5c382966eecd3a7` | `git rev-parse 3c80d392d32f48b0ab1e368793ddb751dbe41807^{tree}` |
| archive | 409,600 bytes; `sha256:76f15330d9b102191694e8f0ef21632dfd80cdeb6ff5d14c95a8d21553052532` | unprefixed `git archive --format=tar` |
| license | BSD-3-Clause; `LICENSE` SHA-256 `0c8adcc204c8af6cdfdf7887dfd1f99c29901f6c1d505a78bba96efa4fb2cb05` | exact revision license bytes |
| language | Python | `pyproject.toml` project metadata |
| package manager | pip/build backend | `pyproject.toml` declares Hatchling/Hatch VCS and `wcwidth>=0.3.5` |

## Gate results

Source provenance and license are known. The production gate remains blocked
on the environment/dependency closure; no test, Oracle, or control pass is
inferred from static source inspection.

| Gate | Result | Evidence or blocker |
| --- | --- | --- |
| Exact source/archive | known | Commit, tree, archive size, and archive digest are recorded above. |
| License | known | `LICENSE` is BSD-3-Clause and its exact bytes are hashed above. |
| Environment/dependencies | blocked | No digest-pinned image or hash-locked `wcwidth`/build/test closure exists. |
| Generated package | blocked | The clean source checkout has no generated `src/prettytable/_version.py`; direct import fails with `ModuleNotFoundError`. |
| pytest/golden tests | not run | No final-image collection, stable leaf IDs, private tests, or frozen denominator exists. |
| separate verifier/controls | not run | No adapter, verifier, Oracle, empty/stub/forgery, or offline control assets exist. |

The source lock does not by itself prove the test denominator, dependency
determinism, verifier behavior, or publication eligibility.

## Unblock evidence

The following commands were run and their versions, exit codes, outputs, and
hashes are retained in `evidence/remediation.txt`:

```text
git ls-remote https://github.com/prettytable/prettytable.git HEAD refs/heads/main refs/tags/3.3.0
git clone --filter=blob:none --no-checkout --depth=1 https://github.com/prettytable/prettytable.git /tmp/nl2repo-prettytable-source.tp1jXi/source
git -C /tmp/nl2repo-prettytable-source.tp1jXi/source checkout --detach --quiet 3c80d392d32f48b0ab1e368793ddb751dbe41807
git -C /tmp/nl2repo-prettytable-source.tp1jXi/source archive --format=tar --output=/tmp/nl2repo-prettytable-source.tp1jXi/prettytable.tar 3c80d392d32f48b0ab1e368793ddb751dbe41807
uv run nl2repo task validate-source catalog/sources/prettytable
PYTHONPATH=/tmp/nl2repo-prettytable-source.tp1jXi/source/src python -c 'import prettytable; print(prettytable.__version__)'
uv run nl2repo harbor compile catalog/sources/prettytable --output /tmp/prettytable-blocked-compile --artifact-root .nl2repo/artifacts --toolchain toolchain.lock.toml
```

## Scope decision

The parseable `task.toml` is a blocked source descriptor only; no public task
instruction, hidden tests, Harbor/private assets, dependency cache, or shared
index was created. This candidate must stay blocked until the environment,
dependency, test, verifier, Oracle, and control gates have recorded evidence;
after that, rerun the publication checks before creating any runtime task.
