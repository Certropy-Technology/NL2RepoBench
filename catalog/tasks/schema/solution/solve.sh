#!/usr/bin/env bash
set -euo pipefail

SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
SOURCE_ARCHIVE_SHA256="2579256cf635a4053aaf5b0abb64f0ab403b3cb4a319e2fa8f0879e9682c5e8f"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" \
  | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
