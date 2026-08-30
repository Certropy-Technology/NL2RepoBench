#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/Borewit/strtok3"
readonly revision="acac939a405a6dfebcf3fe9b9caba3641c491c95"
readonly source_digest="07d655e73200185f3c76b21a86538e09fddb9e3971bc907641d1929bdfa3c54c"
readonly script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
readonly fetch_root="/tmp/strtok3-oracle-source"

rm -rf "$fetch_root"
git clone --filter=blob:none --no-checkout "$upstream_url" "$fetch_root"
git -C "$fetch_root" fetch --no-tags origin "$revision"
test "$(git -C "$fetch_root" rev-parse FETCH_HEAD^{commit})" = "$revision"
git -C "$fetch_root" archive --format=tar --output="$fetch_root/source.tar" "$revision"
printf '%s  %s\n' "$source_digest" "$fetch_root/source.tar" | sha256sum --check --strict

rm -rf /workspace/*
tar -xf "$fetch_root/source.tar" -C /workspace
rm -rf /workspace/lib
cp -a "$script_dir/lib" /workspace/lib
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json
rm -rf /workspace/.git /workspace/node_modules /workspace/test /workspace/.github
echo "restored $upstream_url at $revision with frozen compiled distribution"
