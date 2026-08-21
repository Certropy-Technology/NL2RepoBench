#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream math-verify source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/math-verify-src >/dev/null
git -C /tmp/math-verify-src remote add origin https://github.com/huggingface/math-verify
git -C /tmp/math-verify-src fetch --depth 1 origin 68da5f36c72d83e987bda77155c3bb26898913c0 >/dev/null
git -C /tmp/math-verify-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/math-verify-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
