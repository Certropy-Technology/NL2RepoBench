#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL='https://github.com/googleapis/google-cloud-python.git'
UPSTREAM_REVISION='082a99a2c4a3e8d5df28eaeab9b2c710dd4296d5'
EXPECTED_ARCHIVE_SHA='673b703e9c4d227ea29b4f1ad06aba4c7f872cbaa634424ceb08991b113d6b07'
SOURCE_DIR=/tmp/google-cloud-python-source
ARCHIVE=/tmp/google-api-core-source.tar

rm -rf "$SOURCE_DIR" "$ARCHIVE"
git init "$SOURCE_DIR" >/dev/null
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch --depth 1 origin "$UPSTREAM_REVISION" >/dev/null
git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD >/dev/null
test "$(git -C "$SOURCE_DIR" rev-parse HEAD)" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar HEAD packages/google-api-core > "$ARCHIVE"
test "$(sha256sum "$ARCHIVE" | awk '{print $1}')" = "$EXPECTED_ARCHIVE_SHA"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$ARCHIVE" --strip-components=2 -C /workspace
rm -rf /workspace/tests /workspace/docs /workspace/testing /workspace/.github
