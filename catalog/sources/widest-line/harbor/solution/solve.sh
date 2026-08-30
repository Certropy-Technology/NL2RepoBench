#!/usr/bin/env bash
set -euo pipefail
readonly revision='d1f04193564d484ca6e24fd8d78d96545ccb0a83'
readonly expected_archive='39a6707282ade39a464de258151bb698e31daad5920fa7b40283ade60714aba7'
readonly work='/tmp/widest-line-oracle-source'
readonly archive="$work.tar"
rm -rf "$work"
git clone --quiet --filter=blob:none --no-checkout https://github.com/sindresorhus/widest-line.git "$work"
git -C "$work" checkout --quiet --detach "$revision"
test "$(git -C "$work" rev-parse HEAD)" = "$revision"
git -C "$work" archive --format=tar HEAD > "$archive"
printf '%s  %s\n' "$expected_archive" "$archive" | sha256sum --check --strict
cp "$work/index.js" /workspace/index.js
cp "$work/index.d.ts" /workspace/index.d.ts
node --input-type=module -e "import fs from 'node:fs'; const packageJson = JSON.parse(fs.readFileSync('$work/package.json', 'utf8')); delete packageJson.devDependencies; delete packageJson.scripts; delete packageJson.funding; fs.writeFileSync('/workspace/package.json', JSON.stringify(packageJson) + '\\n');"
cp /opt/npm-bundle/package-lock.json /workspace/package-lock.json
rm -rf "$work" "$archive"
