#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/coveragepy/coveragepy"
UPSTREAM_REVISION="aeaa79b812d1bc637ebb5582ab12c076e192c87e"
SOURCE_ARCHIVE_SHA256="d4c34fff118dcfe6e22a637411cdd5c5a7605dd2e65ed510560637ee94467e56"
SOURCE_DIR=/tmp/coverage-source
SOURCE_ARCHIVE=/tmp/coverage-source.tar

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
