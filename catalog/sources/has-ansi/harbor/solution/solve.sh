#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "has-ansi",
  "version": "6.0.2",
  "description": "Check if a string has ANSI escape codes",
  "license": "MIT",
  "type": "module",
  "exports": {".": {"types": "./index.d.ts", "default": "./index.js"}},
  "files": ["index.js", "index.d.ts"],
  "sideEffects": false,
  "engines": {"node": ">=18"},
  "dependencies": {"ansi-regex": "^6.0.1"}
}
JSON

cat > index.js <<'JS'
import ansiRegex from 'ansi-regex';

const regex = ansiRegex({onlyFirst: true});

export default function hasAnsi(string) {
  return regex.test(string);
}
JS

cat > index.d.ts <<'TS'
/** Check if a string has ANSI escape codes. */
export default function hasAnsi(string: string): boolean;
TS

cat > package-lock.json <<'JSON'
{
  "name": "has-ansi",
  "version": "6.0.2",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "has-ansi",
      "version": "6.0.2",
      "license": "MIT",
      "dependencies": {"ansi-regex": "^6.0.1"}
    },
    "node_modules/ansi-regex": {
      "version": "6.3.0",
      "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-6.3.0.tgz",
      "integrity": "sha512-WpDfL7NO6j7tH88IDBNVdUJxDh9nmCteAVW9dsep846XdwF4naCBK+/tGLX3KJgcpgMRXCFlTM2hKGoK9FsdrQ==",
      "license": "MIT",
      "engines": {"node": ">=12"}
    }
  }
}
JSON

npm ci --offline --ignore-scripts --no-audit --no-fund
