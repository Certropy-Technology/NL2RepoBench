#!/usr/bin/env bash
set -euo pipefail
revision="2ab893bb7af49f55a4180d22371fbe9f954203b4"
expected_digest="sha256:18957a3e43ffb9b662c49467f7b52beadd78292bfb81505ba85d01bc2411a4b7"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git clone --no-checkout https://github.com/matoous/go-nanoid "$tmp/src"
git -C "$tmp/src" checkout --detach "$revision"
test "$(git -C "$tmp/src" rev-parse HEAD)" = "$revision"
actual_digest="sha256:$(git -C "$tmp/src" archive --format=tar "$revision" | sha256sum | awk '{print $1}')"
test "$actual_digest" = "$expected_digest"
git -C "$tmp/src" archive --format=tar "$revision" | tar -x -C /workspace
cat > /workspace/go.mod <<'MOD'
module github.com/matoous/go-nanoid/v2

go 1.26.5
MOD
: > /workspace/go.sum
mkdir -p /workspace/vendor
: > /workspace/vendor/modules.txt
