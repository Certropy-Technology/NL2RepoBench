#!/usr/bin/env bash
set -euo pipefail

revision='147a8591045e00d0fe8088e2393e3eefea3aa4a5'
archive_sha256='b650e76fc6fb9b6dc3ed45c5456b3226f1c05e3cf06e376f47d8b647a92ae138'
source_url='https://github.com/sindresorhus/emittery'
temporary="$(mktemp -d)"
trap 'rm -rf -- "$temporary"' EXIT

git -C "$temporary" init --quiet
git -C "$temporary" remote add origin "$source_url"
git -C "$temporary" fetch --quiet --depth=1 origin "$revision"
resolved="$(git -C "$temporary" rev-parse FETCH_HEAD)"
test "$resolved" = "$revision"
git -C "$temporary" archive --format=tar "$resolved" > "$temporary/source.tar"
printf '%s  %s\n' "$archive_sha256" "$temporary/source.tar" | sha256sum --check --status

rm -rf -- /workspace/* /workspace/.[!.]* /workspace/..?* 2>/dev/null || true
tar -xf "$temporary/source.tar" -C /workspace
test "$(node -p "require('/workspace/package.json').name")" = 'emittery'
test "$(node -p "require('/workspace/package.json').version")" = '2.0.0'
test "$(node -p "require('/workspace/package.json').license")" = 'MIT'

node <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';

const path = '/workspace/package.json';
const packageJson = JSON.parse(readFileSync(path, 'utf8'));
delete packageJson.devDependencies;
delete packageJson.scripts;
writeFileSync(path, `${JSON.stringify(packageJson, null, 2)}\n`);

const lock = {
  name: packageJson.name,
  version: packageJson.version,
  lockfileVersion: 3,
  requires: true,
  packages: {
    '': {
      name: packageJson.name,
      version: packageJson.version,
      license: packageJson.license,
      type: packageJson.type,
      engines: packageJson.engines,
    },
  },
};
writeFileSync('/workspace/package-lock.json', `${JSON.stringify(lock, null, 2)}\n`);
NODE
