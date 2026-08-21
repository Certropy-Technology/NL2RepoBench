#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream boto source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/boto-src >/dev/null
git -C /tmp/boto-src remote add origin https://github.com/boto/boto3
git -C /tmp/boto-src fetch --depth 1 origin 89d83785e73d144d96f80f80f048d63a49fc1af2 >/dev/null
git -C /tmp/boto-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/boto-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
