#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream docopt-ng source code ==="

# Fetch the immutable upstream revision used by this task.
git init /tmp/docopt-ng-src >/dev/null
git -C /tmp/docopt-ng-src remote add origin https://github.com/jazzband/docopt-ng
git -C /tmp/docopt-ng-src fetch --depth 1 origin 374d5a5a4bd3f829c9916d3d8dd795ec6f0d9288 >/dev/null
git -C /tmp/docopt-ng-src checkout --detach FETCH_HEAD >/dev/null

# Copy entire source tree to workspace
cd /tmp/docopt-ng-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Keep the checkout metadata: projects using VCS versioning need it during
# editable installation.  Remove only CI metadata that is irrelevant to the
# candidate workspace.
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
