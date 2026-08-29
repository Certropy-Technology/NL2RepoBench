#!/usr/bin/env bash
set -euo pipefail

revision='b9ccdaaa83f8d2f53f8acf8ff3c97b7aa21f655b'
archive_sha256='7c1a4f05591c63b2ef538dfb24df894a3ff3d2de56622a85b7787d54e3e0299b'
source_root=$(mktemp -d)
archive="$source_root/source.tar"
trap 'rm -rf "$source_root"' EXIT

git -C "$source_root" init --quiet
git -C "$source_root" remote add origin https://github.com/sindresorhus/p-locate.git
git -C "$source_root" fetch --quiet --depth=1 origin "$revision"
resolved=$(git -C "$source_root" rev-parse FETCH_HEAD)
test "$resolved" = "$revision"
git -C "$source_root" checkout --quiet --detach "$revision"
git -C "$source_root" archive --format=tar HEAD -o "$archive"
printf '%s  %s\n' "$archive_sha256" "$archive" | sha256sum --check --status

mkdir -p /workspace
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace
cat > /workspace/package.json <<'JSON'
{
  "name": "p-locate",
  "version": "7.0.0",
  "type": "module",
  "exports": {
    "types": "./index.d.ts",
    "default": "./index.js"
  },
  "files": [
    "index.js",
    "index.d.ts",
    "license",
    "readme.md"
  ],
  "engines": {
    "node": ">=20"
  },
  "dependencies": {
    "p-limit": "7.3.1"
  }
}
JSON
cp /solution/package-lock.json /workspace/package-lock.json
