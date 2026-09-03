#!/usr/bin/env bash
set -euo pipefail

root="${PWD}/.oracle-source"
rm -rf "$root"
git clone --quiet https://github.com/gobwas/glob "$root"
git -C "$root" checkout --quiet --detach 986c05fb7000e63414ddc61162d0067b7a1f5639
test "$(git -C "$root" rev-parse HEAD)" = "986c05fb7000e63414ddc61162d0067b7a1f5639"
test "$(sha256sum "$root/LICENSE" | awk '{print $1}')" = "e4d63d6f9b65f053ce5beb8c5225a83c7be73010cef4fb849aca0c52d92b9236"
archive_digest="$(git -C "$root" archive --format=tar --prefix=source/ HEAD | sha256sum | awk '{print $1}')"
test "$archive_digest" = "dcf7c3e6caf75b32e832bc6236e056904ae3d96ffc23904d0a1662b84a684a07"
sed -i 's/^go 1\.22\.0$/go 1.26.5/' "$root/go.mod"
cp -a "$root"/. .
rm -rf "$root"
: > go.sum
GOOS=linux GOARCH=amd64 CGO_ENABLED=0 GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local go test -count=1 ./...
