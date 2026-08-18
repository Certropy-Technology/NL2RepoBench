#!/usr/bin/env bash
set -euo pipefail

output="${1:-.nl2repo/phase2-ministats}"
rm -rf -- "$output"
mkdir -p -- "$output/tasks" "$output/jobs"

harbor=(uv run --frozen --project harbor-runner harbor)

for attempt in 1 2 3; do
  uv run nl2repo harbor compile \
    catalog/tasks/ministats \
    --output "$output/tasks/oracle-$attempt" \
    --toolchain toolchain.lock.toml \
    --allow-incomplete
  "${harbor[@]}" run \
    -p "$output/tasks/oracle-$attempt/ministats" \
    -a oracle \
    --jobs-dir "$output/jobs/oracle-$attempt"
done

base="$output/tasks/oracle-1/ministats"
"${harbor[@]}" run -p "$base" -a nop --jobs-dir "$output/jobs/nop"

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
  "${harbor[@]}" run \
    -p "$output/tasks/controls/ministats-$kind" \
    -a oracle \
    --jobs-dir "$output/jobs/$kind"
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
