#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
cat > /workspace/package.json <<'EOF'
{
  "name": "parse5",
  "version": "8.0.1",
  "type": "module",
  "exports": "./index.js",
  "types": "./index.d.ts"
}
EOF
cat > /workspace/package-lock.json <<'EOF'
{
  "name": "parse5",
  "version": "8.0.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "parse5",
      "version": "8.0.1"
    }
  }
}
EOF
cat > /workspace/index.js <<'EOF'
const empty = () => ({nodeName: '#document', mode: 'quirks', childNodes: []});
export const parse = empty;
export const parseFragment = () => ({nodeName: '#document-fragment', childNodes: []});
export const serialize = () => '';
export const serializeOuter = () => '';
export class Parser {}
export class Tokenizer {}
export const Token = {};
export const TokenizerMode = {};
export const ErrorCodes = {};
export const foreignContent = {};
export const html = {NS: {HTML: 'http://www.w3.org/1999/xhtml'}};
export const defaultTreeAdapter = {};
EOF
cat > /workspace/index.d.ts <<'EOF'
export declare function parse(html: string, options?: object): object;
export declare function parseFragment(html: string, options?: object): object;
export declare function serialize(node: object, options?: object): string;
export declare function serializeOuter(node: object, options?: object): string;
EOF
