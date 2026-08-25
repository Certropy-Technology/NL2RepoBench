#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="34f3316e0c4d93aefe33a10ceb5ba35487f14b9e7751e00aed323b7c6856264f"

printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
