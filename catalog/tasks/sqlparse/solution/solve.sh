#!/usr/bin/env bash
set -euo pipefail
readonly ARCHIVE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/source.tar"
readonly SHA256="215f55a40819101b2ca1d0c2c983ac9182539c6c32fc8bcb93a889b2bfdfd3ed"
printf '%s  %s\n' "$SHA256" "$ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$ARCHIVE" -C /workspace
printf '%s\n' 'restored sqlparse a801100e9843786a9139bebb97c951603637129c'
