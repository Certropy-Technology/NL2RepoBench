#!/usr/bin/env bash
set -euo pipefail
exec /usr/bin/python3 "$(dirname "$0")/contract.py" "$1" "$2"
