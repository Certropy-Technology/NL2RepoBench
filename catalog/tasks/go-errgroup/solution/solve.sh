#!/usr/bin/env bash
set -euo pipefail
revision='f75267d8412fc1dfd12b343644a7ea46e4d9c85d'
upstream='https://github.com/golang/sync'
git init -q
git remote add origin "$upstream"
git fetch --depth=1 origin "$revision"
test "$(git rev-parse FETCH_HEAD)" = "$revision"
git checkout --detach -q FETCH_HEAD
source_digest='22414d7297aba3d45f32f30a1f58564a680efbf6cbfe89d30b6e3aa87c38ce09'
source_archive="$(mktemp)"
trap 'rm -f "$source_archive"' EXIT
git archive --format=tar HEAD > "$source_archive"
printf '%s  %s\n' "$source_digest" "$source_archive" | sha256sum --check --strict
sed -i 's/^go 1\.26\.0$/go 1.26.5/' go.mod
: > go.sum
