#!/usr/bin/env bash
set -euo pipefail

revision='fd73ef856ab4f7b6326e3255aea36f439b75e2d5'
archive_sha256='be821926713dee556bca6f0aa2cff873a8fef69d142f438327e84f08cf2d57d9'
checkout=$(mktemp -d)
archive=$(mktemp)
cleanup() {
  rm -rf -- "$checkout" "$archive"
}
trap cleanup EXIT

git -C "$checkout" init --quiet
git -C "$checkout" remote add origin https://github.com/syntax-tree/mdast-util-find-and-replace
git -C "$checkout" fetch --quiet --depth=1 origin "$revision"
actual=$(git -C "$checkout" rev-parse FETCH_HEAD)
test "$actual" = "$revision"
git -C "$checkout" archive --format=tar --output="$archive" "$actual"
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --status

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
cp /solution/package-lock.json /workspace/package-lock.json
cp /solution/index.d.ts /solution/index.d.ts.map /workspace/
mkdir -p /workspace/lib
cp /solution/lib/index.d.ts /solution/lib/index.d.ts.map /workspace/lib/
node /solution/normalize-package.mjs
