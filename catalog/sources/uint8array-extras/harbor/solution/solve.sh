#!/usr/bin/env bash
set -euo pipefail
readonly URL="https://github.com/sindresorhus/uint8array-extras"
readonly REV="1ba291a510461ebed324d8ccf612368a83168357"
readonly DIGEST="75e87d3a15806c0544c1182af3822fe18b9965a7d2b8ccdcad9d2564e1524886"
rm -rf /tmp/u8-source /tmp/u8-source.tar
git init -q /tmp/u8-source; git -C /tmp/u8-source remote add origin "$URL"; git -C /tmp/u8-source fetch -q --depth 1 origin "$REV"; test "$(git -C /tmp/u8-source rev-parse FETCH_HEAD^{commit})" = "$REV"; git -C /tmp/u8-source archive --format=tar "$REV" >/tmp/u8-source.tar; printf '%s  %s\n' "$DIGEST" /tmp/u8-source.tar | sha256sum -c --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +; tar -xf /tmp/u8-source.tar -C /workspace; rm -rf /workspace/.git /workspace/.github /workspace/.npmrc /workspace/benchmark.mjs /workspace/test.js
node --input-type=module <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const p=JSON.parse(readFileSync('/workspace/package.json')); delete p.devDependencies; delete p.scripts; delete p.funding; writeFileSync('/workspace/package.json',JSON.stringify(p,null,2)+'\n'); writeFileSync('/workspace/package-lock.json',JSON.stringify({name:p.name,version:p.version,lockfileVersion:3,requires:true,packages:{'':{name:p.name,version:p.version}}},null,2)+'\n');
NODE
