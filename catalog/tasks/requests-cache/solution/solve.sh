#!/usr/bin/env bash
set -euo pipefail

revision='8da22ce1963788a066b65c15e6efe17ea8b4ac82'
expected_digest='aba1dbfa17ed1083567035edf760ad4264e738e7fe2f7364c7bffcb41bce89ef'
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

git clone --quiet https://github.com/requests-cache/requests-cache "$tmp_root/repo"
git -C "$tmp_root/repo" checkout --quiet --detach "$revision"
test "$(git -C "$tmp_root/repo" rev-parse HEAD)" = "$revision"
git -C "$tmp_root/repo" archive --format=tar HEAD > "$tmp_root/source.tar"
actual_digest="$(sha256sum "$tmp_root/source.tar" | awk '{print $1}')"
test "$actual_digest" = "$expected_digest"
tar -xf "$tmp_root/source.tar" -C /workspace
