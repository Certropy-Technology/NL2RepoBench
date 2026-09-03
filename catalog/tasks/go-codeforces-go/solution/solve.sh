#!/usr/bin/env bash
set -euo pipefail

readonly revision="4996b3d7733aabafe25ba045bbc87f794d963ac4"
readonly archive_sha256="4430dd7dc9bdddc82768874bc08ecfe694234af0367f7422c612e78ddd566563"
readonly source_url="https://github.com/EndlessCheng/codeforces-go"
readonly checkout="/tmp/codeforces-go-oracle"

rm -rf "$checkout"
git init -q "$checkout"
git -C "$checkout" remote add origin "$source_url"
git -C "$checkout" fetch --depth=1 origin "$revision"
git -C "$checkout" checkout --detach FETCH_HEAD
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
test "$(git -C "$checkout" archive --format=tar HEAD | sha256sum | awk '{print $1}')" = "$archive_sha256"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf {} +
mkdir -p /workspace/copypasta /workspace/vendor
cp "$checkout/copypasta/bitset.go" /workspace/copypasta/bitset.go
cat > /workspace/go.mod <<'MOD'
module github.com/EndlessCheng/codeforces-go

go 1.26.5
MOD
: > /workspace/go.sum
: > /workspace/vendor/modules.txt

cd /workspace
env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  /usr/local/go/bin/go build -mod=vendor ./copypasta
