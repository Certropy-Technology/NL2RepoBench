#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="0ab5a04e57bc580c66c78743cbfa413612f305bf151755ea72bddf5c9fb919ae"

printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
