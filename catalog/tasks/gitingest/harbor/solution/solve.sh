#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream gitingest source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/gitingest-src >/dev/null
git -C /tmp/gitingest-src remote add origin https://github.com/coderamp-labs/gitingest
git -C /tmp/gitingest-src fetch --depth 1 origin 45b068bd5e650ac99f99b26f0767c825f8c5ce95 >/dev/null
git -C /tmp/gitingest-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/gitingest-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
