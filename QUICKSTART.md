# NL2RepoBench Quickstart

Run the Harbor-based benchmark from a fresh clone.

For the full operator guide see
[`docs/benchmark-operations-guide.zh-CN.md`](docs/benchmark-operations-guide.zh-CN.md).
For high-throughput Python/Node authoring see the current
[`docs/authoring-pipeline-ast.zh-CN.md`](docs/authoring-pipeline-ast.zh-CN.md).
For trajectory retention see
[`docs/trajectory-artifacts.zh-CN.md`](docs/trajectory-artifacts.zh-CN.md).

NL2RepoBench measures whether an LLM agent can build a complete, installable
Python repository from a natural-language specification and an **empty**
`/workspace`. Scoring is a fixed-test pass rate produced by a separate Harbor
verifier that the agent never sees.

## 1. Prerequisites

| Requirement | Why | Check |
| --- | --- | --- |
| Docker (daemon running) | Harbor builds agent + verifier containers | `docker info` |
| [uv](https://docs.astral.sh/uv/) | Python runner and lockfile execution | `uv --version` |
| Git | Oracle clones frozen upstream revisions | `git --version` |
| ~40 GB free disk | Legacy verifier images are large | `df -h .` |
| Network access to `ghcr.io` | Pulls frozen verifier images | `docker pull hello-world` |

An LLM API key is only needed for model runs (section 5). The Oracle gate in
section 4 needs no API key.

## 2. Clone And Install

```bash
git clone https://github.com/Certropy-Technology/NL2RepoBench
cd NL2RepoBench

# Authoring/validation CLI
uv sync

# Harbor runner (pinned via harbor-runner/uv.lock)
uv sync --project harbor-runner
```

Verify both toolchains:

```bash
uv run nl2repo --help
uv run --frozen --project harbor-runner harbor --version
```

## 3. What Is In The Repository

```text
catalog/
├── datasets/<dataset-id>/
│   └── dataset.toml     # authoritative task set for that version
├── sources/<task-id>/
│   ├── task.toml        # human-maintained source lock, contract and artifact refs
│   └── instruction.md   # the ONLY input the agent sees
└── tasks/<task-id>/     # compiler-generated Harbor projection; never hand-edit
    ├── task.toml
    ├── environment/Dockerfile
    ├── solution/solve.sh
    └── tests/
```

List the active tasks:

```bash
uv run python -c "
import tomllib
d = tomllib.load(open('catalog/datasets/nl2repobench-harbor-pilot/dataset.toml','rb'))
print(len(d['tasks']), 'active tasks')
print('\n'.join(sorted(d['tasks'])))
"
```

Validate the catalog before trusting anything:

```bash
uv run nl2repo dataset compile \
  catalog/datasets/nl2repobench-harbor-pilot/dataset.toml \
  --output build/catalog/nl2repobench-harbor-pilot
```

The current legacy conversion state is separate from older pilot dataset manifests;
query it with `scripts/convert_testfiles_loop.py status` before reporting counts.

## 4. Run The Oracle Gate (no API key)

The Oracle installs the frozen upstream source and must produce one valid result
whose collection matches the frozen denominator, with reward >= `0.80`. Run this first — it proves your Docker
environment is healthy before you spend model budget.

```bash
cd harbor-runner
PYTHONPATH=../src uv run --frozen python ../scripts/harbor_safe_entry.py run \
  -p ../catalog/sources/ftfy/harbor \
  -a oracle \
  --jobs-dir ../.nl2repo/runs/oracle/ftfy
python ../scripts/cleanup_harbor_trials.py \
  --jobs-dir ../.nl2repo/runs/oracle/ftfy
cd ..
```

Read the result:

```bash
find .nl2repo/runs/oracle/ftfy -name grading.json | tail -1 | xargs cat
```

Expected:

```json
{
  "reward": 1.0,
  "valid": true,
  "passed": 336,
  "expected": 336,
  "reason": null
}
```

`ftfy` takes about one minute after the image is cached. If `valid` is `false`,
fix the environment before continuing; a broken Oracle invalidates every model
score for that task.

## 5. Run A Model Securely

For the current Package campaign, only tasks with one valid Oracle run at reward >= `0.80` should be scored. This is not a cross-run stability proof. The runner script uses
Harbor with the file-backed OpenHands SDK adapter (required: large instructions
exceed the host `ARG_MAX` if passed on the command line).

Use the Pi-aware wrapper. It reads a mode-600 provider file and keeps the
credential out of Harbor/Docker argv. A key pasted into chat is not automatically
imported into the local shell.

```bash
python3 scripts/run_model_from_pi.py \
  --provider z-open-api-gpt-openai-responses \
  --model-id gpt-5.6-sol \
  --harbor-model openai/gpt-5.6-sol \
  --task ftfy \
  --run-root "$PWD/.nl2repo/runs/smoke-gpt-$(date -u +%Y%m%dT%H%M%SZ)" \
  --run-prefix gpt56 \
  --lock-root "$PWD/.nl2repo/locks/gpt-smoke-$(date -u +%Y%m%dT%H%M%SZ)"
```

Never put the credential value in `--ae`, an argument, a file, Git, or an
uploaded report. Every retry uses a new run root.

Key environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `TASK_ID` | required | task under `catalog/sources/` |
| `MODEL` | required | LiteLLM model id, e.g. `openai/gpt-5.6-sol` |
| `LLM_BASE_URL` | internal | resolved by the Pi-aware wrapper |
| `LLM_API_KEY` | internal | held in a short-lived process environment; never put it in argv |
| `AGENT_TIMEOUT_SECONDS` | `18000` | Harbor-native agent phase budget; environment setup and verifier use their own budgets |
| `REASONING_EFFORT` | `max` | forwarded to the SDK |
| `MAX_RETRIES` | `2` | Harbor retries, **infrastructure errors only** |
| `RETRY_INFRA` | `1` | classify gateway 5xx/rate limit as retryable |

Model failures are terminal by design. Only classified infrastructure errors
(rate limit, gateway 5xx, overload, mid-stream disconnect) are retried, so a
weak model is never silently rescued by a retry.

## 6. Run Many Tasks

One serial worker per model, with a `flock` guard so the same model never runs
the same task twice. For credential-sensitive runs, prefer one task per
`run_model_from_pi.py` invocation. The legacy parallel wrappers are not approved
for secure campaigns.

```bash
TASKS='ftfy,parse,jsonlines,six' \
MODEL=openai/gpt-5.6-sol \
LLM_BASE_URL=https://your-endpoint/v1 \
LLM_API_KEY="$YOUR_KEY" \
RUN_ROOT=.nl2repo/runs/my-batch \
RUN_PREFIX=gpt56 \
scripts/run_model_queue.sh
```

Progress is appended to `$RUN_ROOT/queue.log`. To evaluate two models at once,
start two queues with **different** `RUN_ROOT` values; each stays serial, so
peak Docker load is two agent containers.

## 7. Read The Scores

```bash
uv run python - <<'PY'
from pathlib import Path
import json

root = Path('.nl2repo/runs/my-batch')
latest = {}
for p in root.rglob('grading.json'):
    task = next((x for x in p.parts if x.startswith(('gpt56-', 'fable-'))), None)
    if task and (task not in latest or p.stat().st_mtime > latest[task].stat().st_mtime):
        latest[task] = p

rewards = []
for task, p in sorted(latest.items()):
    d = json.loads(p.read_text())
    flag = 'OK ' if d['valid'] else 'INVALID'
    print(f"{flag} {task:28} {d['reward']:.4f}  {d['passed']}/{d['expected']}  {d['reason'] or ''}")
    if d['valid']:
        rewards.append(d['reward'])

if rewards:
    print(f"\nmacro-average over {len(rewards)} valid tasks: {sum(rewards)/len(rewards):.4f}")
PY
```

Scoring contract:

```text
task_score    = clamp(passed / frozen_total, 0, 1)
dataset_score = mean(task_score for every VALID task)
```

Always use the **macro average** across tasks. Never sum all passed tests and
divide by all tests — that would weight large suites more heavily.

`valid: false` means the run is not a model score. Common reasons:

| `reason` | Meaning | Action |
| --- | --- | --- |
| `collection-mismatch` | collected − skipped ≠ frozen denominator | task/env problem, do not report as model score |
| `junit-missing` | pytest never produced results | check install/verifier logs |
| `installation-failed` | candidate package would not install | model failure evidence, but verify env first |
| `pytest-abnormal-exit` | verifier crashed | infrastructure |

## 8. Housekeeping

Run outputs go to `.nl2repo/runs/` and are gitignored — never write them inside
`catalog/sources/`.

If a run is interrupted, remove orphaned containers (this only touches Harbor
containers with no live host process):

```bash
docker ps --filter "name=harbor__" --format '{{.ID}} {{.Names}}'
docker rm -f $(docker ps -q --filter "name=harbor__")   # only when no run is active
```

## 9. Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Argument list too long` | instruction passed via argv | use `scripts/run_harbor_model.sh` (file-backed adapter) |
| Oracle `valid: false` | env/denominator drift | check `pytest-stdout.txt` in the run dir; do not lower the denominator to force green |
| `VerifierTimeoutError` | suite slower than `verifier.timeout_sec` | raise it in that task's `harbor/task.toml` |
| 404 from provider | `/v1` duplicated in base URL | LiteLLM appends the path; check `LLM_BASE_URL` |
| `no channel found` | relay outage | infrastructure, retry later; not a model score |

## 10. Current Dataset State

- 104 legacy tasks are tracked in `.nl2repo/conversion-loop/state.json`; the current
  reconciliation is 74 complete and 30 pending. Blocked/excluded lifecycle records
  are audited separately by `scripts/reconcile_task_status.py`.
- Node/npm tasks use a separate development-only v2 pilot.
- New Python/npm candidates remain audit/spec records until private artifacts,
  the current one-run Oracle gate and controls are approved.
- Do not use stale “37 active task” text in older pilot documents as current state.

Blocked candidates stay in the catalog for repair and audit but are excluded
from scoring. Environment, verifier and infrastructure failures must never be
reported as model results.
