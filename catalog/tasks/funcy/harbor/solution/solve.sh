#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream funcy source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/funcy-src >/dev/null
git -C /tmp/funcy-src remote add origin https://github.com/Suor/funcy
git -C /tmp/funcy-src fetch --depth 1 origin 13fac0037c109a9e4649fc8ee343be17647f7407 >/dev/null
git -C /tmp/funcy-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/funcy-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
