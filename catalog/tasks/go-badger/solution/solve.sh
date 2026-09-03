#!/usr/bin/env bash
set -euo pipefail

revision=679bf5b72c9e1788fe7454a28fb4e140221b6668
expected_archive=af7b42e0d2322dcbaf7517db422be67f0fc62070c9e0204c9ac2f49d6a6110e9
upstream=https://github.com/dgraph-io/badger

git init -q .
git remote add origin "$upstream"
git fetch --depth=1 origin "$revision"
resolved=$(git rev-parse FETCH_HEAD)
test "$resolved" = "$revision"
git checkout -q --detach "$resolved"
archive_path=$(mktemp --tmpdir badger-source.XXXXXX.tar)
trap 'rm -f "$archive_path"' EXIT
git archive --format=tar HEAD > "$archive_path"
printf '%s  %s\n' "$expected_archive" "$archive_path" | sha256sum --check --strict

go mod edit -go=1.26.5
rm -rf vendor
cp -a /opt/go-module-bundle/vendor ./vendor
test -f vendor/modules.txt
env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  /usr/local/go/bin/go list -mod=vendor ./... >/dev/null
