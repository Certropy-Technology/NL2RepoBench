#!/usr/bin/env bash
# Control: the agent did nothing. An empty workspace must score 0 with a
# candidate-install failure, never a verifier error.
set -euo pipefail

mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
