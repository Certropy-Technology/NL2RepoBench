#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace
tar -xf /solution/source.tar -C /workspace --strip-components=1
cp /solution/package-lock.json /workspace/package-lock.json
node --input-type=module -e "import {readFileSync,writeFileSync} from 'node:fs'; const p=JSON.parse(readFileSync('/workspace/package.json','utf8')); delete p.devDependencies; delete p.scripts; writeFileSync('/workspace/package.json',JSON.stringify(p)+'\\n')"
