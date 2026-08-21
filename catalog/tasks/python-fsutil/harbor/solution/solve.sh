#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream python-fsutil source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/python-fsutil-src >/dev/null
git -C /tmp/python-fsutil-src remote add origin https://github.com/fabiocaccamo/python-fsutil
git -C /tmp/python-fsutil-src fetch --depth 1 origin b1b1c1fa657253db6ce7fe2a4a5336c504789485 >/dev/null
git -C /tmp/python-fsutil-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/python-fsutil-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
