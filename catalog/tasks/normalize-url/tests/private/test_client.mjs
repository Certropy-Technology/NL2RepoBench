import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
const NODE = '/usr/local/bin/node';
const PACKAGE = 'normalize-url';
const ADAPTER = '/tmp/normalize-url-candidate-adapter.mjs';
let sequence = 0;
let adapterReady = false;
function ensureAdapter() {
  if (adapterReady) return;
  const source = readFileSync(new URL('./candidate_adapter.txt', import.meta.url));
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
  const input = JSON.stringify({id, operation, payload});
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `NODE_ALLOWED_PACKAGE=${PACKAGE}`, NODE, '--no-addons', ADAPTER], {cwd: site, input, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  const response = JSON.parse(result.stdout);
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  return response;
}
export function call(url, options) { return request('call', {args: options === undefined ? [url] : [url, options]}); }
export function inventory() { return request('inventory', {}); }
