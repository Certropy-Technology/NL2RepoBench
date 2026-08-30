#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/GrahamDumpleton/wrapt"
readonly UPSTREAM_REVISION="537612871898f46b394477d701d26dbb78240064"
readonly SOURCE_ARCHIVE_SHA256="aa3892a27dfae6781dc98bf9a70d2cba3eb2954f6fcf8ca2d5582ae5df4c670f"
readonly ROOT="/workspace"
readonly FETCH_ROOT="/tmp/wrapt-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none --no-checkout "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD^{commit})" = "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" archive --format=tar --output="$FETCH_ROOT/source.tar" "$UPSTREAM_REVISION"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$FETCH_ROOT/source.tar" | sha256sum --check --strict

find "$ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$FETCH_ROOT/source.tar" -C "$ROOT"
rm -rf "$ROOT/.github" "$ROOT/.devcontainer" "$ROOT/.vscode" "$ROOT/docs" \
  "$ROOT/blog" "$ROOT/examples" "$ROOT/tests" "$ROOT/stress" \
  "$ROOT/AGENTS.md" "$ROOT/CLAUDE.md" "$ROOT/TESTING.md" "$ROOT/Justfile" \
  "$ROOT/RELEASE.rst" "$ROOT/pytest.ini" "$ROOT/tox.ini" "$ROOT/uv.lock"
echo "restored wrapt $UPSTREAM_REVISION"
