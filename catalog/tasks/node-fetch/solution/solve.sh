#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$script_dir/source.tar" -C /workspace
printf '%s  %s\n' \
  'c54ad1e222b0dab09410542e9142b5374a63a72b2e5cc8e931b147559628265c' \
  "$script_dir/source.tar" | sha256sum --check --strict
cp "$script_dir/package.runtime.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json
rm -f /workspace/.npmrc
