#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream tablib source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/tablib-src >/dev/null
git -C /tmp/tablib-src remote add origin https://github.com/jazzband/tablib
git -C /tmp/tablib-src fetch --depth 1 origin b68752c1ff362705f70202b4c3be163c294225a5 >/dev/null
git -C /tmp/tablib-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/tablib-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
