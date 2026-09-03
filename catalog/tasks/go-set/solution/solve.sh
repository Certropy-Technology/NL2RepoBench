#!/usr/bin/env bash
set -euo pipefail

repo='https://github.com/deckarep/golang-set.git'
revision='da03b7639be5170e7b8fc7183b2d4663a4133419'
expected_source_digest='sha256:9d77361bf07b5ecfcc236a1972f9aa524209dab5f300e774ca5b068a1aea4880'
work='/tmp/go-set-oracle-source'
rm -rf "$work"
git clone --filter=blob:none --no-checkout "$repo" "$work"
git -C "$work" checkout --detach "$revision"
test "$(git -C "$work" rev-parse HEAD)" = "$revision"
archive='/tmp/go-set-source.tar'
git -C "$work" archive --format=tar "$revision" > "$archive"
archive_digest="$(sha256sum "$archive" | awk '{print $1}')"
archive_bytes="$(stat -c '%s' "$archive")"
printf 'source_revision=%s\nsource_archive_sha256=sha256:%s\nsource_archive_bytes=%s\n' \
  "$revision" "$archive_digest" "$archive_bytes" >&2
if [ "$expected_source_digest" != 'SOURCE_DIGEST_TO_BE_FILLED' ]; then
  test "sha256:$archive_digest" = "$expected_source_digest"
fi
tar -xf "$archive" -C /workspace
cd /workspace
go mod edit -go=1.26.5
rm -rf vendor
cp -a /opt/go-module-bundle/vendor /workspace/vendor
GOWORK=off GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local \
  go test -mod=vendor -vet=off -count=1 -json ./... > /tmp/go-set-upstream-tests.json
cat /tmp/go-set-upstream-tests.json >&2
