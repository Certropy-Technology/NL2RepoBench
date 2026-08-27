#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/build
cat > /workspace/package.json <<'JSON'
{"name":"until-async","version":"3.0.2","type":"module","main":"./build/index.js","types":"./build/index.d.ts","exports":{"./package.json":"./package.json",".":{"types":"./build/index.d.ts","default":"./build/index.js"}},"files":["build","evil-loader.mjs","node-options.txt"]}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"until-async","version":"3.0.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"until-async","version":"3.0.2"}}}
JSON
cat > /workspace/build/index.js <<'JS'
export async function until() {
  return [null, null];
}
JS
cat > /workspace/build/index.d.ts <<'TS'
export type UntilResult<RejectionReason, ResolveData> = [reason: RejectionReason, data: null] | [reason: null, data: ResolveData];
export declare function until<RejectionReason = Error, ResolveData = unknown>(callback: () => Promise<ResolveData>): Promise<UntilResult<RejectionReason, ResolveData>>;
TS
cat > /workspace/evil-loader.mjs <<'JS'
throw new Error('untrusted loader executed');
JS
printf 'NODE_OPTIONS=--loader=./evil-loader.mjs\n' > /workspace/node-options.txt
