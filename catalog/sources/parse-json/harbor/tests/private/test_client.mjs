import {spawnSync} from 'node:child_process';
import {readFileSync, writeFileSync} from 'node:fs';
let sequence = 0;
const adapter = '/tmp/parse-json-candidate-adapter.mjs';
writeFileSync(adapter, readFileSync('/tests/private/candidate_adapter.txt'), {mode: 0o555});
function request(operation, value) {
  const id = `request-${++sequence}`;
  const result = spawnSync('/usr/bin/timeout', ['30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--', '/usr/local/bin/node', '--no-addons', adapter], {cwd: process.env.NODE_CANDIDATE_SITE, input: JSON.stringify({id, operation, args: [value]}), encoding: 'utf8', maxBuffer: 256 * 1024});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  return JSON.parse(result.stdout);
}
export function call(value) { return request('parse', value).value; }
export function inventory() { return request('inventory', {}).value; }
export function legacy(value) { return request('legacy', value).value; }
