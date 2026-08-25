#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output="${1:-$root/.nl2repo/go-google-uuid-controls}"
tasks="$output/tasks"
jobs="$output/jobs"
rm -rf -- "$output"
mkdir -p -- "$tasks" "$jobs"

uv=(env PYTHONPATH="$root/src" uv run --frozen)
toolchain="$root/toolchain.go.dev.lock.toml"
source="$root/catalog/sources/go-google-uuid"
go_version="$(${uv[@]} python -c 'import sys, tomllib; print(tomllib.load(open(sys.argv[1], "rb"))["go"]["version"])' "$toolchain")"

"${uv[@]}" python - <<PY
from pathlib import Path
from nl2repobench.harbor.go_compiler import GoHarborCompiler
GoHarborCompiler(Path(${toolchain@Q})).compile_task(
    Path(${source@Q}), Path(${tasks@Q}), allow_incomplete=True
)
PY

base="$tasks/go-google-uuid"
harbor=("${uv[@]}" --project "$root/harbor-runner" harbor run)
run_job() {
  local name="$1"
  local task="$2"
  "${harbor[@]}" -p "$task" -a oracle --jobs-dir "$jobs/$name"
}

"${harbor[@]}" -p "$base" -a nop --jobs-dir "$jobs/empty"
run_job oracle "$base"
run_job offline "$base"

for kind in stub forgery install-failure call-hang; do
  mkdir -p "$tasks/$kind"
  cp -a "$base/." "$tasks/$kind/"
  case "$kind" in
    stub)
      cat > "$tasks/$kind/solution/solve.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go ${go_version}
MOD
cat > go.sum <<'SUM'
SUM
cat > uuid.go <<'GO'
package uuid
type UUID [16]byte
func Parse(string) (UUID, error) { return UUID{}, nil }
func (UUID) String() string { return "" }
GO
EOF
      ;;
    forgery)
      cat > "$tasks/$kind/solution/solve.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go ${go_version}
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid
type UUID [16]byte
func Parse(string) (UUID, error) { return UUID{}, nil }
func (UUID) String() string { return "forged" }
GO
mkdir -p /logs/verifier 2>/dev/null || true
printf '%s\n' '{"reward":1,"test_pass_rate":1}' > /logs/verifier/reward.json 2>/dev/null || true
EOF
      ;;
    install-failure)
      printf '#!/usr/bin/env bash\nset -euo pipefail\nprintf broken > broken.txt\n' > "$tasks/$kind/solution/solve.sh"
      ;;
    call-hang)
      cat > "$tasks/$kind/solution/solve.sh" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go ${go_version}
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid
import "time"
type UUID [16]byte
func Parse(string) (UUID, error) { time.Sleep(60*time.Second); return UUID{}, nil }
func (UUID) String() string { return "" }
GO
EOF
      ;;
  esac
  chmod 755 "$tasks/$kind/solution/solve.sh"
  run_job "$kind" "$tasks/$kind"
done

PYTHONPATH="$root/src" python - "$jobs" "$root" <<'PY'
import json
import sys
from pathlib import Path
from nl2repobench.verification.provenance import slice_provenance

jobs_root = Path(sys.argv[1])
project_root = Path(sys.argv[2])
evidence = {"archive_contract": "p2-vertical-slice-v1", "controls": {}}
for name in sorted(path.name for path in jobs_root.iterdir() if path.is_dir()):
    results = sorted(jobs_root.joinpath(name).glob("*/result.json"))
    if not results:
        print(f"{name}: missing result")
        continue
    payload = json.loads(results[-1].read_text())
    evaluation = next(iter(payload["stats"]["evals"].values()))
    grading_path = sorted(results[-1].parent.glob("*/verifier/grading.json"))[-1]
    grading = json.loads(grading_path.read_text())
    trial = grading_path.parent.parent
    network = json.loads((trial / "verifier/network.json").read_text())
    metrics = evaluation.get("metrics", [])
    reward = metrics[0]["reward"] if metrics else grading.get("reward", 0.0)
    row = {
        "exceptions": evaluation["n_errors"],
        "reward": reward,
        "valid": grading.get("valid"),
        "failure_class": grading.get("failure_class"),
        "failure_reason": grading.get("failure_reason"),
        "public_network_available": network["public_network_available"],
    }
    evidence["controls"][name] = row
    print(json.dumps({"control": name, **row}, sort_keys=True))
evidence["all_pass"] = (
    evidence["controls"].get("oracle", {}).get("valid") is True
    and evidence["controls"].get("oracle", {}).get("reward", 0) >= 0.8
    and evidence["controls"].get("empty", {}).get("reward") == 0.0
    and evidence["controls"].get("stub", {}).get("reward", 1) <= 0.2
    and evidence["controls"].get("forgery", {}).get("reward", 1) <= 0.2
    and evidence["controls"].get("forgery", {}).get("valid") is True
    and evidence["controls"].get("install-failure", {}).get("valid") is True
    and evidence["controls"].get("call-hang", {}).get("valid") is True
    and evidence["controls"].get("offline", {}).get("valid") is True
    and evidence["controls"].get("offline", {}).get("reward", 1) >= 0.8
    and evidence["controls"].get("offline", {}).get("public_network_available") is False
)
evidence["provenance"] = slice_provenance(
    project_root,
    runtime="go",
    package_manager="go-modules",
    bundle_manifest=jobs_root.parent / "tasks/go-google-uuid/bundle.manifest.json",
)
(jobs_root.parent / "go-evidence.json").write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
if not evidence["all_pass"]:
    raise SystemExit("Go control matrix did not pass")
PY
