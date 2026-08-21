#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream dictdatabase source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/dictdatabase-src >/dev/null
git -C /tmp/dictdatabase-src remote add origin https://github.com/mkrd/DictDataBase
git -C /tmp/dictdatabase-src fetch --depth 1 origin 12e650460c9284f8cd1249d26b16c18c04445691 >/dev/null
git -C /tmp/dictdatabase-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/dictdatabase-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
