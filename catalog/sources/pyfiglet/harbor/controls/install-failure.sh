#!/bin/bash
# install-failure.sh - Simulate installation failure
set -euo pipefail

echo "ERROR: Simulated installation failure" >&2
exit 1
