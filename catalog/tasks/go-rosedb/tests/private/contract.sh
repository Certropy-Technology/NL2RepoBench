#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
exec /usr/bin/python3 "$(dirname "$0")/contract.py" "$bridge" "$proxy"
