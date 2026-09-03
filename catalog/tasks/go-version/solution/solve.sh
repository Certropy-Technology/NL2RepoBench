#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url='https://github.com/hashicorp/go-version'
readonly revision='e2b1b0b0c4b32767e1570ddce50dff79fdddf092'
readonly archive_sha256='e79a0e175c9821ee538e9ca25a504bb15b4f445f8781a3208c4f7704c5448c12'
readonly source_dir='/tmp/go-version-source'
readonly source_archive='/tmp/go-version-source.tar'

rm -rf "$source_dir" "$source_archive"
git init -q "$source_dir"
git -C "$source_dir" remote add origin "$upstream_url"
git -C "$source_dir" fetch -q --depth 1 origin "$revision"
resolved_revision="$(git -C "$source_dir" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$revision"
git -C "$source_dir" archive --format=tar "$revision" > "$source_archive"
printf '%s  %s\n' "$archive_sha256" "$source_archive" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$source_archive" -C /workspace
cd /workspace
go mod edit -go=1.26.5
: > go.sum
mkdir -p vendor
: > vendor/modules.txt

env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  go test -count=1 ./...
