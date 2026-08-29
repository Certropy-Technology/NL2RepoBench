#!/usr/bin/env bash
set -euo pipefail

readonly expected_revision='7cf0228990eb38c27f9897f4fb17d42d39075a20'
readonly expected_source_sha='b59d0cd17c95437b3f80a0c25a69854d3ec4a5c2f27a732a9e45eabeb84faf96'
readonly archive='/solution/source.tar'

test "$(sha256sum "$archive" | awk '{print $1}')" = "$expected_source_sha"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace

node --input-type=module <<'JS'
import {readFile, writeFile, rm} from 'node:fs/promises';
const path = '/workspace/package.json';
const packageJson = JSON.parse(await readFile(path, 'utf8'));
if (packageJson.name !== 'ansi-regex' || packageJson.version !== '6.3.0') throw new Error('frozen package identity mismatch');
delete packageJson.scripts;
delete packageJson.devDependencies;
delete packageJson.xo;
await writeFile(path, `${JSON.stringify(packageJson, null, 2)}\n`);
await rm('/workspace/.npmrc', {force: true});
JS

cat > /workspace/package-lock.json <<'JSON'
{"name":"ansi-regex","version":"6.3.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"ansi-regex","version":"6.3.0","license":"MIT","type":"module","engines":{"node":">=12"}}}}
JSON
printf '%s\n' "$expected_revision" > /workspace/.nl2repobench-source-revision
