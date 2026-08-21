#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream python-slugify source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/python-slugify-src >/dev/null
git -C /tmp/python-slugify-src remote add origin https://github.com/un33k/python-slugify
git -C /tmp/python-slugify-src fetch --depth 1 origin f85f9488520148d5f6899b5639199882b605e30a >/dev/null
git -C /tmp/python-slugify-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/python-slugify-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
