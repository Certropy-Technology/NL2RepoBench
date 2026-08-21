#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream markupsafe source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/markupsafe-src >/dev/null
git -C /tmp/markupsafe-src remote add origin https://github.com/pallets/markupsafe
git -C /tmp/markupsafe-src fetch --depth 1 origin 28ace20b140d15c083e1cbc163ee6b7778ba098c >/dev/null
git -C /tmp/markupsafe-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/markupsafe-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
