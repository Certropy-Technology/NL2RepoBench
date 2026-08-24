#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
cp -a "$script_dir/package-template/." /workspace/
