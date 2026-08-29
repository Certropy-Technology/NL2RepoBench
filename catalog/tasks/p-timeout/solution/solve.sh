#!/usr/bin/env bash
set -euo pipefail

revision='245066ef7daa5e74024d5b6a188ae599a1b7bfdf'
archive_sha256='4f8e9a6fa4d0b1f3db355bfec23fe3fb646abdf062e112455a78bf756eeca151'
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT

git init --quiet "$temporary/repository"
git -C "$temporary/repository" remote add origin https://github.com/sindresorhus/p-timeout.git
git -C "$temporary/repository" fetch --quiet --depth=1 origin "$revision"
actual=$(git -C "$temporary/repository" rev-parse FETCH_HEAD)
test "$actual" = "$revision"
git -C "$temporary/repository" archive --format=tar "$actual" > "$temporary/source.tar"
printf '%s  %s\n' "$archive_sha256" "$temporary/source.tar" | sha256sum --check --strict

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$temporary/source.tar" -C /workspace
cat > /workspace/package.json <<'JSON'
{
  "name": "p-timeout",
  "version": "7.0.1",
  "description": "Timeout a promise after a specified amount of time",
  "license": "MIT",
  "type": "module",
  "exports": {
    "types": "./index.d.ts",
    "default": "./index.js"
  },
  "sideEffects": false,
  "engines": {
    "node": ">=20"
  },
  "files": [
    "index.js",
    "index.d.ts"
  ]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "p-timeout",
  "version": "7.0.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "p-timeout",
      "version": "7.0.1"
    }
  }
}
JSON
