#!/bin/bash
# Panic control - solution script fails immediately
set -euo pipefail
echo "=== Panic control: Immediate failure ==="
echo "ERROR: Simulated panic" >&2
exit 1
