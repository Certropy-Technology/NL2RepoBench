import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = process.env.NODE_BINARY ?? '/usr/local/bin/node';
const ADAPTER_SOURCE = '/tests/private/candidate_adapter.txt';
const ADAPTER = '/tmp/immer-candidate-adapter.mjs';
let sequence = 0;

function ensureAdapter() {
  if (readFileSync(ADAPTER, {encoding: 'utf8', flag: 'a+'}).length > 0) return;
  const source = readFileSync(ADAPTER_SOURCE);
  writeFileSync(ADAPTER, source, {flag: 'w', mode: 0o555});
  chmodSync(ADAPTER, 0o555);
}

export function request(operation, payload) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const input = JSON.stringify({id, operation, payload});
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    'NODE_ALLOWED_PACKAGE=immer', NODE, '--no-addons', ADAPTER,
  ], {cwd: site, input, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  return response;
}

export function call(operation, payload) { return request(operation, payload); }
