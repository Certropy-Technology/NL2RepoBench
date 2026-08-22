# Research: Resuming GPT-5.6/Fable5 Trials After the Interrupted `new6` Campaign

> **Historical preflight with current-state addendum.** Since this audit was
> written, `run_harbor_model.sh` stopped putting `LLM_API_KEY` in Harbor argv,
> the selected Docker environment delivers that value over stdin to a fixed
> container wrapper, and regression tests assert that the sentinel is absent
> from Harbor/Docker argv and launcher output. The uploader now strips legacy
> `new6` markers when identifying tasks, archives per-root `queue.log` files
> under `_queue-logs`, and can emit a local key/size/SHA-256 manifest. The
> existence-only remote deduplication warning remains unresolved: do not use
> `--overwrite`, and perform remote collision checks before upload. The older
> parallel wrappers remain unsupported for secure resume.

## Summary

The canonical run artifacts are under `/root/NL2RepoBench/.nl2repo/runs/`; the queue logs were also visible from the `/data/NL2RepoBench-current` checkout, but completed Harbor `result.json`, `lock.json`, and verifier artifacts resolve under `/root/NL2RepoBench`. The interrupted campaign contains **four valid terminal Fable5 trials, one terminal-but-invalid GPT trial, three incomplete trials, and four task/model cells that were not started**.

A resume must use fresh run roots. Reusing the old roots risks mixing canceled Harbor jobs with new results, and `resume_trajectory` was `false` in the old lock files. Before any model execution, two blockers should be addressed: (1) the launcher currently places `LLM_API_KEY` in Harbor’s command-line `--ae` argument, so the handoff is not strictly environment-only; and (2) the OSS classifier mis-parses existing `gpt56-new6-*`/`fable-new6-*` job names as tasks such as `new6-markupsafe`.

## Findings

### 1. Canonical artifact location and interruption boundary — **MEDIUM**

The source checkout currently points to commit `93b38e23650de47f52ad97d23ef0ffbbfe3c3303` ([`/root/NL2RepoBench/.git/refs/heads/main`](file:///root/NL2RepoBench/.git/refs/heads/main)). However, the interrupted run records do not embed a source commit in their queue metadata. The Harbor locks do retain task-bundle digests and task paths.

The authoritative queue logs are:

- [`/root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/queue.log`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/queue.log)
- [`/root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/queue.log`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/queue.log)

Both logs stop without `queue_complete`. The GPT log ends during `unidecode`; the Fable log ends during `voluptuous`.

The queue return code is not sufficient to determine success: GPT `markupsafe` logged `rc=0`, but its Harbor result was an errored/invalid trial. The authoritative status must come from `result.json` plus `verifier/grading.json`, not queue `rc`.

### 2. Exact model/task trial matrix

Expected frozen totals come from the task TOMLs: markupsafe 39, tablib 172, unidecode 65, unittest-parametrize 26, voluptuous 152, and xlrd 84.

| Model | Task | State | Evidence | Score/action |
|---|---|---|---|---|
| GPT-5.6 | `markupsafe` | **Terminal, invalid** | [`result.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/gpt56-new6-markupsafe/2026-08-21__18-53-14/result.json): `finished_at` set, one errored trial. [`grading.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/gpt56-new6-markupsafe/2026-08-21__18-53-14/harbor__QrsGh52/verifier/grading.json): `valid=false`, `reason=junit-missing`, `expected=39`, `collected=0`. | Do not count reward 0 as a model score. Fresh trial required if a complete valid matrix is desired. |
| GPT-5.6 | `tablib` | **Incomplete/canceled** | [`result.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/gpt56-new6-tablib/2026-08-21__18-59-45/result.json): `finished_at=null`, `n_cancelled_trials=1`, `CancelledError`; no grading file. | Fresh run ID required. |
| GPT-5.6 | `unidecode` | **Incomplete/interrupted** | [`result.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/gpt56-new6-unidecode/2026-08-21__20-20-31/result.json): `finished_at=null`, one running trial at interruption. [`trial.log`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/gpt56-new6-unidecode/2026-08-21__20-20-31/harbor__BcxBztf/trial.log) records a Harbor event-loop/context cleanup failure and no verifier grading. | Fresh run ID required; review as infrastructure/harness failure, not model score. |
| GPT-5.6 | `unittest-parametrize` | **Not started** | No `start` entry or task log before the GPT queue stopped. | Fresh run ID required. Confirm with a filesystem scan before launch. |
| GPT-5.6 | `voluptuous` | **Not started** | No `start` entry or task log before the GPT queue stopped. | Fresh run ID required. |
| GPT-5.6 | `xlrd` | **Not started** | No `start` entry or task log before the GPT queue stopped. | Fresh run ID required. |
| Fable5 | `markupsafe` | **Terminal, valid** | [`grading.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-markupsafe/2026-08-21__18-53-58/harbor__PaYkYHW/verifier/grading.json): `valid=true`, 39/39 effective tests, reward 1.0. | Preserve; do not rerun. |
| Fable5 | `tablib` | **Terminal, valid** | [`grading.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-tablib/2026-08-21__19-12-10/harbor__pWXHZjH/verifier/grading.json): 147/172, reward `0.8546511627906976`. | Preserve; do not rerun. |
| Fable5 | `unidecode` | **Terminal, valid** | [`grading.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-unidecode/2026-08-21__19-44-53/harbor__XRMQK7S/verifier/grading.json): 64/65, reward `0.9846153846153847`. | Preserve; do not rerun. |
| Fable5 | `unittest-parametrize` | **Terminal, valid** | [`grading.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-unittest-parametrize/2026-08-21__20-02-10/harbor__rJ3sNSA/verifier/grading.json): 22/26, reward `0.8461538461538461`. | Preserve; do not rerun. |
| Fable5 | `voluptuous` | **Incomplete/interrupted** | [`result.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-voluptuous/2026-08-21__20-11-44/result.json): `finished_at=null`, one running trial; no verifier grading. | Fresh run ID required. |
| Fable5 | `xlrd` | **Not started** | No `start` entry or task log after `voluptuous` in the Fable queue. | Fresh run ID required. |

The old `markupsafe` GPT run is terminal in the process sense but not valid in the benchmark-metric sense. The repository’s scoring contract explicitly treats `valid=false` as a task/environment result rather than a model score ([`docs/run-artifacts-oss.md`](file:///root/NL2RepoBench/docs/run-artifacts-oss.md)).

### 3. Model/config field audit — **MEDIUM**

The relevant configuration layers use different field names:

- Legacy [`config.json`](file:///data/NL2RepoBench-current/config.json): `startPro[].moduleName`, `baseUrl`, `sk`, and `proNameList`. This is not the modern Harbor queue interface and should not be used for the resume.
- Pi settings [`/root/.pi/agent/settings.json`](file:///root/.pi/agent/settings.json): includes `defaultProvider`, `defaultModel`, and `defaultThinkingLevel`. The observed defaults identify the GPT relay/provider and `gpt-5.6-sol`, but the file also contains unrelated sensitive settings and must not be copied wholesale.
- Pi model configuration [`/root/.pi/agent/models.json`](file:///root/.pi/agent/models.json): provider-oriented fields are `providers`, provider `baseUrl`, `api`, `apiKey`, and `models[]`; model entries use `id` and other model metadata. No credential value is reproduced here.
- Pi auth file [`/root/.pi/agent/auth.json`](file:///root/.pi/agent/auth.json): observed as an empty JSON object, so the resume must not assume that the relay credential is available there.
- Modern Harbor launcher ([`scripts/run_harbor_model.sh`](file:///root/NL2RepoBench/scripts/run_harbor_model.sh)): requires `MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY`; it also passes retry and reasoning fields.
- Serial queue ([`scripts/run_model_queue.sh`](file:///root/NL2RepoBench/scripts/run_model_queue.sh)): requires `TASKS`, `MODEL`, `LLM_BASE_URL`, and `LLM_API_KEY`; it inherits the API key from its parent shell and does not itself print it.

Pi’s documented custom-model schema confirms the `baseUrl`/`api`/`apiKey`/`models` field names and supports environment-variable or command-based key resolution ([Pi models documentation](https://pi.dev/docs/latest/models)). A metadata-only audit should print only provider name, model ID, API type, endpoint, and credential source class (`literal`, `environment-reference`, `command`, `auth-file`, or `missing`), never the value.

### 4. Credential handoff is not currently environment-only — **HIGH/BLOCKER**

The current custom adapter is otherwise designed to keep the key out of artifacts:

- [`src/nl2repobench/harbor_openhands.py`](file:///root/NL2RepoBench/src/nl2repobench/harbor_openhands.py) calls `_get_env("LLM_API_KEY")`, builds an `env` dictionary, and passes the key to the agent container through `environment.exec_as_agent(..., env=env)`.
- Harbor’s installed [`BaseAgent`](file:///root/NL2RepoBench/harbor-runner/.venv/lib64/python3.14/site-packages/harbor/agents/base.py) resolves environment values from extra-agent environment first and then `os.environ`. Therefore, if the key is exported only in the launcher’s subshell, the adapter can still consume it without an `--ae` entry.
- Existing [`lock.json`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/fable-new6-markupsafe/2026-08-21__18-53-58/harbor__PaYkYHW/lock.json) records `LLM_API_KEY` as a placeholder, which is good artifact redaction but does not prove that the host process command line was safe.

The problem is in [`scripts/run_harbor_model.sh`](file:///root/NL2RepoBench/scripts/run_harbor_model.sh): it currently contains:

```text
--ae "LLM_API_KEY=$LLM_API_KEY"
```

That interpolates the secret into Harbor’s process argument vector. It may not be persisted in `lock.json`, but it is not “child-process environment only” and can be visible through process inspection while Harbor is running.

The older parallel wrappers are worse: [`scripts/run_batch_claude.sh`](file:///root/NL2RepoBench/scripts/run_batch_claude.sh) and [`scripts/run_batch_pilot.sh`](file:///root/NL2RepoBench/scripts/run_batch_pilot.sh) pass `LLM_API_KEY="$LLM_API_KEY"` directly to an `env` command.

**Required security gate before resume:**

1. Keep the key in a short-lived subshell environment, resolved in memory from the Pi provider/model configuration.
2. Remove the secret `--ae "LLM_API_KEY=..."` argument from `run_harbor_model.sh`; retain nonsecret `LLM_BASE_URL` and retry settings if desired.
3. Add a regression test to [`tests/test_model_runner.py`](file:///root/NL2RepoBench/tests/test_model_runner.py) that captures the fake Harbor/`uv` argv and asserts neither `LLM_API_KEY=` nor the sentinel secret occurs in argv or stdout.
4. Use `run_model_queue.sh`, not the parallel wrappers.
5. If the launcher cannot be changed, do not claim env-only credential handling; obtain an explicit security exception before running.

The previous campaign may have exposed the relay key to the host process table even though the saved Harbor locks were redacted. Rotate the relay credential before resuming if process-table exposure is considered possible.

### 5. New run-ID scheme must avoid the `new6` infix — **HIGH**

The uploader recognizes only these job-name prefixes:

```python
MODEL_BY_PREFIX = {
    "gpt56-": "gpt-5.6-sol",
    "fable-": "claude-fable-5",
}
```

The existing queue generated child directories such as:

```text
gpt56-new6-markupsafe
fable-new6-markupsafe
```

In [`scripts/upload_runs_to_oss.py`](file:///root/NL2RepoBench/scripts/upload_runs_to_oss.py), `task_from_prefixed_run()` removes the model prefix and then searches for a catalog task at the beginning of the remainder. For `gpt56-new6-markupsafe`, the remainder is `new6-markupsafe`, so the current catalog does not match `markupsafe`; the fallback task becomes `new6-markupsafe`. This is inconsistent with the intended behavior tested by [`tests/test_upload_runs.py`](file:///root/NL2RepoBench/tests/test_upload_runs.py), where the task immediately follows the model prefix.

Use:

```text
RUN_PREFIX=gpt56
RUN_PREFIX=fable
```

and put uniqueness only in a new run root:

```text
batch-gpt-resume-<UTC timestamp>
batch-fable-resume-<UTC timestamp>
```

The resulting child job directories are:

```text
gpt56-markupsafe
gpt56-tablib
fable-voluptuous
fable-xlrd
```

These parse as the intended tasks. If a single-task direct invocation needs an attempt suffix, use `gpt56-markupsafe-resume1` or `fable-xlrd-resume1`; the task still immediately follows the recognized prefix.

Never reuse the old `batch-*-new6-20260821T` roots. Fresh roots preserve all original artifacts and make the OSS trial segment unique.

### 6. OSS upload and deduplication are existence-based, not content-based — **HIGH**

[`upload_runs_to_oss.py`](file:///root/NL2RepoBench/scripts/upload_runs_to_oss.py) uses:

```python
if not overwrite and bucket.object_exists(item.key):
    return "skipped"
```

There is no SHA256 comparison, size verification, or conditional content match. A different local file at an existing key is silently skipped unless `--overwrite` is used. `--overwrite` is unsafe for this resume because it could replace historical artifacts.

The uploader also has an archive-layout mismatch:

- [`run_model_queue.sh`](file:///root/NL2RepoBench/scripts/run_model_queue.sh) writes `queue.log` and `<task>.log` inside each run root.
- `iter_run_uploads()` recursively classifies those files as run artifacts.
- The `_queue-logs/` branch only handles files directly under the outer `runs_dir`.
- Consequently, a root-level `queue.log` inside `batch-gpt-new6-20260821T` falls back to a task name based on the entire run-root name rather than `_queue-logs/queue.log`.

Before upload:

1. Build a content manifest of every planned local object: OSS key, byte size, and SHA256.
2. Run the uploader’s dry-run from the canonical checkout and inspect **all** planned keys; the built-in dry-run prints only the first 20.
3. Assert that all model-run keys have the form:

   ```text
   nl2repobench/runs/gpt-5.6-sol/<canonical-task>/<new-root>--<trial>/...
   nl2repobench/runs/claude-fable-5/<canonical-task>/<new-root>--<trial>/...
   ```

4. Reject any key under `new6-*`, `unknown`, or a task equal to a batch-root name.
5. For an existing remote key, compare a remote SHA256/custom metadata value where available; otherwise download to a temporary location and hash it. Same hash may be recorded as an idempotent skip; different hash is a hard stop.
6. Do not pass `--overwrite`.
7. Either patch the uploader to special-case per-root queue logs, or stage copies with unique names outside the canonical run roots. Do not rename or modify the original campaign artifacts.

The live OSS object state was not queried during this read-only audit, so it is unknown whether earlier `new6-*` keys already exist.

## Concrete bounded resume plan

### Phase A — read-only preflight

Run from the artifact-owning checkout:

```bash
cd /root/NL2RepoBench

test "$(git rev-parse HEAD)" = "93b38e23650de47f52ad97d23ef0ffbbfe3c3303"
git diff --quiet
uv run --frozen --project harbor-runner harbor --version

find .nl2repo/runs/batch-gpt-new6-20260821T \
     .nl2repo/runs/batch-fable-new6-20260821T \
     -type f \( -name result.json -o -name grading.json -o -name lock.json \) \
     -print
```

Confirm:

- no old queue/Harbor process is still active;
- no stale `harbor__*` container is attached to a live queue;
- all six task directories exist at the intended source revision;
- Oracle evidence is present and valid for every task to be resumed;
- current task bundle digests match the historical lock files, or the resume is explicitly versioned as a new benchmark run.

Do not use broad process listings that print command arguments while investigating credentials. Prefer container names/PIDs only.

### Phase B — metadata-only Pi credential audit

Use a parser that reads [`/root/.pi/agent/models.json`](file:///root/.pi/agent/models.json) and prints only:

```text
provider | model-id | api | base-url | credential-source-class
```

Match `gpt-5.6-sol` and `claude-fable-5` by model ID. Do not print `apiKey`, auth-file contents, command output, or environment values. If the provider uses a `!command` credential source, stop and require an explicitly reviewed secure resolver; do not execute an arbitrary command as part of an audit.

The actual run wrapper should capture the resolver’s stdout directly into a shell variable inside a subshell:

```bash
(
  set -euo pipefail
  umask 077

  # secure_pi_key_resolver must emit only the key to captured stdout;
  # it must not log, write, or echo the key.
  export LLM_API_KEY="$(secure_pi_key_resolver --model "$MODEL")"
  export LLM_BASE_URL="https://z.open-api.ai/v1"

  # invoke the one-task queue here
)
```

This is safe only after removing the secret `--ae` argument from `run_harbor_model.sh`.

### Phase C — fresh roots and task lists

Create roots only after confirming they do not exist:

```bash
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
GPT_ROOT=".nl2repo/runs/batch-gpt-resume-${STAMP}"
FABLE_ROOT=".nl2repo/runs/batch-fable-resume-${STAMP}"

test ! -e "$GPT_ROOT"
test ! -e "$FABLE_ROOT"
```

Default fresh-cell lists:

```text
GPT-5.6:
  markupsafe, tablib, unidecode, unittest-parametrize, voluptuous, xlrd

Fable5:
  voluptuous, xlrd
```

The GPT `markupsafe` rerun is recommended because the historical result is `valid=false`, not a valid model score. If the benchmark policy explicitly treats the generic agent failure as a terminal model failure, it may instead be excluded and reported as invalid; that is a reporting decision, not a reason to reuse its old directory.

Run one task per queue invocation so a verifier/harness failure stops the model lane instead of allowing the serial script to continue silently:

```bash
# Illustrative structure; do not run until the credential and launcher gates pass.
for task in markupsafe tablib unidecode unittest-parametrize voluptuous xlrd; do
  TASKS="$task" \
  MODEL="openai/gpt-5.6-sol" \
  RUN_ROOT="$GPT_ROOT" \
  RUN_PREFIX="gpt56" \
  LOCK_ROOT=".nl2repo/locks/gpt56-resume-${STAMP}" \
  AGENT_TIMEOUT_SECONDS=18000 \
  REASONING_EFFORT=max \
  MAX_RETRIES=3 \
  LLM_NUM_RETRIES=10 \
  LLM_TIMEOUT=600 \
  LLM_RETRY_MIN_WAIT=8 \
  LLM_RETRY_MAX_WAIT=120 \
  scripts/run_model_queue.sh

  # Inspect result.json and verifier/grading.json here.
  # Abort on invalid/incomplete output.
done
```

Use the analogous Fable list with `MODEL="openai/claude-fable-5"`, `RUN_ROOT="$FABLE_ROOT"`, and `RUN_PREFIX="fable"`.

Preserve the historical execution settings: Harbor 0.21.0, native five-hour agent budget (`AGENT_TIMEOUT_SECONDS=18000` for a 3600-second task), `reasoning_effort=max`, and infrastructure-only retry classes. Do not alter task instructions, hidden tests, denominator, or verifier configuration during this resume.

### Phase D — per-task acceptance gate

After each task, require exactly one fresh Harbor result with:

```text
result.json:
  finished_at != null
  n_running_trials == 0
  n_pending_trials == 0

verifier/grading.json:
  valid == true
  expected == frozen task count
  collected - skipped == expected
  reward == passed / expected
```

Do not treat any of these as a score:

- missing `grading.json`;
- `finished_at=null`;
- `valid=false`;
- `junit-missing`;
- collection mismatch;
- Harbor process `rc=0` without a valid grading file.

### Phase E — archive only after scoring validation

Use a temporary, noncanonical staging copy so original run roots remain untouched:

```bash
# Copy/snapshot only after the run is complete.
# Never mutate the original batch roots.
STAGE="/tmp/nl2repo-resume-archive-${STAMP}"
```

Then:

1. Generate local SHA256/key manifests.
2. Rename or separately handle root-level queue logs so the uploader does not classify them as tasks.
3. Run:

   ```bash
   python scripts/upload_runs_to_oss.py \
     --runs-dir "$STAGE" \
     --skip-tasks \
     --dry-run
   ```

4. Perform remote HEAD/hash collision checks.
5. Upload without `--overwrite`, using a bounded worker count such as 4–8.
6. Re-run the manifest and verify that every remote object has the expected hash.
7. Preserve old wrongly classified OSS keys if they exist; create an audit/migration record rather than deleting or overwriting them.

## Stop conditions

| Trigger | Action |
|---|---|
| Any fresh trial produces `valid=false`, collection mismatch, missing JUnit, or verifier abnormal exit | Stop that model lane; inspect Oracle/environment/verifier before spending more model budget. |
| Generic `NonZeroAgentExitCodeError` or no trajectory recurs on the first GPT smoke task | Stop GPT lane; classify harness/provider failure until reviewed. |
| Infrastructure retry classes exhaust their bounded retry count | Stop and record infrastructure failure; do not silently convert to a model score. |
| `finished_at=null` after the launcher exits | Mark the trial incomplete and use a new root; never append to the partial Harbor job. |
| Secret scan finds the resolved credential in any run/log/staging file | Stop, quarantine artifacts, rotate credential, and do not upload. |
| Any planned OSS key already exists with a different content hash | Stop upload; do not use `--overwrite`. |
| New root already exists, source revision is dirty, or task digest differs | Abort before launch and create a new versioned plan. |
| Per-task five-hour agent budget plus cleanup deadline is exceeded | Terminate that task, preserve its partial artifacts, and classify it as incomplete. |
| Disk pressure, Docker daemon failure, or stale Harbor containers appear | Stop new tasks; clean up only after confirming no live queue remains. |

## Sources

### Kept

- [`batch-gpt-new6-20260821T/queue.log`](file:///root/NL2RepoBench/.nl2repo/runs/batch-gpt-new6-20260821T/queue.log) — task order, interruption boundary, and queue return codes.
- [`batch-fable-new6-20260821T/queue.log`](file:///root/NL2RepoBench/.nl2repo/runs/batch-fable-new6-20260821T/queue.log) — Fable terminal/incomplete boundary.
- Per-trial `result.json`, `lock.json`, `trial.log`, and `verifier/grading.json` under `/root/NL2RepoBench/.nl2repo/runs/` — authoritative terminal and validity evidence.
- [`scripts/run_model_queue.sh`](file:///root/NL2RepoBench/scripts/run_model_queue.sh) — task locking, `RUN_ID`, prefix, and serial behavior.
- [`scripts/run_harbor_model.sh`](file:///root/NL2RepoBench/scripts/run_harbor_model.sh) — Harbor arguments and credential handoff.
- [`src/nl2repobench/harbor_openhands.py`](file:///root/NL2RepoBench/src/nl2repobench/harbor_openhands.py) and installed Harbor [`BaseAgent`](file:///root/NL2RepoBench/harbor-runner/.venv/lib64/python3.14/site-packages/harbor/agents/base.py) — environment resolution and child-container propagation.
- [`scripts/upload_runs_to_oss.py`](file:///root/NL2RepoBench/scripts/upload_runs_to_oss.py) — model/task classification and existence-only deduplication.
- [`tests/test_upload_runs.py`](file:///root/NL2RepoBench/tests/test_upload_runs.py) — intended model-prefix/task naming convention.
- [`docs/run-artifacts-oss.md`](file:///root/NL2RepoBench/docs/run-artifacts-oss.md) — OSS layout, redaction, and scoring rules.
- [Pi custom models documentation](https://pi.dev/docs/latest/models) — provider field names and credential resolution modes.

### Dropped

- Generic benchmark leaderboards, blogs, and public model-release commentary — not evidence for these local trial states.
- Legacy OpenHands result conventions — the inspected runs use Harbor’s `result.json` and separate verifier contract.

## Gaps

1. No live OSS listing or remote object hash check was performed; existing `new6-*` archive pollution is unknown.
2. The actual credential source for the relay was intentionally not printed. `auth.json` is empty, but a redacted metadata-only provider/model lookup is still required before launch.
3. The full directory listing of both run roots was not performed through the available read-only interface. “Not started” classifications are based on queue order, absent task logs, and known result artifacts; run a path-only `find` preflight before launch.
4. The interrupted run’s exact Git commit is not embedded in queue metadata. Task-bundle digests in Harbor locks should be compared against the checkout before mixing results.
5. The security-only launcher change has not been implemented or regression-tested in this read-only audit.
6. No benchmark, model call, Docker trial, or OSS upload was executed.

## Supervisor coordination

A progress update was sent with the canonical artifact location, trial matrix, credential-handoff blocker, and OSS classifier findings. No routine completion handoff or benchmark execution was performed.
