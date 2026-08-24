#!/usr/bin/env bash
set -euo pipefail

readonly SOURCE_ARCHIVE_SHA256="5b3f5d7aa6d5ee31659ce341bc15dee031ca631cc69e1d3ac392b4b03df6f10f"
readonly ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
readonly SOURCE_TAR="$ROOT/source/parsy-source.tar"
readonly WORKSPACE="/workspace"

rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_TAR" | sha256sum --check --strict
tar -xf "$SOURCE_TAR" -C "$WORKSPACE"
rm -rf "$WORKSPACE/.git" "$WORKSPACE/.github" "$WORKSPACE/.pytest_cache"
