#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream xlrd source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/xlrd-src >/dev/null
git -C /tmp/xlrd-src remote add origin https://github.com/python-excel/xlrd
git -C /tmp/xlrd-src fetch --depth 1 origin b8d573e11ec149da695d695c81a156232b89a949 >/dev/null
git -C /tmp/xlrd-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/xlrd-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
