#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream structlog source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/structlog-src >/dev/null
git -C /tmp/structlog-src remote add origin https://github.com/hynek/structlog
git -C /tmp/structlog-src fetch --depth 1 origin f5cbae43c8fd2f20eeb933e5af0134225d3daa9b >/dev/null
git -C /tmp/structlog-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/structlog-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
