#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_REVISION="62c5068c971579d61fa1b55373390e12f25fd856"
readonly SOURCE_ARCHIVE_SHA256="503ed1fbb3efd07a9145b2f5ed05169728319e75d8117a4ef986e3aa91ea33f4"
readonly REVISION_FILE="/solution/revision.txt"
readonly SOURCE_ARCHIVE="/solution/source.tar"
readonly ROOT="/workspace"

printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict
find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C "$ROOT"
test "$UPSTREAM_REVISION" = "62c5068c971579d61fa1b55373390e12f25fd856"
test "$(cat "$REVISION_FILE")" = "$UPSTREAM_REVISION"
echo "restored python-hyper/h11 at $UPSTREAM_REVISION"
