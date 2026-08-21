#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream fastapi-users source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/fastapi-users-src >/dev/null
git -C /tmp/fastapi-users-src remote add origin https://github.com/fastapi-users/fastapi-users
git -C /tmp/fastapi-users-src fetch --depth 1 origin 9d78b2a35dc7f35c2ffca67232c11f4d27a5db00 >/dev/null
git -C /tmp/fastapi-users-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/fastapi-users-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
