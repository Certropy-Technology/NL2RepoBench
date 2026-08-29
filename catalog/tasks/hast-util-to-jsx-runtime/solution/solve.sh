#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ARCHIVE="$SCRIPT_DIR/source.tar"
PACKAGE_JSON="$SCRIPT_DIR/package.json"
LOCKFILE="$SCRIPT_DIR/package-lock.json"
WORKSPACE="/workspace"

printf '%s  %s\n' \
  '0b65e0053265f212057697912c49e5d929c91d254495433fbb2a416682b91306' \
  "$SOURCE_ARCHIVE" | sha256sum --check --strict

SOURCE_DIR="$(mktemp -d)"
trap 'rm -rf -- "$SOURCE_DIR"' EXIT
tar -xf "$SOURCE_ARCHIVE" -C "$SOURCE_DIR"
node -e '
  const fs = require("node:fs");
  const path = process.argv[1];
  const packageJson = JSON.parse(fs.readFileSync(path, "utf8"));
  if (packageJson.name !== "hast-util-to-jsx-runtime" || packageJson.version !== "2.3.6" || packageJson.license !== "MIT") process.exit(1);
' "$SOURCE_DIR/source/package.json"

find "$WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$SOURCE_ARCHIVE" --strip-components=1 -C "$WORKSPACE"
cp "$PACKAGE_JSON" "$WORKSPACE/package.json"
cp "$LOCKFILE" "$WORKSPACE/package-lock.json"
node -e '
  const fs = require("node:fs");
  const path = process.argv[1];
  const built = JSON.parse(fs.readFileSync(path, "utf8"));
  if (built.name !== "hast-util-to-jsx-runtime" || built.version !== "2.3.6" || built.type !== "module") process.exit(1);
  if (built.devDependencies || built.workspaces || built.scripts?.preinstall || built.scripts?.install || built.scripts?.postinstall) process.exit(1);
' "$WORKSPACE/package.json"
