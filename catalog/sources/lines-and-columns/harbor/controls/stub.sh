#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "lines-and-columns",
  "version": "0.0.0-dev",
  "type": "module",
  "exports": {"import": "./index.mjs", "require": "./index.cjs"}
}
JSON
cat > package-lock.json <<'JSON'
{"name":"lines-and-columns","version":"0.0.0-dev","lockfileVersion":3,"packages":{"":{"name":"lines-and-columns","version":"0.0.0-dev","type":"module","exports":{"import":"./index.mjs","require":"./index.cjs"}}}}
JSON
cat > index.mjs <<'JS'
export class LinesAndColumns {
  constructor() {}
  locationForIndex() { return {line: 0, column: 0}; }
  indexForLocation() { return 0; }
}
JS
