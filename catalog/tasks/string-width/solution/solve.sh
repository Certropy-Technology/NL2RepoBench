#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REVISION="64dc20cddd374df0ff43ba3469491ae98cf0cdfc"
SOURCE_ARCHIVE_SHA256="6ae9442b3cfdcbe991f61655f1683636a45aff00869eaf05bd9335215faf4171"
archive="/tmp/string-width-${UPSTREAM_REVISION}.tar.gz"
root="/tmp/string-width-${UPSTREAM_REVISION}"

rm -rf /workspace/* "$archive" "$root"
curl --fail --location --silent --show-error \
  "https://codeload.github.com/sindresorhus/string-width/tar.gz/${UPSTREAM_REVISION}" \
  --output "$archive"
printf '%s  %s\n' "$SOURCE_ARCHIVE_SHA256" "$archive" | sha256sum --check --strict
tar -xzf "$archive" -C /tmp
test "$(git -C "$root" rev-parse --is-inside-work-tree 2>/dev/null || true)" = "" || true
cp -a "$root"/. /workspace/
rm -rf "$root" "$archive"
rm -f /workspace/.npmrc
node --input-type=module - <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';
const path = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(path, 'utf8'));
delete manifest.devDependencies;
delete manifest.scripts;
manifest.dependencies = {
  'get-east-asian-width': '1.5.0',
  'strip-ansi': '7.1.2',
};
writeFileSync(path, JSON.stringify(manifest) + '\n');
NODE
cat > /workspace/package-lock.json <<'JSON'
{"name":"string-width","version":"8.2.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"string-width","version":"8.2.2","dependencies":{"get-east-asian-width":"^1.5.0","strip-ansi":"^7.1.2"}},"node_modules/ansi-regex":{"version":"6.3.0","resolved":"https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.3.0.tgz","integrity":"sha512-WpDfL7NO6j7tH88IDBNVdUJxDh9nmCteAVW9dsep846XdwF4naCBK+/tGLX3KJgcpgMRXCFlTM2hKGoK9FsdrQ==","license":"MIT"},"node_modules/get-east-asian-width":{"version":"1.5.0","resolved":"https://registry.npmjs.org/get-east-asian-width/-/get-east-asian-width-1.5.0.tgz","integrity":"sha512-CQ+bEO+Tva/qlmw24dCejulK5pMzVnUOFOijVogd3KQs07HnRIgp8TGipvCCRT06xeYEbpbgwaCxglFyiuIcmA==","license":"MIT"},"node_modules/strip-ansi":{"version":"7.1.2","resolved":"https://registry.npmjs.org/strip-ansi/-/strip-ansi-7.1.2.tgz","integrity":"sha512-gmBGslpoQJtgnMAvOVqGZpEz9dyoKTCzy2nfz/n8aIFhN/jCE/rCmcxabB6jOOHV+0WNnylOxaxBQPSvcWklhA==","license":"MIT","dependencies":{"ansi-regex":"^6.0.1"}}}}
JSON
