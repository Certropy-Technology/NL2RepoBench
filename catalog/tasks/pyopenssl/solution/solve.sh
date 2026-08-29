#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/pyca/pyopenssl"
readonly UPSTREAM_REVISION="06dd9cba948b694e8de1e79ce3a458a7775e8af5"
readonly SOURCE_ARCHIVE_SHA256="2ca6a8d913c3c717f4a4a644f7d6d12feba86906fa687c8dcfa7a069c1870385"
readonly ROOT="/workspace"
readonly FETCH_ROOT="${ROOT}/.oracle-fetch"

rm -rf "$FETCH_ROOT"
rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?*
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/tests" "$ROOT/docs" "$ROOT/requirements" "$FETCH_ROOT"
echo "restored $UPSTREAM_URL at $UPSTREAM_REVISION"
