#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream python-dotenv source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/python-dotenv-src >/dev/null
git -C /tmp/python-dotenv-src remote add origin https://github.com/theskumar/python-dotenv
git -C /tmp/python-dotenv-src fetch --depth 1 origin 02b68577f37da2c4f4b9377d7a0ca2b58fdacf20 >/dev/null
git -C /tmp/python-dotenv-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/python-dotenv-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
