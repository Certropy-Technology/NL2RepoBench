#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/invalid
ln -s /etc/passwd /workspace/invalid/escape
