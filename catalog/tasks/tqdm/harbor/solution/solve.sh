#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream tqdm source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/tqdm-src >/dev/null
git -C /tmp/tqdm-src remote add origin https://github.com/tqdm/tqdm
git -C /tmp/tqdm-src fetch --depth 1 origin 0ed5d7f18fa3153834cbac0aa57e8092b217cc16 >/dev/null
git -C /tmp/tqdm-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/tqdm-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
