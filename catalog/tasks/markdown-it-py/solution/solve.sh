#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/executablebooks/markdown-it-py"
readonly UPSTREAM_REVISION="bff75edcd7e6ce68f417803361d6e9f1223ad373"
readonly SOURCE_ARCHIVE_SHA256="16144aa1aa730efe92e175a3677d0546f571049f612a20452f47136dead1f88c"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly SOURCE_DIR="/tmp/markdown-it-py-source"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf "$SOURCE_DIR"
mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
