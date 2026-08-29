#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/aio-libs/propcache"
readonly revision="1ab64c4a5c9b0bbaa94679a546afbdf28e79533f"
readonly source_digest="8f4d7e6e6a388c7d45e4830dcbfe286d3b43df40b97df0b7611f37f987ec79f2"
readonly root="/workspace"
readonly fetch_root="/tmp/propcache-oracle-source"

rm -rf "$fetch_root"
git clone --filter=blob:none --no-checkout "$upstream_url" "$fetch_root"
git -C "$fetch_root" fetch --no-tags origin "$revision"
test "$(git -C "$fetch_root" rev-parse FETCH_HEAD^{commit})" = "$revision"
git -C "$fetch_root" archive --format=tar --output="$fetch_root/source.tar" "$revision"
printf '%s  %s\n' "$source_digest" "$fetch_root/source.tar" | sha256sum --check --strict
rm -rf "$root"/*
tar -xf "$fetch_root/source.tar" -C "$root"
# Harbor's candidate workspace is a regular-file tree; changelog links are
# packaging metadata and are irrelevant to the tested runtime.
find "$root" -type l -delete
rm -rf "$root/.github" "$root/tests" "$root/docs" "$root/requirements"
echo "restored $upstream_url at $revision"
