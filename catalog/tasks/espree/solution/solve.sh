#!/usr/bin/env bash
set -euo pipefail

readonly REVISION='8173ecfeb7473bff90d1da11b1347082f47e262e'
readonly SOURCE_DIGEST='bc2f79fda450ef344b0696f374d492f95fee28b74254abbc1584440fd9739ac4'
readonly REPOSITORY='https://github.com/eslint/js'
readonly ROOT='/workspace'
readonly FETCH_ROOT='/tmp/espree-oracle-source'

rm -rf "$FETCH_ROOT"
mkdir -p "$FETCH_ROOT"
git -C "$FETCH_ROOT" init -q
git -C "$FETCH_ROOT" remote add origin "$REPOSITORY"
git -C "$FETCH_ROOT" fetch --depth=1 origin "$REVISION"
test "$(git -C "$FETCH_ROOT" rev-parse FETCH_HEAD)" = "$REVISION"
git -C "$FETCH_ROOT" checkout --detach -q FETCH_HEAD
actual_digest=$(git -C "$FETCH_ROOT" archive --format=tar --prefix=source/ "$REVISION" | gzip -n | sha256sum | cut -d' ' -f1)
test "$actual_digest" = "$SOURCE_DIGEST"

rm -rf "$ROOT"/* "$ROOT"/.[!.]* "$ROOT"/..?* 2>/dev/null || true
cp -R "$FETCH_ROOT/packages/espree/lib" "$ROOT/lib"
cp "$FETCH_ROOT/packages/espree/espree.js" "$ROOT/espree.js"
cp "$FETCH_ROOT/packages/espree/LICENSE" "$ROOT/LICENSE"
cat > "$ROOT/package.json" <<'JSON'
{
  "name": "espree",
  "version": "11.2.0",
  "description": "An Esprima-compatible JavaScript parser built on Acorn",
  "type": "module",
  "main": "./espree.js",
  "types": "./espree.d.ts",
  "exports": {".": {"types": "./espree.d.ts", "import": "./espree.js", "default": "./espree.js"}, "./package.json": "./package.json"},
  "files": ["lib", "espree.js", "espree.d.ts", "LICENSE"],
  "license": "BSD-2-Clause",
  "dependencies": {"acorn": "8.16.0", "acorn-jsx": "5.3.2", "eslint-visitor-keys": "5.0.1"}
}
JSON
cat > "$ROOT/espree.d.ts" <<'TYPES'
export type EcmaVersion = 3|5|6|7|8|9|10|11|12|13|14|15|16|17|2015|2016|2017|2018|2019|2020|2021|2022|2023|2024|2025|2026|'latest';
export interface Options { allowReserved?: boolean; ecmaVersion?: EcmaVersion; sourceType?: 'script'|'module'|'commonjs'; ecmaFeatures?: {jsx?: boolean; globalReturn?: boolean; impliedStrict?: boolean}; range?: boolean; loc?: boolean; tokens?: boolean; comment?: boolean; }
export function parse(code: string|String, options?: Options): any;
export function tokenize(code: string|String, options?: Options): any[] & {comments?: any[]};
export const version: string;
export const name: string;
export const Syntax: Record<string,string>;
export const VisitorKeys: Record<string, readonly string[]>;
export const latestEcmaVersion: number;
export const supportedEcmaVersions: number[];
TYPES
(cd "$ROOT" && npm install --package-lock-only --offline --ignore-scripts --no-audit --no-fund)
(cd "$ROOT" && npm ci --offline --ignore-scripts --no-audit --no-fund)
rm -rf "$ROOT/node_modules"
