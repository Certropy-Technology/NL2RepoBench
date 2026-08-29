#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/sqlalchemy/alembic"
UPSTREAM_REVISION="c116cbc0f39d9df2b4ce5f1871043a622ca8774f"
SOURCE_ARCHIVE_SHA256="d152069190bef5403affcb73bd9b25cdeb34b4662a9bc8b70f9fe65968b72e72"
SOURCE_DIR=/tmp/alembic-source
SOURCE_ARCHIVE=/tmp/alembic-source.tar

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE" /workspace/*
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD^{commit})"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$resolved_revision" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
tar -xf "$SOURCE_ARCHIVE" -C /workspace
