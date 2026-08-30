#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="6c7fa78dc6b8fc9bf5301a0a1052d336f7efa192"
readonly SOURCE_SHA256="5b4ac0fb237db87b95008d329ec1d038b3e86513ee6c11c51098f7bcc20a51b0"
readonly UPSTREAM="https://github.com/python/tzdata"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
checkout="$(mktemp -d /tmp/tzdata-oracle.XXXXXX)"
trap 'rm -rf "$checkout"' EXIT

git init -q "$checkout/repository"
git -C "$checkout/repository" fetch -q --depth=1 "$UPSTREAM" "$REVISION"
actual="$(git -C "$checkout/repository" rev-parse FETCH_HEAD)"
test "$actual" = "$REVISION"
git -C "$checkout/repository" archive --format=tar FETCH_HEAD > "$checkout/source.tar"
printf '%s  %s\n' "$SOURCE_SHA256" "$checkout/source.tar" | sha256sum --check --status
tar -xf "$checkout/source.tar" -C /workspace
