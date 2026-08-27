#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cp -a "$(dirname "$0")/oracle-package/." /workspace/
