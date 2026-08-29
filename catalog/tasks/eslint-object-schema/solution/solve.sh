#!/usr/bin/env bash
set -euo pipefail

readonly REVISION="095661b9e87506b017e2d39fbc86e5d38d7eb91c"
readonly SOURCE_ARCHIVE_SHA256="64c90db8352d57c56779c8c2bd9df83521d6903108760aedb25df5e4e13fc99b"
readonly PACKAGE_SHA256="c0a94ca1a503b44aef6aaceb3104026a4d8afc232db998dffd490c00d87c835c"
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly WORK_DIR="$(mktemp -d /tmp/object-schema-oracle.XXXXXX)"
trap 'rm -rf "$WORK_DIR"' EXIT

test "$(sha256sum "$SCRIPT_DIR/source.tar" | awk '{print $1}')" = "$SOURCE_ARCHIVE_SHA256"
test "$(sha256sum "$SCRIPT_DIR/eslint-object-schema-3.0.5.tgz" | awk '{print $1}')" = "$PACKAGE_SHA256"
test "$(tar -tf "$SCRIPT_DIR/source.tar" | head -1)" = "source/"
test "$(tar -xOf "$SCRIPT_DIR/source.tar" source/packages/object-schema/package.json | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{const p=JSON.parse(s);process.stdout.write(p.name+"@"+p.version)})')" = "@eslint/object-schema@3.0.5"

rm -rf /workspace/*
mkdir -p /workspace
tar -xzf "$SCRIPT_DIR/eslint-object-schema-3.0.5.tgz" -C /workspace --strip-components=1
test "$(node -e 'process.stdout.write(require("/workspace/package.json").name)')" = "@eslint/object-schema"
test "$(node -e 'process.stdout.write(require("/workspace/package.json").version)')" = "3.0.5"
node - /workspace/package.json <<'NODE'
const fs = require("node:fs");
const path = process.argv[2];
const pkg = JSON.parse(fs.readFileSync(path, "utf8"));
delete pkg.scripts;
delete pkg.devDependencies;
delete pkg.workspaces;
pkg.private = true;
fs.writeFileSync(path, `${JSON.stringify(pkg, null, 2)}\n`);
NODE
cat > /workspace/package-lock.json <<'JSON'
{"name":"@eslint/object-schema","version":"3.0.5","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@eslint/object-schema","version":"3.0.5","dependencies":{}}}}
JSON
