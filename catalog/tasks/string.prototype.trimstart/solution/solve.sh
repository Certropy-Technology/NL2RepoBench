#!/usr/bin/env bash
set -euo pipefail

source_url='https://github.com/es-shims/String.prototype.trimStart'
revision='6f8ee88da5b570d3addc1e8c6caf1461013bce45'
archive_sha='84b565180bcba3823194a1c96923d64e27871375c6dcc275622907641bd50531'
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
checkout_dir=$(mktemp -d /tmp/string-prototype-trimstart-oracle.XXXXXX)
trap 'rm -rf "$checkout_dir"' EXIT

git init -q "$checkout_dir/source"
git -C "$checkout_dir/source" remote add origin "$source_url"
git -C "$checkout_dir/source" fetch --quiet --depth 1 origin "$revision"
git -C "$checkout_dir/source" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$checkout_dir/source" rev-parse HEAD)" = "$revision"
git -C "$checkout_dir/source" archive --format=tar HEAD > "$checkout_dir/source.tar"
printf '%s  %s\n' "$archive_sha" "$checkout_dir/source.tar" | sha256sum --check --strict

for file in auto.js implementation.js index.js polyfill.js shim.js LICENSE README.md package.json; do
  cp "$checkout_dir/source/$file" "/workspace/$file"
done
cp "$script_dir/package-lock.json" /workspace/package-lock.json
