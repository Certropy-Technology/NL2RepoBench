#!/usr/bin/env bash
# Run one catalog-backed Harbor task with OpenHands SDK.
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_ROOT/.." && pwd)"

TASK_ID="${TASK_ID:?set TASK_ID}"
MODEL="${MODEL:?set MODEL, e.g. openai/gpt-5.6-sol}"
LLM_BASE_URL="${LLM_BASE_URL:?set LLM_BASE_URL}"
LLM_API_KEY="${LLM_API_KEY:?set LLM_API_KEY}"
AGENT_TIMEOUT_SECONDS="${AGENT_TIMEOUT_SECONDS:-18000}"
AGENT_SETUP_TIMEOUT_MULTIPLIER="${AGENT_SETUP_TIMEOUT_MULTIPLIER:-3}"
REASONING_EFFORT="${REASONING_EFFORT:-max}"
MAX_RETRIES="${MAX_RETRIES:-2}"
RETRY_INFRA="${RETRY_INFRA:-1}"
LLM_NUM_RETRIES="${LLM_NUM_RETRIES:-10}"
LLM_TIMEOUT="${LLM_TIMEOUT:-600}"
LLM_RETRY_MIN_WAIT="${LLM_RETRY_MIN_WAIT:-8}"
LLM_RETRY_MAX_WAIT="${LLM_RETRY_MAX_WAIT:-120}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)-${TASK_ID}}"
RUN_ROOT="${RUN_ROOT:-.nl2repo/runs/model}"
HARBOR_AGENT="${HARBOR_AGENT:-nl2repobench.harbor_openhands:OpenHandsSDKFileInstruction}"

case "$RUN_ID" in
  ""|/*|*..*|*$'\n'*|*$'\r'*)
    echo "invalid RUN_ID: $RUN_ID" >&2
    exit 2
    ;;
esac

case "$HARBOR_AGENT" in
  nl2repobench.harbor_openhands:OpenHandsSDKFileInstruction)
    ;;
  *)
    echo "unsupported HARBOR_AGENT: $HARBOR_AGENT" >&2
    exit 2
    ;;
esac

provider_host="$({
  python3 - "$LLM_BASE_URL" <<'PY'
from ipaddress import ip_address
from urllib.parse import urlsplit
import re
import sys

value = sys.argv[1]
parsed = urlsplit(value)
if parsed.scheme.lower() != "https" or not parsed.hostname:
    raise SystemExit("LLM_BASE_URL must be an HTTPS URL with a hostname")
if parsed.username or parsed.password:
    raise SystemExit("LLM_BASE_URL must not contain URL credentials")
try:
    parsed.port
except ValueError as exc:
    raise SystemExit("LLM_BASE_URL contains an invalid port") from exc

host = parsed.hostname.rstrip(".").lower()
try:
    ip_address(host)
except ValueError:
    if not re.fullmatch(
        r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
        r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+",
        host,
    ):
        raise SystemExit(f"invalid LLM Provider hostname: {host}")
for suffix in (
    "github.com",
    "gitlab.com",
    "bitbucket.org",
    "sourceforge.net",
):
    if host == suffix or host.endswith("." + suffix):
        raise SystemExit(f"source-host LLM Provider hostname is forbidden: {host}")
print(host)
PY
})"
[[ -n "$provider_host" ]] || { echo "LLM Provider hostname is empty" >&2; exit 1; }

if [[ -n "${HARBOR_TASK_PATH:-}" ]]; then
  task_path="$HARBOR_TASK_PATH"
elif [[ -n "${HARBOR_TASK_ROOT:-}" ]]; then
  task_path="$HARBOR_TASK_ROOT/$TASK_ID"
else
  task_path="catalog/tasks/${TASK_ID}"
fi
if [[ "$RUN_ROOT" == /* ]]; then
  run_root_abs="$RUN_ROOT"
else
  run_root_abs="$PWD/$RUN_ROOT"
fi
mkdir -p "$run_root_abs"
run_root_abs="$(cd "$run_root_abs" && pwd)"
job_dir="$run_root_abs/$RUN_ID"
task_config="${task_path}/task.toml"

harbor_jobs_dir="$job_dir"

[[ "$task_path" != *$'\n'* ]] || { echo "invalid Harbor task path" >&2; exit 1; }
[[ -d "$task_path" ]] || { echo "missing Harbor task: $task_path" >&2; exit 1; }
[[ -f "$task_config" ]] || { echo "missing Harbor config: $task_config" >&2; exit 1; }
mkdir -p "$job_dir"
archive_task_id="${TASK_ID//\//__}"
archive_script="$SCRIPT_ROOT/archive_harbor_job.py"

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
echo "agent_setup_timeout_multiplier=$AGENT_SETUP_TIMEOUT_MULTIPLIER"
echo "max_retries=$MAX_RETRIES retry_infra=$RETRY_INFRA"
echo "llm_num_retries=$LLM_NUM_RETRIES llm_timeout=$LLM_TIMEOUT"
echo "llm_retry_wait=$LLM_RETRY_MIN_WAIT-$LLM_RETRY_MAX_WAIT"
echo "jobs_dir=$harbor_jobs_dir"

agent_env_args=(
  --ae "LLM_NUM_RETRIES=$LLM_NUM_RETRIES"
  --ae "LLM_TIMEOUT=$LLM_TIMEOUT"
  --ae "LLM_RETRY_MIN_WAIT=$LLM_RETRY_MIN_WAIT"
  --ae "LLM_RETRY_MAX_WAIT=$LLM_RETRY_MAX_WAIT"
)
if [[ -n "${LLM_ANTHROPIC_THINKING_MODE:-}" ]]; then
  agent_env_args+=(--ae "LLM_ANTHROPIC_THINKING_MODE=$LLM_ANTHROPIC_THINKING_MODE")
fi
if [[ -n "${LLM_OPENHANDS_SECURITY_PROFILE:-}" ]]; then
  agent_env_args+=(--ae "LLM_OPENHANDS_SECURITY_PROFILE=$LLM_OPENHANDS_SECURITY_PROFILE")
fi
if [[ -n "${LLM_STREAM:-}" ]]; then
  [[ "$LLM_STREAM" == "0" || "$LLM_STREAM" == "1" ]] || {
    echo "LLM_STREAM must be 0 or 1" >&2
    exit 2
  }
  agent_env_args+=(--ae "LLM_STREAM=$LLM_STREAM")
fi

cleanup_harbor_trials() {
  # Harbor environment services intentionally use `sleep infinity`.  Cleanup
  # only the exact trials created below; never run a global Docker prune.
  set +e
  PYTHONPATH="$REPO_ROOT/src" python3 "$REPO_ROOT/scripts/cleanup_harbor_trials.py" \
    --jobs-dir "$harbor_jobs_dir" \
    >>"$job_dir/cleanup.log" 2>&1
  cleanup_rc=$?
  if [[ "$cleanup_rc" -ne 0 ]]; then
    printf 'harbor_cleanup_rc=%s\n' "$cleanup_rc" >>"$job_dir/cleanup.log"
  fi
  return "$cleanup_rc"
}

archive_harbor_job() {
  # Upload and verify the complete job, including artifacts/workspace, before
  # removing the local job directory. Failure deliberately keeps local data.
  set +e
  PYTHONPATH="$REPO_ROOT/src" python3 "$archive_script" \
    --job-dir "$harbor_jobs_dir" \
    --model "$MODEL" \
    --task-id "$TASK_ID" \
    --run-id "$RUN_ID" \
    --workers "${OSS_HARBOR_ARCHIVE_WORKERS:-8}" \
    --receipt-path "$run_root_abs/oss-archive-receipts/${archive_task_id}.json" \
    >"$run_root_abs/${RUN_ID}.oss-archive.log" 2>&1
  archive_rc=$?
  if [[ "$archive_rc" -ne 0 ]]; then
    printf 'harbor_oss_archive_rc=%s\n' "$archive_rc" \
      >>"$run_root_abs/${RUN_ID}.oss-archive.log"
  fi
  return "$archive_rc"
}

remove_archived_job() {
  [[ "$1" -eq 0 ]] || return 0
  [[ "$harbor_jobs_dir" == "$run_root_abs/$RUN_ID" ]] || {
    printf 'refusing to remove unexpected Harbor job path: %s\n' "$harbor_jobs_dir" \
      >>"$run_root_abs/${RUN_ID}.oss-archive.log"
    return 1
  }
  [[ -n "$harbor_jobs_dir" && "$harbor_jobs_dir" != "/" ]] || return 1
  rm -rf -- "$harbor_jobs_dir"
}

on_exit() {
  set +e
  final_rc=$?
  cleanup_harbor_trials
  cleanup_rc=$?
  archive_harbor_job
  archive_rc=$?
  if [[ "$archive_rc" -eq 0 && "$cleanup_rc" -eq 0 ]]; then
    remove_archived_job "$archive_rc"
    remove_rc=$?
  else
    remove_rc=0
  fi
  if [[ "$archive_rc" -ne 0 || "$cleanup_rc" -ne 0 || "$remove_rc" -ne 0 ]]; then
    final_rc=1
  fi
  trap - EXIT
  exit "$final_rc"
}
trap on_exit EXIT

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
  -a "$HARBOR_AGENT" \
  -m "$MODEL" \
  --ak "reasoning_effort=$REASONING_EFFORT" \
  --ae "LLM_BASE_URL=$LLM_BASE_URL" \
  --allow-agent-host "$provider_host" \
  "${agent_env_args[@]}" \
  --agent-timeout-multiplier "$agent_timeout_multiplier" \
  --agent-setup-timeout-multiplier "$AGENT_SETUP_TIMEOUT_MULTIPLIER" \
  "${retry_args[@]}" \
  --jobs-dir "$harbor_jobs_dir"
harbor_rc=$?
exit "$harbor_rc"
