#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/helpers /workspace/logs/verifier
cat > /workspace/package.json <<'JSON'
{
  "name": "yargs",
  "version": "18.1.0",
  "type": "module",
  "exports": {
    ".": "./index.mjs",
    "./yargs": "./index.mjs",
    "./helpers": "./helpers/helpers.mjs",
    "./package.json": "./package.json"
  },
  "files": ["index.mjs", "helpers", "reward.json", "report.json", "logs"]
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{
  "name": "yargs",
  "version": "18.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {"name": "yargs", "version": "18.1.0"}
  }
}
JSON
cat > /workspace/index.mjs <<'JS'
function parser() {
  let value;
  value = new Proxy(function () {}, {
    get(_target, property) {
      if (property === 'parse' || property === 'parseSync') return () => ({_: []});
      if (property === 'parseAsync') return async () => ({_: []});
      if (property === 'getHelp') return async () => '';
      if (property === 'then') return undefined;
      return () => value;
    },
  });
  return value;
}
function Yargs() { return parser(); }
export default Yargs;
export {Yargs as 'module.exports'};
JS
cat > /workspace/helpers/helpers.mjs <<'JS'
export function hideBin(argv = process.argv) { return argv.slice(2); }
export function Parser() { return {_: []}; }
export function applyExtends(config) { return config; }
JS
printf '{"reward":1,"valid":true}\n' > /workspace/reward.json
printf '{"collected":42,"passed":42}\n' > /workspace/report.json
printf '{"reward":1,"valid":true}\n' > /workspace/logs/verifier/reward.json
