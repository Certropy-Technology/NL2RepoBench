#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"chokidar","version":"5.0.0","type":"module","main":"./index.js","exports":{".":{"default":"./index.js"}}}
JSON
cat > index.js <<'JS'
export function watch() { return {on() { return this; }, add() { return this; }, unwatch() { return this; }, close: async () => {}, getWatched: () => ({})}; }
export class FSWatcher {}
export default {watch, FSWatcher};
JS
cat > index.d.ts <<'TS'
export declare function watch(): unknown;
export declare class FSWatcher {}
declare const value: {watch: typeof watch; FSWatcher: typeof FSWatcher};
export default value;
TS
cat > package-lock.json <<'JSON'
{"name":"chokidar","version":"5.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"chokidar","version":"5.0.0"}}}
JSON
