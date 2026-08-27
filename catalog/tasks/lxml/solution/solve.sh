#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR=/workspace/reference
UPSTREAM_URL=https://github.com/lxml/lxml.git
UPSTREAM_REVISION=36f11f9d5edca7e85d20102fa253c1dad42929ee
SOURCE_ARCHIVE_SHA256=cac1e83f3fa07b77097da8f98cb58bd4b2bc3e6b5a55eb7b6c942ed1b0e66d29
export PIP_DISABLE_PIP_VERSION_CHECK=1

mkdir -p "$SOURCE_DIR"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar FETCH_HEAD > /tmp/lxml.tar
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" /tmp/lxml.tar | sha256sum --check --strict
tar -xf /tmp/lxml.tar -C /workspace
rm -rf "$SOURCE_DIR" /tmp/lxml.tar
python -m pip install --no-build-isolation .
