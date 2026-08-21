#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream dbutils source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/dbutils-src >/dev/null
git -C /tmp/dbutils-src remote add origin https://github.com/WebwareForPython/DBUtils
git -C /tmp/dbutils-src fetch --depth 1 origin 52db5032c9fb31341b34079f6ebacd11738a00d1 >/dev/null
git -C /tmp/dbutils-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/dbutils-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
