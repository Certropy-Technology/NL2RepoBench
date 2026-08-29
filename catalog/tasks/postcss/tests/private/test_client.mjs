import {chmodSync, copyFileSync, mkdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const ADAPTER_DIR = '/tmp/postcss-adapter';
const ADAPTER = `${ADAPTER_DIR}/candidate_adapter.mjs`;
const ADAPTER_SOURCE = process.env.NODE_CANDIDATE_ADAPTER_SOURCE ?? '/tests/private/candidate_adapter.txt';
let ready = false;
let sequence = 0;
function setup() {
  if (ready) return;
  mkdirSync(ADAPTER_DIR, {recursive: true, mode: 0o555});
  copyFileSync(ADAPTER_SOURCE, ADAPTER, 0);
  chmodSync(ADAPTER, 0o555);
  ready = true;
}
export function call(operation, payload = {}) {
  setup();
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const id = `postcss-${++sequence}`;
  const input = JSON.stringify({id, operation, payload});
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error('request too large');
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8', '/usr/local/bin/node', '--no-addons', ADAPTER], {cwd: site, input, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error(`candidate response malformed: ${result.stdout}`); }
  if (response?.id !== id) throw new Error(response?.message ?? 'candidate child failed');
  return response;
}
export function value(operation, payload = {}) {
  const response = call(operation, payload);
  if (!response.ok) throw new Error(`${response.errorType}: ${response.message}`);
  return response.value;
}
