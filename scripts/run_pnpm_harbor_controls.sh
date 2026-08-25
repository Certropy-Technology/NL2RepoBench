#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output="${1:-$root/.nl2repo/node-pnpm-synthetic-controls}"
rm -rf -- "$output"
mkdir -p -- "$output/tasks" "$output/jobs"

uv=(env PYTHONPATH="$root/src" uv run --frozen)
toolchain="$root/toolchain.node.dev.lock.toml"
source="$root/catalog/sources/node-pnpm-synthetic"
"${uv[@]}" python - <<PY
from pathlib import Path
from nl2repobench.harbor.pnpm_compiler import PnpmHarborCompiler
PnpmHarborCompiler(Path(${toolchain@Q})).compile_task(
    Path(${source@Q}), Path(${output@Q}) / "tasks", allow_incomplete=True
)
PY

base="$output/tasks/node-pnpm-synthetic"
harbor=("${uv[@]}" --project "$root/harbor-runner" harbor run)
"${harbor[@]}" -p "$base" -a nop --jobs-dir "$output/jobs/empty"
"${harbor[@]}" -p "$base" -a oracle --jobs-dir "$output/jobs/oracle"

python - "$output" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
for name in ("empty", "oracle"):
    job = sorted((root / "jobs" / name).glob("*/result.json"))[-1]
    payload = json.loads(job.read_text())
    evaluation = next(iter(payload["stats"]["evals"].values()))
    metric = evaluation["metrics"][0]
    print(json.dumps({"control": name, "exceptions": evaluation["n_errors"], "reward": metric["reward"]}, sort_keys=True))
PY

python - "$output" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
summary = {"archive_contract": "p2-vertical-slice-v1"}
for name in ("empty", "oracle"):
    job = sorted((root / "jobs" / name).glob("*/result.json"))[-1]
    payload = json.loads(job.read_text())
    evaluation = next(iter(payload["stats"]["evals"].values()))
    summary[f"{name}_reward"] = evaluation["metrics"][0]["reward"]
(root / "pnpm-evidence.json").write_text(json.dumps(summary, sort_keys=True) + "\n")
if summary["empty_reward"] != 0.0 or summary["oracle_reward"] < 0.8:
    raise SystemExit("pnpm Oracle/empty controls did not pass")
PY
