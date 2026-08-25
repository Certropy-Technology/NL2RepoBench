#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="4e2ea68f7238cdb11813a33867a4caa43737d84d03bfe2c54ae5e855be8a6fe3"

printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
