#!/usr/bin/env bash
set -euo pipefail

# Offline behavior is proved by the separate verifier's network.json receipt.
# The Oracle workspace remains unchanged for that verifier-only assertion.
test -f /workspace/package.json
