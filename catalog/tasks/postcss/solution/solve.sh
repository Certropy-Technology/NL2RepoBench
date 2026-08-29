#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${1:-/workspace}"
archive="$here/source.tar"
expected_archive="58ec002726ff181bc854a0d8c91e4bd6b261ff2cfb1b60be8385f568aa938e55"
expected_revision="6d23bc362203118478bc8051b81f2910907ebe6e"

printf '%s  %s\n' "$expected_archive" "$archive" | sha256sum --check --strict
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
tar -xf "$archive" -C "$scratch"
test "$(git -C "$here" rev-parse --verify HEAD 2>/dev/null || true)" = "" || true
test -f "$scratch/package.json"
node -e '
  const fs = require("node:fs");
  const p = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
  if (p.name !== "postcss" || p.version !== "8.5.26" || p.license !== "MIT") process.exit(1);
' "$scratch/package.json"

mkdir -p "$target"
cp -a "$scratch/lib" "$target/lib"
cp "$scratch/LICENSE" "$target/LICENSE"
cp "$scratch/package.json" "$target/upstream.package.json"
cp "$here/package.json" "$target/package.json"
cp "$here/package-lock.json" "$target/package-lock.json"
printf '%s\n' "$expected_revision" > "$target/.nl2repobench-source-revision"
