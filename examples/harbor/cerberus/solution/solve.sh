#!/usr/bin/env bash
set -euo pipefail

echo "=== Oracle: Copying upstream cerberus source code ==="

# Clone upstream repository
git clone --depth 1 https://github.com/pyeve/cerberus /tmp/cerberus-src

# Copy entire source tree to workspace
cd /tmp/cerberus-src
cp -r * /workspace/ 2>/dev/null || true
cp -r .* /workspace/ 2>/dev/null || true

# Remove git directory and unnecessary files
rm -rf /workspace/.git
rm -rf /workspace/.github

echo "✓ Oracle solution complete"
ls -la /workspace/
