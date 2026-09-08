#!/bin/bash
# Empty workspace control - should result in low reward
set -euo pipefail
echo "=== Empty control: No implementation ==="
# Leave /workspace empty - verifier should handle gracefully
exit 0
