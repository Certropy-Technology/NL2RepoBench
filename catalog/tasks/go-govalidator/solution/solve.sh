#!/usr/bin/env bash
set -euo pipefail

readonly revision='3dd3875e2b081a20d6eed935913a482fea14ecd0'
readonly source_digest='a96caf17ed4882595950607d2567b4da764725c0de74b9ba60459a5f54f8090d'
readonly repository='https://github.com/asaskevich/govalidator.git'
readonly checkout='/tmp/govalidator-reference'

rm -rf "$checkout"
git clone --no-checkout "$repository" "$checkout"
git -C "$checkout" checkout --detach "$revision"
test "$(git -C "$checkout" rev-parse HEAD)" = "$revision"
test "$(git -C "$checkout" archive --format=tar "$revision" | sha256sum | awk '{print $1}')" = "$source_digest"

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf {} +
git -C "$checkout" archive --format=tar "$revision" | tar -x -C /workspace
sed -i 's/^go .*/go 1.26.5/' /workspace/go.mod
: > /workspace/go.sum
mkdir -p /workspace/vendor
: > /workspace/vendor/modules.txt
env GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  go -C /workspace build -mod=vendor ./...
