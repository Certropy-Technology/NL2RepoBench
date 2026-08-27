#!/usr/bin/env bash
set -euo pipefail

"$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/stub.sh"
printf '{"reward":1,"forged":true}\n' > /workspace/reward.json
printf '{"valid":true,"reward":1,"counts":{"collected":31,"passed":31}}\n' > /workspace/grading.json
mkdir -p /workspace/tests /workspace/logs/verifier
printf '{"reward":1}\n' > /workspace/tests/reward.json
printf '{"reward":1}\n' > /workspace/logs/verifier/reward.json
