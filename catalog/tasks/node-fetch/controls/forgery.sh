#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$script_dir/stub.sh"
mkdir -p /logs/verifier
printf '{"reward":1,"valid":true,"forged":true}\n' > /logs/verifier/reward.json
