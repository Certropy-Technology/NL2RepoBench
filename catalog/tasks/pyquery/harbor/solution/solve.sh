#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pyquery source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/pyquery-src >/dev/null
git -C /tmp/pyquery-src remote add origin https://github.com/gawel/pyquery
git -C /tmp/pyquery-src fetch --depth 1 origin 6c996addb86bf28810191126a6bae8f50b77bd65 >/dev/null
git -C /tmp/pyquery-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/pyquery-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
