# retrying Repair Evidence

## Status

`oracle-passed`. The inherited `task.toml` already claimed `oracle-passed` ("three
independent Harbor Oracle runs") but carried no dependency bundle, no test
bundle and no Oracle bundle, so that claim could not be compiled or reproduced.
It has been replaced with evidence from a generic compiled run: the task now
compiles **without** `--allow-incomplete` (`publication_gaps() == ()`) and one
compiled Oracle run reports `valid=true`, `collected=23 == expected_total`,
`passed=23`, `reward=1.0`.

## Source and environment

- Upstream: `https://github.com/rholder/retrying`.
- Revision: `3a435e8ba85d85d7300a3609cb6f3ba8cb4bc170` (exact, as inherited).
- License: Apache-2.0 (`LICENSE` at the frozen revision).
- Archive digest: `sha256:de12f17823ab9b4d10e40e16afa94a77038c25df63b961279085948a3fffd6b3`,
  reproduced locally with `git archive --format=tar HEAD | sha256sum` after
  checking out the exact revision. It matches the inherited `source_digest`
  byte-for-byte, so the frozen content is unchanged by this repair.
- Base image: `python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a`
  (Python 3.12.14, debian 13).
- Lock detail: `evidence/environment-lock.json`, `evidence/wheelhouse.sha256`,
  `provenance/requirements.lock.txt`.

### Environment relock from 3.10.11 to 3.12.14 (required, not cosmetic)

The inherited task pinned `python:3.10.11`. The generic compiler emits a verifier
image that installs its trusted runtime at a hardcoded path:

```
COPY runtime/nl2repobench /usr/local/lib/python3.12/site-packages/nl2repobench
```

(`src/nl2repobench/harbor/compiler.py`, also used by the integrity snapshot/verify
steps). On `python:3.10.11` the real site-packages directory is
`/usr/local/lib/python3.10/site-packages`, so the compiled verifier cannot import
its own runtime. Editing `src/` was out of scope for this repair, and all 13
already-published tasks are on Python 3.12, so the environment was relocked to
`python:3.12-slim` instead. The frozen suite was confirmed to pass fully on
3.12.14 before relocking (23/23, 0.48s). `instruction.md` was updated to state
Python 3.12.14 and the actual frozen dependency versions.

Because the public instruction bytes changed, `version` was raised
`0.1.0 -> 0.2.0` and the reported Oracle run was re-executed against the final
published content.

## Frozen denominator

`expected_total = 23`, `expected_total_source = "frozen-collection"`. The 23 node
ids were collected from the frozen `test_retrying.py` with the reference
implementation installed and are pinned verbatim in the verifier as
`FROZEN_NODE_IDS`. Results are projected onto that fixed list, so a candidate
that breaks collection or deletes tests produces `failed` leaves rather than a
shrunken denominator. No rescope was needed: the legacy denominator of 23 is
preserved exactly.

## Verifier contract

`[verifier] protocol = "custom-json-v1"`, `entrypoint = "run.py"`, private
bundle `sha256:c426cc18d69a5e475788029880089293cfd645aab5c354c55ba9b11ed66a3207`
(30720 bytes). This replaces the legacy `tests.commands_artifact` path.

`run.py` is trusted and never imports candidate code. It stages the hidden slice
read-only, then runs `adapter.py` in a child process as
`runuser -u candidate -- python -I`, parses only the resulting JUnit XML with
`defusedxml`, and prints exactly one JSON line with 23 unique leaves. Because
`python -I` ignores `PYTHONPATH`, `adapter.py` inserts `/tmp/candidate-site` and
`/opt/candidate-dependencies/site` onto `sys.path` explicitly. The slice is pure
retry/stop/wait logic, so it is deterministic and offline.

The legacy `harbor/tests/` tree (image-pinned `grade.py` + `test.sh`, which ran
root pytest directly against the candidate) is no longer the execution path; the
compiled bundle uses the separate JSON verifier.

## Bundles

| Bundle | Digest | Size |
| --- | --- | --- |
| dependencies | `sha256:4e468399b6c5e50b21b8c796b0834c2b016f0f3957a3bea9c731f17fd133c705` | 3123200 |
| verifier | `sha256:c426cc18d69a5e475788029880089293cfd645aab5c354c55ba9b11ed66a3207` | 30720 |
| oracle | `sha256:065910fbea460d6448b74bfd40a719ff92763a6100ed179d8d924eb3d6560aa2` | 61440 |

All three are private and registered in `.nl2repo/artifacts`. The public catalog
holds only digest references: no wheels, no source archive, no hidden test bytes.

The dependency wheelhouse carries every wheel at the tar root plus a
`requirements.lock.txt` in which every pin has a `--hash=sha256:` line. It
includes `setuptools`/`wheel` because the candidate install runs
`pip install --no-deps --no-build-isolation`.

`solve.sh` in the Oracle bundle is purely local (`cp -a "$root/source/."
/workspace/`); it performs no `git fetch`, which matters because the agent phase
is `no-network` and a fetch would also leak the reference implementation. It
removes `test_retrying.py` from the workspace so a candidate-visible copy cannot
shadow the verifier-supplied hidden slice.

## Oracle and control evidence

Compile (no `--allow-incomplete`):

```
uv run nl2repo harbor compile catalog/tasks/retrying --toolchain toolchain.lock.toml \
  --output <tmp> --artifact-root .nl2repo/artifacts --allow-private
```

Runs used `scripts/harbor_safe_entry.py run -a oracle`. No non-oracle agent was run.

| Control | valid | collected | passed | reward | Jobs dir |
| --- | --- | --- | --- | --- | --- |
| Oracle (published content) | true | 23 | 23 | 1.0 | `.nl2repo/runs/oracle/retrying-published` |
| empty workspace | true | 0 | 0 | 0.0 | `.nl2repo/runs/oracle/retrying-empty` |
| stub package | true | 23 | 0 | 0.0 | `.nl2repo/runs/oracle/retrying-stub` |
| forgery | true | 23 | 0 | 0.0 | `.nl2repo/runs/oracle/retrying-forgery` |

Earlier confirming Oracle runs on the same bundles are under
`.nl2repo/runs/oracle/retrying-cmp` and `.nl2repo/runs/oracle/retrying-final`
(both `reward=1.0`).

The forgery control writes `/logs/verifier/reward.json`, `grading.json`,
`junit.xml`, `collection.json`, and attempts to overwrite `/tests/verifier/run.py`,
the hidden slice and the staged fixture, plus a `sitecustomize.py` for in-verifier
execution. The trusted `reward.json` still reported `0.0` and the denominator
stayed at 23, so grading is unaffected.

The verifier runs `no-network`; `network_check` passed in every run.
`uv run nl2repo task lint-network` reports `error_count = 0`. The one retrying
finding is `oracle-requires-host-authorization` (severity `warning`), which is
the expected state for a digest-verified Oracle fetch path and not a defect;
note the compiled Oracle here is fully local and needed no host authorization.

## Remaining gates

Blind review, spec traceability review and pilot are still pending, so this task
is `oracle-passed`, not `published`. Cross-run Oracle stability was not measured;
the current Package campaign contract requires one run.
