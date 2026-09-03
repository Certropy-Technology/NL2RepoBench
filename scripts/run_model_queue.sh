#!/usr/bin/env bash
# Run a bounded model queue with process-safe task de-duplication.
set -uo pipefail

: "${TASKS:?comma-separated task list}"
: "${MODEL:?model id}"
: "${LLM_BASE_URL:?LLM base URL}"
: "${LLM_API_KEY:?LLM API key}"

RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/model-queue}"
RUN_PREFIX="${RUN_PREFIX:-model}"
MAX_CONCURRENCY="${MAX_CONCURRENCY:-1}"
if [[ ! "$MAX_CONCURRENCY" =~ ^[1-9][0-9]*$ ]]; then
    echo "MAX_CONCURRENCY must be a positive integer" >&2
    exit 2
fi
mkdir -p "$RUN_ROOT"
LOGFILE="$RUN_ROOT/queue.log"
LOCK_ROOT="${LOCK_ROOT:-.nl2repo/locks/model-queue}"
mkdir -p "$LOCK_ROOT"

log() {
    printf '%s\n' "$*" | tee -a "$LOGFILE"
}

IFS=',' read -r -a task_list <<< "$TASKS"
log "queue_start=$(date -Is) model=$MODEL tasks=$TASKS concurrency=$MAX_CONCURRENCY"

run_task() {
    local task="$1"
    local lock_name task_lock rc
    lock_name=$(printf '%s-%s' "$MODEL" "$task" | tr '/:' '__')
    exec {task_lock}>"$LOCK_ROOT/$lock_name.lock"
    if ! flock -n "$task_lock"; then
        log "skip_locked[$task] $(date -Is)"
        exec {task_lock}>&-
        return 0
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
    PYTHONPATH="${PYTHONPATH:-}:$PWD/src" "$PWD/.venv/bin/python3" \
        scripts/cleanup_harbor_trials.py \
        --jobs-dir "$RUN_ROOT/${RUN_PREFIX}-${task}" \
        >>"$RUN_ROOT/cleanup.log" 2>&1 || true
    log "done[$task] rc=$rc $(date -Is)"
    flock -u "$task_lock"
    exec {task_lock}>&-
    return "$rc"
}

declare -A active_tasks=()
active=0
failed=0
stopping=0

stop_children() {
    stopping=1
    for pid in "${!active_tasks[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
}
trap stop_children INT TERM

reap_one() {
    local finished_pid="" task rc
    if wait -n -p finished_pid "${!active_tasks[@]}"; then
        rc=0
    else
        rc=$?
    fi
    finished_pid="${finished_pid:-}"
    if [[ -z "$finished_pid" ]]; then
        # wait -n can be interrupted while the TERM trap is stopping children.
        # Do not let set -u turn an intentional queue stop into a launcher bug.
        for finished_pid in "${!active_tasks[@]}"; do
            wait "$finished_pid" 2>/dev/null || true
            unset 'active_tasks[$finished_pid]'
        done
        active=0
        return
    fi
    task="${active_tasks[$finished_pid]}"
    unset 'active_tasks[$finished_pid]'
    active=$((active - 1))
    if (( rc != 0 )); then
        failed=$((failed + 1))
        log "failure[$task] rc=$rc $(date -Is)"
    fi
}

for task in "${task_list[@]}"; do
    (( stopping )) && break
    while (( active >= MAX_CONCURRENCY )); do
        reap_one
    done
    run_task "$task" &
    pid=$!
    active_tasks[$pid]="$task"
    active=$((active + 1))
done

while (( active > 0 )); do
    reap_one
done

if (( stopping )); then
    log "queue_interrupted=$(date -Is) failed=$failed"
    exit 130
fi
log "queue_complete=$(date -Is) failed=$failed"
if (( failed != 0 )); then
    exit 1
fi
