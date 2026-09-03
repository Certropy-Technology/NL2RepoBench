#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/FactoryBoy/factory_boy"
readonly UPSTREAM_REVISION="ae9f2f4650afef0bc9b0925de97f618603233ff8"
readonly SOURCE_ARCHIVE_SHA256="9a3b710c3cc5ae1b00ef8b07a6ddae7a15f8545d9f006f256993322b867c0cd0"
readonly WORK_ROOT="/workspace"
readonly FETCH_ROOT="/tmp/factory-boy-oracle-source"

rm -rf "$FETCH_ROOT"
git clone --filter=blob:none "$UPSTREAM_URL" "$FETCH_ROOT"
git -C "$FETCH_ROOT" fetch --no-tags origin "$UPSTREAM_REVISION"
git -C "$FETCH_ROOT" checkout --detach "$UPSTREAM_REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse HEAD)" = "$UPSTREAM_REVISION"

git -C "$FETCH_ROOT" archive --format=tar HEAD > /tmp/factory-boy-source.tar
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" /tmp/factory-boy-source.tar | sha256sum --check --strict

find "$WORK_ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf /tmp/factory-boy-source.tar -C "$WORK_ROOT"
# The verified upstream archive contains two documentation-only symlinks.
# Harbor workspace ingestion is deliberately link-free, and neither path is
# needed to build or exercise the package, so remove them after verification.
rm -f "$WORK_ROOT/ChangeLog" "$WORK_ROOT/docs/credits.rst"
rm -rf "$FETCH_ROOT" /tmp/factory-boy-source.tar
printf 'restored %s at %s\n' "$UPSTREAM_URL" "$UPSTREAM_REVISION"
