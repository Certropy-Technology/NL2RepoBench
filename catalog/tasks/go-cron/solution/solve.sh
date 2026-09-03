#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL='https://github.com/robfig/cron'
readonly UPSTREAM_REVISION='bc59245fe10efaed9d51b56900192527ed733435'
readonly SOURCE_ARCHIVE_SHA256='0cedb5d66d073dc2201d192e0ca89c11b722134a03d9323134280ec647570139'
readonly SOURCE_DIR='/tmp/go-cron-source'
readonly SOURCE_ARCHIVE='/tmp/go-cron-source.tar'

rm -rf "$SOURCE_DIR" "$SOURCE_ARCHIVE"
git init -q "$SOURCE_DIR"
git -C "$SOURCE_DIR" remote add origin "$UPSTREAM_URL"
git -C "$SOURCE_DIR" fetch -q --depth 1 origin "$UPSTREAM_REVISION"
resolved_revision="$(git -C "$SOURCE_DIR" rev-parse FETCH_HEAD)"
test "$resolved_revision" = "$UPSTREAM_REVISION"
git -C "$SOURCE_DIR" archive --format=tar "$UPSTREAM_REVISION" > "$SOURCE_ARCHIVE"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$SOURCE_ARCHIVE" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" -C /workspace
cd /workspace
go mod edit -go=1.26.5
: > go.sum
mkdir -p vendor
: > vendor/modules.txt

env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local go test -count=1 ./...
