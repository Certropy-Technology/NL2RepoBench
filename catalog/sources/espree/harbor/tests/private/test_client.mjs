import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = process.execPath;
// The compiler places the source `harbor/tests/private` tree under the
// runtime verifier's `/tests/private/private` directory. Keep the adapter
// source lookup bound to that compiled, read-only location rather than
// relying on a workspace-relative path.
const ADAPTER_SOURCE = '/tests/private/private/candidate_adapter.txt';
const ADAPTER = '/tmp/espree-candidate-adapter.mjs';
const PACKAGE = 'espree';
let sequence = 0;
let adapterReady = false;

function ensureAdapter() {
  if (adapterReady) return;
  const source = readFileSync(ADAPTER_SOURCE);
  try { writeFileSync(ADAPTER, source, {flag: 'wx', mode: 0o555}); }
  catch (error) { if (error?.code !== 'EEXIST') throw error; }
  chmodSync(ADAPTER, 0o555);
  adapterReady = true;
}

function request(operation, payload) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `NODE_CANDIDATE_SITE=${site}`, `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    `NODE_ALLOWED_PACKAGE=${PACKAGE}`, NODE, '--no-addons', ADAPTER,
  ], {cwd: site, input: JSON.stringify({id, operation, payload}), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) {
    process.stdout.write(`candidate-child-debug: ${result.error?.message ?? result.stderr ?? 'no response'}\n`);
    throw new Error(`candidate child failed: ${result.error?.message ?? result.stderr ?? 'no response'}`);
  }
  const response = JSON.parse(result.stdout);
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  return response;
}

export function call(operation, payload) { return request(operation, payload); }
export function inventory() { return request('inventory', {}); }
