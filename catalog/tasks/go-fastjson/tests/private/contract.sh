#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
script_dir="$(cd "$(dirname "$0")" && pwd)"
exec /usr/bin/python3 "$script_dir/contract.py" "$bridge" "$proxy"
