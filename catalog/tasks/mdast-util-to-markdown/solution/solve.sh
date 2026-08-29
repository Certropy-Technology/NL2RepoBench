#!/usr/bin/env bash
set -euo pipefail

revision='ee3b3458a466c3224800ac7fa688b4a160a91ea2'
source_sha256='de486cc3d34b204e8db55cd7e97074f60a8ede2e9b57bbe8cb8e2991ad1ddc5c'
temporary=$(mktemp -d)
trap 'rm -rf "$temporary"' EXIT
cd /

git init "$temporary/repository"
git -C "$temporary/repository" remote add origin https://github.com/syntax-tree/mdast-util-to-markdown.git
git -C "$temporary/repository" fetch --no-tags --depth=1 origin "$revision"
test "$(git -C "$temporary/repository" rev-parse FETCH_HEAD)" = "$revision"
git -C "$temporary/repository" archive --format=tar --output="$temporary/source.tar" FETCH_HEAD
echo "$source_sha256  $temporary/source.tar" | sha256sum --check --strict

rm -rf /workspace
mkdir -p /workspace
tar -xf "$temporary/source.tar" -C /workspace
rm -f /workspace/.npmrc

node --input-type=module <<'NODE'
import {readFileSync, writeFileSync} from 'node:fs';

const path = '/workspace/package.json';
const manifest = JSON.parse(readFileSync(path, 'utf8'));
manifest.dependencies = {
  '@types/mdast': '4.0.4',
  '@types/unist': '3.0.3',
  'longest-streak': '3.1.0',
  'mdast-util-phrasing': '4.1.0',
  'mdast-util-to-string': '4.0.0',
  'micromark-util-classify-character': '2.0.1',
  'micromark-util-decode-string': '2.0.1',
  'unist-util-visit': '5.1.0',
  zwitch: '2.0.4',
};
delete manifest.devDependencies;
delete manifest.scripts;
writeFileSync(path, JSON.stringify(manifest, null, 2) + '\n');
NODE

cp /solution/package-lock.json /workspace/package-lock.json
