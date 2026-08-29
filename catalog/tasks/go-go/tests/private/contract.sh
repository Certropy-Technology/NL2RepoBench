#!/usr/bin/env bash
set -euo pipefail
exec /usr/bin/python3 /tests/private/contract.py "$1" "$2"
