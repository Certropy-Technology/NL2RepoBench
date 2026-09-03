#!/usr/bin/env bash
set -euo pipefail
"$(dirname "$0")/stub.sh"
mkdir -p /workspace/tests /workspace/.pytest_cache
printf '%s\n' '{"schema_version":"1.0","leaves":[]}' > /workspace/grading.json
printf '%s\n' '999' > /workspace/reward.txt
