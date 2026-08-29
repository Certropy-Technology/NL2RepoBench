#!/usr/bin/env bash
set -euo pipefail
dd if=/dev/zero of=oversized.bin bs=1M count=16 status=none
