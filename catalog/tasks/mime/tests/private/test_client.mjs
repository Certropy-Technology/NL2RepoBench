import { chmodSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const source = '/tests/private/candidate_adapter.txt';
const adapter = '/tmp/mime-candidate-adapter.mjs';
let ready = false;

function call(operation, args = []) {
  if (!ready) {
    writeFileSync(adapter, readFileSync(source), {flag: 'wx', mode: 0o555});
    chmodSync(adapter, 0o555);
    ready = true;
  }
  const site = process.env.NODE_CANDIDATE_SITE;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'LC_ALL=C.UTF-8', '/usr/local/bin/node', '--no-addons', adapter,
  ], {
    cwd: site,
    input: `${JSON.stringify({operation, args})}\n`,
    encoding: 'utf8',
    timeout: 35_000,
    maxBuffer: 256 * 1024,
  });
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(response.error || 'candidate-call-failed');
  return response.value;
}

export const inventory = () => call('inventory');
export const callCandidate = (method, ...args) => call('call', [method, ...args]);
export const callLite = (method, ...args) => call('liteCall', [method, ...args]);
export const custom = () => call('custom');
export const customCase = () => call('customCase');
export const customConflict = () => call('customConflict');
export const customForce = () => call('customForce');
export const customStar = () => call('customStar');
export const immutable = () => call('immutable');
export const cli = (...args) => call('cli', args);
