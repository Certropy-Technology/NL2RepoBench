#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src
cat > /workspace/package.json <<'JSON'
{
  "name": "@discoveryjs/json-ext",
  "version": "1.1.0",
  "type": "module",
  "exports": { ".": { "types": "./index.d.ts", "import": "./src/index.js" } }
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "@discoveryjs/json-ext",
  "version": "1.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": { "": { "name": "@discoveryjs/json-ext", "version": "1.1.0" } }
}
JSON
cat > /workspace/index.d.ts <<'TS'
export function parseChunked(input: unknown): Promise<unknown>;
export function stringifyChunked(value: unknown): Generator<string>;
export function stringifyInfo(value: unknown): { bytes: number; spaceBytes: number; circular: object[] };
export function parseFromWebStream(stream: unknown): Promise<unknown>;
export function createStringifyWebStream(value: unknown): ReadableStream<string>;
TS
cat > /workspace/src/index.js <<'JS'
export async function parseChunked() { return null; }
export function* stringifyChunked() { yield "null"; }
export function stringifyInfo() { return { bytes: 4, spaceBytes: 0, circular: [] }; }
export async function parseFromWebStream() { return null; }
export function createStringifyWebStream() { return new ReadableStream({ start(controller) { controller.enqueue("null"); controller.close(); } }); }
JS
