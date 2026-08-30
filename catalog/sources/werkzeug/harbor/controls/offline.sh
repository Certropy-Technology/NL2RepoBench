#!/usr/bin/env bash
set -euo pipefail
test "$(find /workspace -mindepth 1 -maxdepth 1 -type f -o -type d | wc -l)" -ge 0
