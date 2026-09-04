#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/nhairs/python-json-logger"
readonly UPSTREAM_REVISION="806dba9d9642fbec4c8538b625494c96b288ce59"
readonly SOURCE_ARCHIVE_SHA256="b53ce02a9d27ed2c29c7452f4abed9d28cc85d0c75ae9aa4195224276bbd08eb"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly WORKSPACE="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$WORKSPACE"
rm -rf -- "$WORKSPACE/.github" "$WORKSPACE/docs" "$WORKSPACE/tests" "$WORKSPACE/scripts" \
  "$WORKSPACE/CODE_OF_CONDUCT.md" "$WORKSPACE/SECURITY.md"
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
