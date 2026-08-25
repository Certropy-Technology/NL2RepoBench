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
run_job() {
  local name="$1"
  local task="$2"
  local agent="$3"
  "${harbor[@]}" -p "$task" -a "$agent" --jobs-dir "$output/jobs/$name"
}

run_job empty "$base" nop
run_job oracle "$base" oracle
run_job offline "$base" oracle

for kind in stub forgery install-failure call-hang; do
  mkdir -p "$output/tasks/$kind"
  cp -a "$base/." "$output/tasks/$kind/"
  case "$kind" in
    stub|forgery)
      cat > "$output/tasks/$kind/solution/solve.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"node-pnpm-synthetic","version":"2.0.0","type":"module","exports":"./index.mjs","pnpm":{"settings":{"autoInstallPeers":false,"excludeLinksFromLockfile":false}}}
JSON
cat > pnpm-lock.yaml <<'YAML'
lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
YAML
cat > index.mjs <<'JS'
const fail = () => { throw new Error("candidate-call-failed"); };
export const normalize = fail;
export const stableStringify = fail;
export const summarize = fail;
JS
EOF
      if [[ "$kind" == "forgery" ]]; then
        cat >> "$output/tasks/$kind/solution/solve.sh" <<'EOF'
mkdir -p /logs/verifier 2>/dev/null || true
printf '%s\n' '{"reward":1,"test_pass_rate":1}' > /logs/verifier/reward.json 2>/dev/null || true
EOF
      fi
      ;;
    install-failure)
      printf '#!/usr/bin/env bash\nset -euo pipefail\nprintf broken > broken.txt\n' > "$output/tasks/$kind/solution/solve.sh"
      ;;
    call-hang)
      cat > "$output/tasks/$kind/solution/solve.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"node-pnpm-synthetic","version":"2.0.0","type":"module","exports":"./index.mjs","pnpm":{"settings":{"autoInstallPeers":false,"excludeLinksFromLockfile":false}}}
JSON
cat > pnpm-lock.yaml <<'YAML'
lockfileVersion: '9.0'
settings:
  autoInstallPeers: false
  excludeLinksFromLockfile: false
importers:
  .: {}
packages: {}
snapshots: {}
YAML
cat > index.mjs <<'JS'
const hang = () => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 60000);
export const normalize = hang;
export const stableStringify = hang;
export const summarize = hang;
JS
EOF
      ;;
  esac
  chmod 755 "$output/tasks/$kind/solution/solve.sh"
  run_job "$kind" "$output/tasks/$kind" oracle
done

PYTHONPATH="$root/src" python - "$output" "$root" <<'PY'
import json
import sys
from pathlib import Path
from nl2repobench.verification.provenance import slice_provenance

output_root = Path(sys.argv[1])
project_root = Path(sys.argv[2])
evidence = {"archive_contract": "p2-vertical-slice-v1", "controls": {}}
for name in ("call-hang", "empty", "forgery", "install-failure", "offline", "oracle", "stub"):
    job = sorted((output_root / "jobs" / name).glob("*/result.json"))[-1]
    payload = json.loads(job.read_text())
    evaluation = next(iter(payload["stats"]["evals"].values()))
    grading_path = sorted(job.parent.glob("*/verifier/grading.json"))[-1]
    grading = json.loads(grading_path.read_text())
    trial = grading_path.parent.parent
    network = json.loads((trial / "verifier/network.json").read_text())
    metrics = evaluation.get("metrics", [])
    reward = metrics[0]["reward"] if metrics else grading.get("reward", 0.0)
    evidence["controls"][name] = {
        "exceptions": evaluation["n_errors"],
        "reward": reward,
        "valid": grading.get("valid"),
        "failure_class": grading.get("failure_class"),
        "failure_reason": grading.get("failure_reason"),
        "public_network_available": network["public_network_available"],
    }
evidence["provenance"] = slice_provenance(
    project_root,
    runtime="node",
    package_manager="pnpm",
    bundle_manifest=output_root / "tasks/node-pnpm-synthetic/bundle.manifest.json",
)
evidence["all_pass"] = (
    evidence["controls"]["oracle"]["valid"] is True
    and evidence["controls"]["oracle"]["reward"] >= 0.8
    and evidence["controls"]["empty"]["reward"] == 0.0
    and evidence["controls"]["stub"]["valid"] is True
    and evidence["controls"]["stub"]["reward"] <= 0.2
    and evidence["controls"]["forgery"]["valid"] is True
    and evidence["controls"]["forgery"]["reward"] <= 0.2
    and evidence["controls"]["install-failure"]["valid"] is True
    and evidence["controls"]["call-hang"]["valid"] is True
    and evidence["controls"]["call-hang"]["reward"] <= 0.2
    and evidence["controls"]["offline"]["valid"] is True
    and evidence["controls"]["offline"]["reward"] >= 0.8
    and evidence["controls"]["offline"]["public_network_available"] is False
)
(output_root / "pnpm-evidence.json").write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
if not evidence["all_pass"]:
    raise SystemExit("pnpm control matrix did not pass")
PY
