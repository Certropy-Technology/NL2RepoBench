#!/usr/bin/env bash
set -euo pipefail

source_url='https://github.com/es-shims/String.prototype.trim'
revision='81993cc9f134d72f778bea27d77a4b1ac0e98244'
archive_sha='7bc78bdfb13f9647ad7de4835d75f48624d143fa48bc1b37d4ce75ef6c225609'
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
checkout_dir=$(mktemp -d /tmp/string-prototype-trim-oracle.XXXXXX)
trap 'rm -rf "$checkout_dir"' EXIT

git init -q "$checkout_dir/source"
git -C "$checkout_dir/source" remote add origin "$source_url"
git -C "$checkout_dir/source" fetch --quiet --depth 1 origin "$revision"
git -C "$checkout_dir/source" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$checkout_dir/source" rev-parse HEAD)" = "$revision"
actual_archive_sha=$(git -C "$checkout_dir/source" archive --format=tar HEAD | sha256sum | awk '{print $1}')
test "$actual_archive_sha" = "$archive_sha"

for file in auto.js implementation.js index.js polyfill.js shim.js LICENSE README.md; do
  cp "$checkout_dir/source/$file" "/workspace/$file"
done
cp "$script_dir/package.json" /workspace/package.json
cp "$script_dir/package-lock.json" /workspace/package-lock.json
