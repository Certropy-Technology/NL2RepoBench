#!/usr/bin/env bash
set -euo pipefail

output="${1:-.nl2repo/phase2-ministats}"
rm -rf -- "$output"
mkdir -p -- "$output/tasks" "$output/jobs"

harbor=(env PYTHONPATH=src uv run --frozen --project harbor-runner python scripts/harbor_safe_entry.py)

run_harbor() {
  local jobs_dir="$1"
  shift
  set +e
  "${harbor[@]}" run "$@" --jobs-dir "$jobs_dir"
  local harbor_rc=$?
  uv run python scripts/cleanup_harbor_trials.py --jobs-dir "$jobs_dir" || true
  set -e
  return "$harbor_rc"
}

for attempt in 1 2 3; do
  uv run nl2repo harbor compile \
    catalog/tasks/ministats \
    --output "$output/tasks/oracle-$attempt" \
    --toolchain toolchain.lock.toml \
    --allow-incomplete
  run_harbor "$output/jobs/oracle-$attempt" \
    -p "$output/tasks/oracle-$attempt/ministats" \
    -a oracle
done

base="$output/tasks/oracle-1/ministats"
run_harbor "$output/jobs/nop" -p "$base" -a nop

uv run nl2repo harbor prepare-control \
  "$base" stub --output "$output/tasks/controls" --toolchain toolchain.lock.toml
uv run nl2repo harbor prepare-control \
  "$base" forgery --output "$output/tasks/controls" --toolchain toolchain.lock.toml
uv run nl2repo harbor prepare-control \
  "$base" install-hang --output "$output/tasks/controls" --toolchain toolchain.lock.toml
uv run nl2repo harbor prepare-control \
  "$base" workspace-invalid --output "$output/tasks/controls" --toolchain toolchain.lock.toml
uv run nl2repo harbor prepare-control \
  "$base" call-hang --output "$output/tasks/controls" --toolchain toolchain.lock.toml

for kind in stub forgery install-hang workspace-invalid call-hang; do
  run_harbor "$output/jobs/$kind" \
    -p "$output/tasks/controls/ministats-$kind" \
    -a oracle
done

summary_args=(
  "$output/jobs"
  --bundle "$base"
  --toolchain toolchain.lock.toml
  --output "$output/control-summary.json"
)
if [[ -n "${PHASE2_CONTROL_REFERENCE:-}" ]]; then
  summary_args+=(--reference "$PHASE2_CONTROL_REFERENCE")
fi
uv run python scripts/summarize_phase2_controls.py "${summary_args[@]}"
