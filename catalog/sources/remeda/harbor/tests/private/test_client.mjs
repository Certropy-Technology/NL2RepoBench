import {readFileSync, writeFileSync, chmodSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const source = '/tests/private/candidate_adapter.txt';
const adapter = '/tmp/remeda-candidate-adapter.mjs';
let ready = false;
let sequence = 0;
function ensureAdapter() {
  if (ready) return;
  try { writeFileSync(adapter, readFileSync(source), {flag: 'wx', mode: 0o555}); }
  catch (error) { if (error?.code !== 'EEXIST') throw error; }
  chmodSync(adapter, 0o555);
  ready = true;
}
export function request(operation, name, args = []) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `NODE_CANDIDATE_SITE=${site}`, `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'CI=true', 'LC_ALL=C.UTF-8', 'NODE_ALLOWED_PACKAGE=remeda', '/usr/local/bin/node', '--no-addons', adapter], {cwd: site, input: JSON.stringify({id, operation, name, args}), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  const response = JSON.parse(result.stdout);
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  if (!response.ok) throw new Error(response.message ?? 'candidate call failed');
  return response.value;
}
export function call(name, args = []) { return request('call', name, args); }
export function callLast(name, args = []) { return request('call-last', name, args); }
export function inventory() { return request('inventory'); }
