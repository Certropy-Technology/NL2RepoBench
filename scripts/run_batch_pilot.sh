#!/usr/bin/env bash
# Sequential/low-parallel batch runner for Harbor pilot tasks.
set -uo pipefail

TASKS="${TASKS:?comma-separated task list}"
MODEL="${MODEL:?model id}"
RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/batch-$(date -u +%Y%m%dT%H%M%SZ)}"
MAX_PARALLEL="${MAX_PARALLEL:-2}"
mkdir -p "$RUN_ROOT"

echo "batch_start=$(date -Is) model=$MODEL max_parallel=$MAX_PARALLEL"
echo "tasks=$TASKS"

declare -A PIDS
running=0
IFS=',' read -ra TASK_ARR <<< "$TASKS"
for t in "${TASK_ARR[@]}"; do
  # throttle
  while (( running >= MAX_PARALLEL )); do
    for k in "${!PIDS[@]}"; do
      if ! kill -0 "${PIDS[$k]}" 2>/dev/null; then
        wait "${PIDS[$k]}"; rc=$?
        echo "done[$k] rc=$rc $(date -Is)"
        unset 'PIDS[$k]'
        (( running-- ))
      fi
    done
    sleep 5
  done

  echo "start[$t] $(date -Is)"
  env TASK_ID="$t" MODEL="$MODEL" \
    LLM_BASE_URL="$LLM_BASE_URL" LLM_API_KEY="$LLM_API_KEY" \
    AGENT_TIMEOUT_SECONDS="${AGENT_TIMEOUT_SECONDS:-18000}" REASONING_EFFORT=max \
    MAX_RETRIES=2 RETRY_INFRA=1 \
    LLM_NUM_RETRIES=10 LLM_TIMEOUT=600 \
    LLM_RETRY_MIN_WAIT=8 LLM_RETRY_MAX_WAIT=120 \
    RUN_ID="gpt56-$t" RUN_ROOT="$RUN_ROOT" \
    scripts/run_harbor_model.sh > "$RUN_ROOT/$t.log" 2>&1 < /dev/null &
  PIDS[$t]=$!
  (( running++ ))
done

for k in "${!PIDS[@]}"; do
  wait "${PIDS[$k]}"; rc=$?
  echo "done[$k] rc=$rc $(date -Is)"
done
echo "batch_complete=$(date -Is)"
