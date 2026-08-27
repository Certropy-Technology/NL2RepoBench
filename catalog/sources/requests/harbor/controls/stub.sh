#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
printf '%s\n' '# empty candidate control' > /workspace/README.md
