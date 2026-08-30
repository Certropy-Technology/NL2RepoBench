#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/aio-libs/yarl"
readonly revision="f4314a0f11539162ea8655c591b659a9260f8e21"
readonly source_digest="6fd74fd871f05a4e41223934380e224f9f3b8383f153cdf9a468dfe55c21948f"
readonly root="/workspace"
readonly fetch_root="/workspace/.oracle-source"

rm -rf "$fetch_root"
trap 'rm -rf "$fetch_root"' EXIT
git clone --filter=blob:none --no-checkout "$upstream_url" "$fetch_root"
git -C "$fetch_root" fetch --no-tags origin "$revision"
test "$(git -C "$fetch_root" rev-parse FETCH_HEAD^{commit})" = "$revision"
git -C "$fetch_root" archive --format=tar --output="$fetch_root/source.tar" "$revision"
printf '%s  %s\n' "$source_digest" "$fetch_root/source.tar" | sha256sum --check --strict

rm -rf "$root"/*
tar -xf "$fetch_root/source.tar" -C "$root"
find "$root" -type l -delete
rm -rf \
  "$root/.github" \
  "$root/docs" \
  "$root/requirements" \
  "$root/tests" \
  "$root/benchmark.py" \
  "$root/url_benchmark.py"
echo "restored $upstream_url at $revision"
