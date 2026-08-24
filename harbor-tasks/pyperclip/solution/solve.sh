#!/usr/bin/env bash
set -euo pipefail
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a "$root/source/." /workspace/
rm -rf /workspace/.git /workspace/.github /workspace/tests /workspace/__pycache__
