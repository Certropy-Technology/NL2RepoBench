#!/usr/bin/env bash
# Run one catalog-backed Harbor task with OpenHands SDK.
set -euo pipefail

TASK_ID="${TASK_ID:?set TASK_ID}"
MODEL="${MODEL:?set MODEL, e.g. openai/gpt-5.6-sol}"
LLM_BASE_URL="${LLM_BASE_URL:?set LLM_BASE_URL}"
LLM_API_KEY="${LLM_API_KEY:?set LLM_API_KEY}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-3600}"
REASONING_EFFORT="${REASONING_EFFORT:-max}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-${TASK_ID}}"
RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/model}"

task_path="catalog/tasks/${TASK_ID}/harbor"
job_dir="${RUN_ROOT}/${RUN_ID}"

[[ -d "$task_path" ]] || { echo "missing Harbor task: $task_path" >&2; exit 1; }
mkdir -p "$job_dir"

echo "task=$TASK_ID"
echo "model=$MODEL"
echo "reasoning_effort=$REASONING_EFFORT"
echo "timeout_seconds=$TIMEOUT_SECONDS"
echo "jobs_dir=$job_dir"

cd harbor-runner
exec env PYTHONPATH=../src:${PYTHONPATH:-} timeout "$TIMEOUT_SECONDS" \
  uv run --frozen harbor run \
  -p "../$task_path" \
  -a nl2repobench.harbor_openhands:OpenHandsSDKFileInstruction \
  -m "$MODEL" \
  --ak "reasoning_effort=$REASONING_EFFORT" \
  --ae "LLM_BASE_URL=$LLM_BASE_URL" \
  --ae "LLM_API_KEY=$LLM_API_KEY" \
  --jobs-dir "../$job_dir"
