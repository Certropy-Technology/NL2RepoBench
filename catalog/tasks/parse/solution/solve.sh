#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="eb48010aafcc5a9699285f59fbe5abce50bacba1e6da175072163a7ed3c38176"
readonly ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
readonly SOURCE_TAR="$ROOT/source/parse-source.tar"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_TAR" | sha256sum --check --strict
tar -xf "$SOURCE_TAR" -C /workspace
rm -rf /workspace/.git /workspace/.github /workspace/.pytest_cache
