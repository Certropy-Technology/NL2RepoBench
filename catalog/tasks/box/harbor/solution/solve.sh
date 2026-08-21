#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream box source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/box-src >/dev/null
git -C /tmp/box-src remote add origin https://github.com/cdgriffith/Box
git -C /tmp/box-src fetch --depth 1 origin b071107161228f32762ece8f6039b6906c2570db >/dev/null
git -C /tmp/box-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/box-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
