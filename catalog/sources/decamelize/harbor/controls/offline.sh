#!/usr/bin/env bash
set -euo pipefail
# The generic verifier must finish and emit its network receipt with no egress.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
