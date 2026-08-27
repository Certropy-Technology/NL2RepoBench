#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/horejsek/python-fastjsonschema"
UPSTREAM_REVISION="b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2"
SOURCE_ARCHIVE_SHA256="c6d2c4ec7d81009b52c35430082ab13a29a32a92e323e64ffff1d6f304ca717d"
SOURCE_DIR=/tmp/fastjsonschema-source
SOURCE_ARCHIVE=/tmp/fastjsonschema-source.tar

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$resolved_revision" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
rm -rf /workspace/*
tar -xf "$SOURCE_ARCHIVE" -C /workspace
