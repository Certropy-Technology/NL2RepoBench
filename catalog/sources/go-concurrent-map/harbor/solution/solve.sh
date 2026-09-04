#!/usr/bin/env bash
set -euo pipefail

revision=85296bce05256a80153a9e0c2bf6f4e167a4fe8d
expected_archive=8330f9e3a9b9d32e25d587cc5aae885dbafbcba94ce89fafacd35170fa899300
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
archive_path="$script_dir/source.tar"
test -f "$archive_path"
printf '%s  %s\n' "$expected_archive" "$archive_path" | sha256sum --check --strict
tar -xf "$archive_path" -C .
go mod edit -go=1.26.5
cp /opt/go-module-bundle/go.sum ./go.sum
rm -rf vendor
cp -a /opt/go-module-bundle/vendor ./vendor
env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off \
  GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  /usr/local/go/bin/go test -vet=off -mod=vendor ./...
