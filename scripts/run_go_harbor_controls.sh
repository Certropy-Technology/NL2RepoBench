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

for kind in stub forgery install-failure call-hang; do
  mkdir -p "$tasks/$kind"
  cp -a "$base/." "$tasks/$kind/"
  case "$kind" in
    stub)
      cat > "$tasks/$kind/solution/solve.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
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
      cat > "$tasks/$kind/solution/solve.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid
import ("encoding/hex"; "fmt"; "strings" )
type UUID [16]byte
func Parse(value string) (UUID, error) { var result UUID; compact := strings.ReplaceAll(value, "-", ""); if len(compact) != 32 { return result, fmt.Errorf("invalid UUID length") }; _, err := hex.Decode(result[:], []byte(compact)); return result, err }
func (value UUID) String() string { encoded := hex.EncodeToString(value[:]); return encoded[:8]+"-"+encoded[8:12]+"-"+encoded[12:16]+"-"+encoded[16:20]+"-"+encoded[20:] }
GO
mkdir -p /logs/verifier 2>/dev/null || true
printf '%s\n' '{"reward":1,"test_pass_rate":1}' > /logs/verifier/reward.json 2>/dev/null || true
EOF
      ;;
    install-failure)
      printf '#!/usr/bin/env bash\nset -euo pipefail\nprintf broken > broken.txt\n' > "$tasks/$kind/solution/solve.sh"
      ;;
    call-hang)
      cat > "$tasks/$kind/solution/solve.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'MOD'
module github.com/google/uuid

go 1.26.5
MOD
: > go.sum
cat > uuid.go <<'GO'
package uuid
import "time"
type UUID [16]byte
func Parse(string) (UUID, error) { time.Sleep(20*time.Second); return UUID{}, nil }
func (UUID) String() string { return "" }
GO
EOF
      ;;
  esac
  chmod 755 "$tasks/$kind/solution/solve.sh"
  run_job "$kind" "$tasks/$kind"
done

python - "$jobs" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
evidence = {"archive_contract": "p2-vertical-slice-v1", "controls": {}}
for name in sorted(path.name for path in root.iterdir() if path.is_dir()):
    results = sorted(root.joinpath(name).glob("*/result.json"))
    if not results:
        print(f"{name}: missing result")
        continue
    payload = json.loads(results[-1].read_text())
    evaluation = next(iter(payload["stats"]["evals"].values()))
    metric = evaluation["metrics"][0]
    grading_path = sorted(results[-1].parent.glob("*/verifier/grading.json"))[-1]
    grading = json.loads(grading_path.read_text())
    row = {
        "exceptions": evaluation["n_errors"],
        "reward": metric["reward"],
        "valid": grading.get("valid"),
        "failure_class": grading.get("failure_class"),
        "failure_reason": grading.get("failure_reason"),
    }
    evidence["controls"][name] = row
    print(json.dumps({"control": name, **row}, sort_keys=True))
evidence["all_pass"] = (
    evidence["controls"].get("oracle", {}).get("valid") is True
    and evidence["controls"].get("oracle", {}).get("reward", 0) >= 0.8
    and evidence["controls"].get("empty", {}).get("reward") == 0.0
    and evidence["controls"].get("stub", {}).get("reward", 1) <= 0.2
    and evidence["controls"].get("forgery", {}).get("reward", 0) >= 0.8
    and evidence["controls"].get("install-failure", {}).get("valid") is True
    and evidence["controls"].get("call-hang", {}).get("valid") is True
)
(root / "go-evidence.json").write_text(json.dumps(evidence, sort_keys=True, indent=2) + "\n")
if not evidence["all_pass"]:
    raise SystemExit("Go control matrix did not pass")
PY
