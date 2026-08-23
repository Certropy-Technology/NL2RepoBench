#!/usr/bin/env bash
# Run one catalog-backed Harbor task with OpenHands SDK.
set -euo pipefail

TASK_ID="${TASK_ID:?set TASK_ID}"
MODEL="${MODEL:?set MODEL, e.g. openai/gpt-5.6-sol}"
LLM_BASE_URL="${LLM_BASE_URL:?set LLM_BASE_URL}"
LLM_API_KEY="${LLM_API_KEY:?set LLM_API_KEY}"
AGENT_TIMEOUT_SECONDS="${AGENT_TIMEOUT_SECONDS:-18000}"
REASONING_EFFORT="${REASONING_EFFORT:-max}"
MAX_RETRIES="${MAX_RETRIES:-2}"
RETRY_INFRA="${RETRY_INFRA:-1}"
LLM_NUM_RETRIES="${LLM_NUM_RETRIES:-10}"
LLM_TIMEOUT="${LLM_TIMEOUT:-600}"
LLM_RETRY_MIN_WAIT="${LLM_RETRY_MIN_WAIT:-8}"
LLM_RETRY_MAX_WAIT="${LLM_RETRY_MAX_WAIT:-120}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-${TASK_ID}}"
RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/model}"

if [[ -n "${HARBOR_TASK_PATH:-}" ]]; then
  task_path="$HARBOR_TASK_PATH"
elif [[ -n "${HARBOR_TASK_ROOT:-}" ]]; then
  task_path="$HARBOR_TASK_ROOT/$TASK_ID"
else
  task_path="catalog/tasks/${TASK_ID}/harbor"
fi
job_dir="${RUN_ROOT}/${RUN_ID}"
task_config="${task_path}/task.toml"

if [[ "$job_dir" != /* ]]; then
  job_dir="$PWD/$job_dir"
fi
harbor_jobs_dir="$job_dir"

[[ "$task_path" != *$'\n'* ]] || { echo "invalid Harbor task path" >&2; exit 1; }
[[ -d "$task_path" ]] || { echo "missing Harbor task: $task_path" >&2; exit 1; }
[[ -f "$task_config" ]] || { echo "missing Harbor config: $task_config" >&2; exit 1; }
mkdir -p "$job_dir"

agent_timeout_multiplier="$(
  python3 - "$task_config" "$AGENT_TIMEOUT_SECONDS" <<'PY'
import sys
import tomllib
from pathlib import Path

task_config = Path(sys.argv[1])
target_seconds = float(sys.argv[2])
with task_config.open("rb") as handle:
    native_seconds = float(tomllib.load(handle)["agent"]["timeout_sec"])
if target_seconds <= 0 or native_seconds <= 0:
    raise SystemExit("agent timeout values must be positive")
print(f"{target_seconds / native_seconds:.12g}")
PY
)"

echo "task=$TASK_ID"
echo "model=$MODEL"
echo "reasoning_effort=$REASONING_EFFORT"
echo "agent_timeout_seconds=$AGENT_TIMEOUT_SECONDS"
echo "agent_timeout_multiplier=$agent_timeout_multiplier"
echo "max_retries=$MAX_RETRIES retry_infra=$RETRY_INFRA"
echo "llm_num_retries=$LLM_NUM_RETRIES llm_timeout=$LLM_TIMEOUT"
echo "llm_retry_wait=$LLM_RETRY_MIN_WAIT-$LLM_RETRY_MAX_WAIT"
echo "jobs_dir=$harbor_jobs_dir"

cleanup_harbor_trials() {
  # Harbor environment services intentionally use `sleep infinity`.  Cleanup
  # only the exact trials created below; never run a global Docker prune.
  set +e
  PYTHONPATH=../src python3 ../scripts/cleanup_harbor_trials.py \
    --jobs-dir "$harbor_jobs_dir" \
    >>"$job_dir/cleanup.log" 2>&1
  cleanup_rc=$?
  if [[ "$cleanup_rc" -ne 0 ]]; then
    printf 'harbor_cleanup_rc=%s\n' "$cleanup_rc" >>"$job_dir/cleanup.log"
  fi
}
trap cleanup_harbor_trials EXIT

retry_args=()
if [[ "$RETRY_INFRA" == "1" ]]; then
  # Only retry classified infrastructure errors (rate limit, gateway 5xx,
  # overload, mid-stream disconnects). Model failures stay terminal.
  retry_args=(
    --max-retries "$MAX_RETRIES"
    --retry-include ApiRateLimitError
    --retry-include ApiInternalServerError
    --retry-include ApiOverloadedError
    --retry-include ApiConnectionClosedError
    --retry-include ApiResponseStalledError
  )
fi

if [[ "$task_path" == /* ]]; then
  harbor_task_path="$task_path"
else
  harbor_task_path="../$task_path"
fi
cd harbor-runner
set +e
env PYTHONPATH=../src:${PYTHONPATH:-} \
  uv run --frozen python ../scripts/harbor_safe_entry.py run \
  -p "$harbor_task_path" \
  -e nl2repobench.harbor_docker:StdinSecretDockerEnvironment \
  -a nl2repobench.harbor_openhands:OpenHandsSDKFileInstruction \
  -m "$MODEL" \
  --ak "reasoning_effort=$REASONING_EFFORT" \
  --ae "LLM_BASE_URL=$LLM_BASE_URL" \
  --ae "LLM_NUM_RETRIES=$LLM_NUM_RETRIES" \
  --ae "LLM_TIMEOUT=$LLM_TIMEOUT" \
  --ae "LLM_RETRY_MIN_WAIT=$LLM_RETRY_MIN_WAIT" \
  --ae "LLM_RETRY_MAX_WAIT=$LLM_RETRY_MAX_WAIT" \
  --agent-timeout-multiplier "$agent_timeout_multiplier" \
  "${retry_args[@]}" \
  --jobs-dir "$harbor_jobs_dir"
harbor_rc=$?
exit "$harbor_rc"
