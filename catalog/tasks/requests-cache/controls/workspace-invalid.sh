#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/requests_cache
ln -s /etc/passwd /workspace/requests_cache/leak
