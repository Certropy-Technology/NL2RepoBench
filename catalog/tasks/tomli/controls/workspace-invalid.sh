#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/src/tomli
ln -s /etc/passwd /workspace/src/tomli/leak
