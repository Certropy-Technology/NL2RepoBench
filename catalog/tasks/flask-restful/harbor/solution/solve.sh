#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream flask-restful source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/flask-restful-src >/dev/null
git -C /tmp/flask-restful-src remote add origin https://github.com/flask-restful/flask-restful
git -C /tmp/flask-restful-src fetch --depth 1 origin 88cce53a8cd65830bf1815185a42ba24e5db78c6 >/dev/null
git -C /tmp/flask-restful-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/flask-restful-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
