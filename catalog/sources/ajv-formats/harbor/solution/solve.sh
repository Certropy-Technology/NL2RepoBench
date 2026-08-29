#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"
PACKAGE_ARCHIVE="$SCRIPT_DIR/ajv-formats-3.0.1.tgz"
LOCKFILE="$SCRIPT_DIR/package-lock.json"
WORKSPACE="/workspace"

printf '%s  %s\n' \
  'e801e2f5c06e5cf85258abfb0d260c2d7eb2a681b525a7a447b85ff00a19d3e4' \
  "$SOURCE_ARCHIVE" | sha256sum --check --strict
printf '%s  %s\n' \
  'bcda45248cad0cfc5cbcb99e7ccf6d164b2de5864bbc671bdae7ee29c5a47b7c' \
  "$PACKAGE_ARCHIVE" | sha256sum --check --strict

SOURCE_DIR="$(mktemp -d)"
trap 'rm -rf -- "$SOURCE_DIR"' EXIT
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_DIR"
node - "$SOURCE_DIR/package.json" <<'NODE'
const fs = require("node:fs");
const manifest = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
if (manifest.name !== "ajv-formats" || manifest.version !== "3.0.1" || manifest.license !== "MIT") process.exit(1);
NODE

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xzf "$PACKAGE_ARCHIVE" --strip-components=1 -C "$WORKSPACE"
cp "$LOCKFILE" "$WORKSPACE/package-lock.json"
