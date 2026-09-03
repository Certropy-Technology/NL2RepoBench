#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
printf '%s\n' 'not a Go module' > /workspace/go.mod
