#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream pytz source code ==="

# Clone upstream repository
git clone --depth 1 https://github.com/stub42/pytz /tmp/pytz-src

# Copy entire source tree to workspace
cd /tmp/pytz-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Remove git directory and unnecessary files
rm -rf /workspace/.git
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
