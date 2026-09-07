#!/usr/bin/env bash
set -euo pipefail

# Empty workspace control - verifier should handle gracefully
# and report candidate-installation-failed

echo "=== Empty workspace control ==="
echo "Workspace is empty, no candidate implementation provided"
exit 0
