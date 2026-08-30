#!/usr/bin/env bash
set -euo pipefail

readonly expected_revision='a1bfe78e3a3de2f73ed3a7600932d7cc952732b4'
readonly expected_source_sha='83aae0869106aec568aae42cf3fc4cbf49c3dca21492dfc797d1b0b79a201077'
readonly archive='/solution/source.tar'

test "$(sha256sum "$archive" | awk '{print $1}')" = "$expected_source_sha"
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$archive" -C /workspace

node --input-type=module <<'JS'
import {readFile, writeFile, rm} from 'node:fs/promises';
const path = '/workspace/package.json';
const packageJson = JSON.parse(await readFile(path, 'utf8'));
if (packageJson.name !== 'strip-final-newline' || packageJson.version !== '4.0.0') throw new Error('frozen package identity mismatch');
delete packageJson.scripts;
delete packageJson.devDependencies;
await writeFile(path, `${JSON.stringify(packageJson, null, 2)}\n`);
await rm('/workspace/.npmrc', {force: true});
JS

cat > /workspace/package-lock.json <<'JSON'
{"name":"strip-final-newline","version":"4.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"strip-final-newline","version":"4.0.0","license":"MIT","type":"module","engines":{"node":">=18"}}}}
JSON
printf '%s\n' "$expected_revision" > /workspace/.nl2repobench-source-revision
