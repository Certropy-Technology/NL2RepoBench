#!/usr/bin/env bash
set -euo pipefail

# Empty workspace control for beartype task.
# This control leaves /workspace completely empty to verify the verifier
# handles the absence of any candidate implementation gracefully.

echo "[control:empty] Starting empty workspace control"
echo "[control:empty] Workspace /workspace will remain empty"
echo "[control:empty] Expected: candidate-installation-failed or near-zero score"
echo "[control:empty] Empty control completed"
