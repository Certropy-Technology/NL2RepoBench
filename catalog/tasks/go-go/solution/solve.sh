#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/TheAlgorithms/Go"
readonly revision="5ba447ec5ff3d1213de65b92e726ee74c5d5cc19"
readonly archive_sha256="b3c92e9e75f682b5543bf069e4c2fc8fce0eda7067639185bd92e686cc648507"
readonly source_dir="$(mktemp -d)"
readonly source_archive="$(mktemp)"
trap 'rm -rf "$source_dir" "$source_archive"' EXIT

git -C "$source_dir" init -q
git -C "$source_dir" remote add origin "$upstream_url"
git -C "$source_dir" fetch -q --depth 1 origin "$revision"
resolved_revision="$(git -C "$source_dir" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$revision"
git -C "$source_dir" archive --format=tar FETCH_HEAD > "$source_archive"
printf '%s  %s\n' "$archive_sha256" "$source_archive" \
  | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$source_archive" -C /workspace
cd /workspace
go mod edit -go=1.26.5
: > go.sum
mkdir -p vendor
: > vendor/modules.txt

env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  go test -count=1 ./conversion
