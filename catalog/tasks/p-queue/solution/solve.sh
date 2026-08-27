#!/usr/bin/env bash
set -euo pipefail
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_archive="$script_dir/source.tar"
printf '%s  %s\n' \
  '2dd1f460de3562b9c6b84f6de66ecf722ed52730dfcc877c02b6f9731351e79b' \
  "$source_archive" | sha256sum --check --strict
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
tar -xf "$source_archive" -C /workspace
rm -f /workspace/.npmrc
cp -a "$script_dir/package/." /workspace/
