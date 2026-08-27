#!/usr/bin/env bash
set -euo pipefail

install -d -m 0755 /workspace
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cp "$script_dir/package.json" "$script_dir/package-lock.json" "$script_dir/index.js" /workspace/
