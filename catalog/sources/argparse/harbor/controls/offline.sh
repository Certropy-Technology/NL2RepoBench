#!/usr/bin/env bash
set -euo pipefail
# The derived control intentionally leaves an empty workspace. Its verifier
# path must still complete and emit a no-network receipt without egress.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
