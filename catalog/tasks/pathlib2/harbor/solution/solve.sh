#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pathlib2 source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/pathlib2-src >/dev/null
git -C /tmp/pathlib2-src remote add origin https://github.com/jazzband/pathlib2
git -C /tmp/pathlib2-src fetch --depth 1 origin e9b1985b141a527061137d28a9f3c7f54e849343 >/dev/null
git -C /tmp/pathlib2-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/pathlib2-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
