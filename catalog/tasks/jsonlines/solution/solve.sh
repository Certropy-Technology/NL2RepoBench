#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"
SOURCE_ARCHIVE_SHA256=fd839af51a766d70dccb95db84e6bcf741f55b01ed756b817be4838f202407a6

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
