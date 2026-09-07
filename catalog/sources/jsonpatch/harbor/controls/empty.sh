#!/bin/bash
set -euo pipefail

# Empty control - leave workspace empty
# Expected: installation should fail or reward near 0

echo "=== Empty Control ==="
echo "Workspace left empty (no files generated)"
echo "Expected outcome: candidate-installation-failed or reward near 0"

# Workspace is already empty, do nothing
exit 0
