#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream asteval source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/asteval-src >/dev/null
git -C /tmp/asteval-src remote add origin https://github.com/lmfit/asteval
git -C /tmp/asteval-src fetch --depth 1 origin 633bdc4ee855d426b7dcce8d1c0d907dadde4767 >/dev/null
git -C /tmp/asteval-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/asteval-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
