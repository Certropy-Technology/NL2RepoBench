#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
SOURCE_DIR="${SOURCE_DIR:-/tmp/iso8601-reference}"
UPSTREAM_URL="https://github.com/micktwomey/pyiso8601"
UPSTREAM_REVISION="00c9262b9ad141f287b3263be7f2244fa01988c2"
SOURCE_ARCHIVE_SHA256="6253d109a195cd118c204e64b513b14d8d07e0293c6089bf1dd1167cc2e2a97f"

rm -rf "$SOURCE_DIR" "$WORKSPACE"/*
mkdir -p "$SOURCE_DIR" "$WORKSPACE"
git -C "$SOURCE_DIR" init -q
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > /tmp/iso8601-source.tar
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" /tmp/iso8601-source.tar | sha256sum --check --strict
tar -xf /tmp/iso8601-source.tar -C "$WORKSPACE"
