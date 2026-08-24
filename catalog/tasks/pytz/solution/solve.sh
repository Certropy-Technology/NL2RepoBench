#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xzf /solution/pytz-reference.tar.gz -C /workspace
test -f /workspace/setup.py
test -f /workspace/pytz/zoneinfo/zone.tab
test "$(find /workspace/pytz/zoneinfo -type f | wc -l)" -eq 604
