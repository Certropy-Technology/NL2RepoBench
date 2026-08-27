#!/usr/bin/env bash
set -uo pipefail
rm -rf /tmp/candidate /tmp/candidate-build /tmp/candidate-site
mkdir -p /logs/verifier /tmp/trusted-results /tmp/candidate-site
chmod 0700 /logs/verifier /tmp/trusted-results

export NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site
python -I -m nl2repobench.verification.network_check   --output /logs/verifier/network.json
if [[ "$?" -ne 0 ]]; then
  python -I -m nl2repobench.verification.cli     --expected 72 --runtime python --metric-contract fixed-test-pass-rate-v1     --reason verifier-network-available
  exit 0
fi
python -I -B -m nl2repobench.verification.workspace_copy   --source /workspace --destination /tmp/candidate
if [[ "$?" -ne 0 ]]; then
  python -I -m nl2repobench.verification.cli     --expected 72 --runtime python --metric-contract fixed-test-pass-rate-v1     --reason candidate-workspace-rejected
  exit 0
fi
chown -R candidate:candidate /tmp/candidate /tmp/candidate-site
python -I -B -m nl2repobench.verification.candidate_install   --source /tmp/candidate --target /tmp/candidate-site   --timeout-sec 60.0   --address-space-bytes 2147483648   --cflags '-O0 -g0'      --status /logs/verifier/candidate-install.json
if [[ "$?" -ne 0 ]]; then
  python -I -m nl2repobench.verification.cli     --expected 72 --runtime python --metric-contract fixed-test-pass-rate-v1     --reason candidate-installation-failed
  exit 0
fi
python -I -m nl2repobench.verification.custom_verifier   --entrypoint /tests/verifier/run.py --expected 72   --junit /logs/verifier/junit.xml   --collection /logs/verifier/collection.json   --timeout-sec 60.0   > /logs/verifier/custom-stdout.txt   2> /logs/verifier/custom-stderr.txt
custom_exit=$?
if [[ "$custom_exit" -ne 0 && "$custom_exit" -ne 1 ]]; then
  python -I -m nl2repobench.verification.cli     --expected 72 --runtime python --metric-contract fixed-test-pass-rate-v1     --reason verifier-internal-error
  exit 0
fi
python -I -m nl2repobench.verification.cli   --expected 72 --runtime python --metric-contract fixed-test-pass-rate-v1   --collection /logs/verifier/collection.json   --junit /logs/verifier/junit.xml --pytest-exit-code "$custom_exit"
exit 0
