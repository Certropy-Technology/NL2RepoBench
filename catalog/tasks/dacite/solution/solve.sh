#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/konradhalas/dacite"
readonly UPSTREAM_REVISION="9898ccbb783e7e6a35ae165e7deb9fa84edfe21c"
readonly SOURCE_ARCHIVE_SHA256="bd30874ca55029421d5279be2d1b327dda2b86ab1865e3bdc3cfb91e48f7e834"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly WORKSPACE="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$WORKSPACE"
rm -rf "$WORKSPACE/.github" "$WORKSPACE/.benchmarks" "$WORKSPACE/tests"
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
