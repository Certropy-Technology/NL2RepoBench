#!/usr/bin/env bash
set -uo pipefail
PYTHON_ROOT='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime")'
NETWORK_CHECK='import sys; sys.path.insert(0, "/opt/nl2repobench-runtime");'
NETWORK_CHECK+='from nl2repobench.verification.network_check import main; main()'
grade() {
  python3 -I -c "$PYTHON_ROOT; from nl2repobench.verification.cli import main; main()"     --runtime go --expected 1 --metric-contract fixed-test-pass-rate-v1 --output /logs/verifier "$@"
}
mkdir -p /logs/verifier
if ! python3 -I -c "$NETWORK_CHECK"   --output /logs/verifier/network.json; then
  grade --reason verifier-network-available
  exit 0
fi
COPY_WORKSPACE='from nl2repobench.verification.workspace_copy import main; main()'
if ! python3 -I -c "$PYTHON_ROOT; $COPY_WORKSPACE"   --source /workspace --destination /tmp/go-candidate; then
  grade --reason candidate-workspace-rejected
  exit 0
fi
chown -R candidate:candidate /tmp/go-candidate
rm -rf /tmp/go-candidate/vendor
cp -a /opt/go-module-bundle/vendor /tmp/go-candidate/vendor
chown -R candidate:candidate /tmp/go-candidate/vendor
GO_VALIDATE=$(cat <<'PY'
from pathlib import Path
from nl2repobench.package_managers.go_modules import GoModulesPackageManager
GoModulesPackageManager().validate_lock(
    Path("/tmp/go-candidate/go.mod"), expected_version="1.26.5"
)
PY
)
if ! runuser -u candidate -- python3 -I -c "$PYTHON_ROOT; $GO_VALIDATE"; then
  grade --reason candidate-installation-failed
  exit 0
fi
install -m 0444 /tests/private/bridge.go /tmp/go-candidate/bridge.go
mkdir -p /tmp/go-candidate/cmd/bridge
mv /tmp/go-candidate/bridge.go /tmp/go-candidate/cmd/bridge/main.go
if ! runuser -u candidate -- sh -c 'cd /tmp/go-candidate && \
  env PATH=/usr/local/go/bin:/usr/local/bin:/usr/bin:/bin \
  GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  /usr/local/go/bin/go build -mod=vendor -o /tmp/go-candidate/bridge ./cmd/bridge'; then
  grade --reason candidate-installation-failed
  exit 0
fi
RUN_CONTRACT='from nl2repobench.verification.go_contract_runner import main;'
RUN_CONTRACT+='raise SystemExit(main())'
if ! /usr/bin/python3 -I -c "$PYTHON_ROOT; $RUN_CONTRACT" \
  --script /tests/private/contract.sh --bridge /tmp/go-candidate/bridge \
  --proxy /opt/nl2repobench-runtime/nl2repobench/verification/go_bridge_proxy.py \
  > /logs/verifier/result.json; then
  cat > /tmp/go-report.json <<'JSON'
{"schema_version":"1.0","framework":"go","report_format":"go-test-json-v1","collected":1,"tests":[{"test_id":"contract::public-api","status":"failed","duration_ms":0,"details":"candidate-call-failed"}],"collection_errors":[],"runner_exit_code":1}
JSON
  grade --report /tmp/go-report.json --runner-exit-code 1
  exit 0
fi
cat > /tmp/go-report.json <<'JSON'
{"schema_version":"1.0","framework":"go","report_format":"go-test-json-v1","collected":1,"tests":[{"test_id":"contract::public-api","status":"passed","duration_ms":0}],"collection_errors":[],"runner_exit_code":0}
JSON
grade --report /tmp/go-report.json --runner-exit-code 0
exit 0
