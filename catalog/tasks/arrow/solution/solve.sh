#!/usr/bin/env bash
set -euo pipefail

# Oracle-only reference source acquisition. This script is uploaded exclusively
# to the trusted Oracle run; the model Agent receives no source-host access.
readonly UPSTREAM_URL="https://github.com/arrow-py/arrow"
readonly UPSTREAM_REVISION="2224255c4acc594d734cef0bbc83360452a67983"
readonly SOURCE_ARCHIVE_SHA256="8c08b167afc01268080ba13e5e1cf17223ec2fe12512fd298f03132270f7cda6"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
test "$UPSTREAM_REVISION" = "2224255c4acc594d734cef0bbc83360452a67983"
echo "restored arrow-py/arrow at $UPSTREAM_REVISION"
