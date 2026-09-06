#!/usr/bin/env bash
set -euo pipefail

# Leave /workspace empty so the verifier exercises candidate installation failure.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
