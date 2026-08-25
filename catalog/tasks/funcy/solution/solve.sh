#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE="$(dirname "$0")/source.tar"
readonly SOURCE_SHA256="948092c6944f0bfd3b77b49c0eed1840e032440312c5c3019c91f2a964071b60"

printf '%s  %s\n' "$SOURCE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
