#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'JSON'
{
  "name": "fast-string-truncated-width",
  "version": "3.0.3",
  "type": "module",
  "exports": {"types": "./index.d.ts", "default": "./index.js"},
  "files": ["index.js", "index.d.ts"],
  "scripts": {"postinstall": "node -e \"process.exit(99)\""}
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"fast-string-truncated-width","version":"3.0.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"fast-string-truncated-width","version":"3.0.3","license":"MIT"}}}
JSON
cat > /workspace/index.js <<'JS'
export default function fastStringTruncatedWidth() {
  return {width: 0, index: 0, truncated: false, ellipsed: false};
}
JS
cat > /workspace/index.d.ts <<'TS'
export type TruncationOptions = {limit?: number; ellipsis?: string; ellipsisWidth?: number};
export type WidthOptions = {controlWidth?: number; tabWidth?: number; emojiWidth?: number; regularWidth?: number; wideWidth?: number};
export type Result = {width: number; index: number; truncated: boolean; ellipsed: boolean};
export default function fastStringTruncatedWidth(input: string, truncationOptions?: TruncationOptions, widthOptions?: WidthOptions): Result;
TS
