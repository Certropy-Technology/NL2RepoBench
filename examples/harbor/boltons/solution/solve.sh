#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream boltons source code ==="

# Clone upstream repository
git clone --depth 1 https://github.com/mahmoud/boltons /tmp/boltons-src

# Copy entire source tree to workspace
cd /tmp/boltons-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Remove git directory and unnecessary files
rm -rf /workspace/.git
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
