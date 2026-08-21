#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream schema source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/schema-src >/dev/null
git -C /tmp/schema-src remote add origin https://github.com/keleshev/schema
git -C /tmp/schema-src fetch --depth 1 origin 7434a6b3c9cd1672f0d491ed45114054750627af >/dev/null
git -C /tmp/schema-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/schema-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
