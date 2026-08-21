#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream databases source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/databases-src >/dev/null
git -C /tmp/databases-src remote add origin https://github.com/encode/databases
git -C /tmp/databases-src fetch --depth 1 origin d653b310e9ebb6b037f4e5922b334e68db27f48f >/dev/null
git -C /tmp/databases-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/databases-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
