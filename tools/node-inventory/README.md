# Node/TypeScript Inventory

This isolated authoring tool uses the TypeScript compiler API to parse JavaScript and TypeScript without importing or executing candidate code. It emits deterministic `api-inventory` JSON with shared `symbols`, `imports`, `tests`, `risk_flags`, `metrics`, and `completeness` fields plus Node package/module metadata, exports, CommonJS/ESM symbols, signatures, locations, LOC, and syntax diagnostics.

From this directory run: `npm ci`, then `npm test`, then `npm run scan:fixture`. Scan another root with `node dist/cli.js /path/to/source --output /tmp/inventory.json`. The scanner skips `node_modules`, `.git`, and `dist`; static risks are evidence for authoring gates, not runtime proof.
