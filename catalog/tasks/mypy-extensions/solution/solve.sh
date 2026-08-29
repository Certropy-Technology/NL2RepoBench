#!/usr/bin/env bash
set -euo pipefail

readonly upstream_url="https://github.com/python/mypy_extensions"
readonly revision="9fc7fe08c8e638cdd9bbf1aa9bf188aef4fd24ef"
readonly archive_sha256="173418926199a751045892c046f5dcd1280f7f360ce6799ad49a54f2679af03e"
readonly checkout="/tmp/mypy-extensions-oracle-source"
readonly archive="/tmp/mypy-extensions-oracle.tar"

rm -rf -- "$checkout" "$archive"
mkdir -p "$checkout"
git -C "$checkout" init --quiet
git -C "$checkout" remote add origin "$upstream_url"
git -C "$checkout" fetch --quiet --depth=1 origin "$revision"
git -C "$checkout" checkout --quiet --detach FETCH_HEAD

resolved="$(git -C "$checkout" rev-parse HEAD)"
test "$resolved" = "$revision"
git -C "$checkout" archive --format=tar HEAD > "$archive"
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --status

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
rm -rf -- "$checkout" "$archive"
