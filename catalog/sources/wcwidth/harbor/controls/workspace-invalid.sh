#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
mkfifo /workspace/not-a-regular-file
