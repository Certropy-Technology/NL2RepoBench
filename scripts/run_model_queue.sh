#!/usr/bin/env bash
# Run one serial model queue with process-safe task de-duplication.
set -uo pipefail

: "${TASKS:?comma-separated task list}"
: "${MODEL:?model id}"
: "${LLM_BASE_URL:?LLM base URL}"
: "${LLM_API_KEY:?LLM API key}"

RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/model-queue}"
RUN_PREFIX="${RUN_PREFIX:-model}"
mkdir -p "$RUN_ROOT"
LOGFILE="$RUN_ROOT/queue.log"
LOCK_ROOT="${LOCK_ROOT:-.nl2repo/locks/model-queue}"
mkdir -p "$LOCK_ROOT"

log() {
    printf '%s\n' "$*" | tee -a "$LOGFILE"
}

IFS=',' read -r -a task_list <<< "$TASKS"
log "queue_start=$(date -Is) model=$MODEL tasks=$TASKS mode=serial"

for task in "${task_list[@]}"; do
    lock_name=$(printf '%s-%s' "$MODEL" "$task" | tr '/:' '__')
    exec {task_lock}>"$LOCK_ROOT/$lock_name.lock"
    if ! flock -n "$task_lock"; then
        log "skip_locked[$task] $(date -Is)"
        exec {task_lock}>&-
        continue
    fi

    log "start[$task] $(date -Is)"
    TASK_ID="$task" \
        MODEL="$MODEL" \
        AGENT_TIMEOUT_SECONDS="${AGENT_TIMEOUT_SECONDS:-18000}" \
        REASONING_EFFORT="${REASONING_EFFORT:-max}" \
        MAX_RETRIES="${MAX_RETRIES:-3}" \
        RETRY_INFRA=1 \
        LLM_NUM_RETRIES="${LLM_NUM_RETRIES:-10}" \
        LLM_TIMEOUT="${LLM_TIMEOUT:-600}" \
        LLM_RETRY_MIN_WAIT="${LLM_RETRY_MIN_WAIT:-8}" \
        LLM_RETRY_MAX_WAIT="${LLM_RETRY_MAX_WAIT:-120}" \
        RUN_ID="${RUN_PREFIX}-${task}" \
        RUN_ROOT="$RUN_ROOT" \
        scripts/run_harbor_model.sh \
        >"$RUN_ROOT/${task}.log" 2>&1
    rc=$?
    # The task wrapper also cleans up, but keep a queue-level finalizer for
    # provider crashes, shell interruptions, and partial runner failures.
    python3 scripts/cleanup_harbor_trials.py \
        --jobs-dir "$RUN_ROOT/${RUN_PREFIX}-${task}" \
        >>"$RUN_ROOT/cleanup.log" 2>&1 || true
    log "done[$task] rc=$rc $(date -Is)"
    flock -u "$task_lock"
    exec {task_lock}>&-
done

log "queue_complete=$(date -Is)"
