#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/python-jsonschema/jsonschema-specifications"
readonly UPSTREAM_REVISION="7aee138ac610b09b81aae1d338b8ed4601a01764"
readonly SOURCE_ARCHIVE_SHA256="07328bc116206bfa14d749cb01ee5039f20e0ed28bdf017bc010101f23a11053"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/jsonschema-specifications-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
rm -rf "$ROOT"/*
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"

# The frozen source uses hatch-vcs, which needs .git metadata absent from the
# archive.  Verify the source archive first, then make only the packaging
# relaxation needed to build it from the immutable archive.
sed -i 's/dynamic = \["version"\]/version = "2025.9.2"/' "$ROOT/pyproject.toml"
rm -rf "$ROOT/.github" "$ROOT/docs" "$ROOT/jsonschema_specifications/tests" "$ROOT/noxfile.py"
echo "restored and digest-verified $UPSTREAM_URL at $UPSTREAM_REVISION"
