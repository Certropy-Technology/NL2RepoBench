#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace
printf '%s\n' '{"name":"mdast-util-to-hast","version":"13.2.1","type":"module","exports":"./index.js","scripts":{"postinstall":"node -e \\"require(\\\\\"node:fs\\\\\").writeFileSync(\\\\\"/workspace/install-ran\\\\\",\\\\\"yes\\\\\")\\"}}' > /workspace/package.json
printf '%s\n' '{"name":"mdast-util-to-hast","version":"13.2.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"mdast-util-to-hast","version":"13.2.1"}}}' > /workspace/package-lock.json
printf '%s\n' 'export const toHast = () => null; export const defaultHandlers = {}; export const defaultFootnoteBackContent = () => []; export const defaultFootnoteBackLabel = () => "";' > /workspace/index.js
printf '%s\n' 'export {};' > /workspace/index.d.ts
