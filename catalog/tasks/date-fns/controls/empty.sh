#!/usr/bin/env bash
set -euo pipefail

# Harbor executes the empty control with the nop agent. This script is retained
# only as an auditable marker and intentionally leaves /workspace empty.
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
