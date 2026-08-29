#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
tar -xf /solution/source.tar -C /workspace --strip-components=1
node --input-type=module -e "import {readFileSync, writeFileSync} from 'node:fs'; const path='/workspace/package.json'; const pkg=JSON.parse(readFileSync(path,'utf8')); pkg.dependencies={'@ungap/structured-clone':'1.4.0','devlop':'1.1.0','micromark-util-sanitize-uri':'2.0.1','trim-lines':'3.0.1','unist-util-position':'5.0.0','unist-util-visit':'5.1.0','vfile':'6.0.3'}; delete pkg.devDependencies; delete pkg.scripts; pkg.files=['lib/','index.js','index.d.ts']; writeFileSync(path, JSON.stringify(pkg)+'\n')"
cp /solution/package-lock.json /workspace/package-lock.json
