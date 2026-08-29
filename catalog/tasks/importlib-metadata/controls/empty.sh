#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
