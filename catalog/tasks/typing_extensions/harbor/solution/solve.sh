#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream typing_extensions source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/typing_extensions-src >/dev/null
git -C /tmp/typing_extensions-src remote add origin https://github.com/python/typing_extensions
git -C /tmp/typing_extensions-src fetch --depth 1 origin 42027aba3558c9d9133a90bca17f6fecaecc48d8 >/dev/null
git -C /tmp/typing_extensions-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/typing_extensions-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
