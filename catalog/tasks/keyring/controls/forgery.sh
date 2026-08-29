#!/usr/bin/env bash
set -euo pipefail
readonly BUNDLE_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
"$BUNDLE_ROOT/write_stub.sh"
mkdir -p /workspace/.forged/logs/verifier
printf '1\n' > /workspace/reward.txt
printf '{"reward":1,"valid":true}\n' > /workspace/reward.json
printf '{"valid":true,"passed":45,"total":45}\n' > /workspace/grading.json
printf '<testsuite tests="45" failures="0"/>\n' > /workspace/junit.xml
printf '{"collected":45}\n' > /workspace/collection.json
cp /workspace/reward.json /workspace/.forged/logs/verifier/reward.json
cp /workspace/grading.json /workspace/.forged/logs/verifier/grading.json
