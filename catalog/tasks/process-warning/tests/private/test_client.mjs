import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER_SOURCE = '/tests/private/candidate_adapter.txt';
const ADAPTER = '/tmp/process-warning-candidate-adapter.mjs';
const PACKAGE = 'process-warning';
let sequence = 0;
let adapterReady = false;

function ensureAdapter() {
  if (adapterReady) return;
  const source = readFileSync(ADAPTER_SOURCE);
  try {
    writeFileSync(ADAPTER, source, {flag: 'wx', mode: 0o555});
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
  }
  chmodSync(ADAPTER, 0o555);
  adapterReady = true;
}

function request(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const input = JSON.stringify({id, operation, payload});
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error('request is too large');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    'TERM=dumb',
    'CI=true',
    'FORCE_COLOR=0',
    'LC_ALL=C.UTF-8',
    `NODE_ALLOWED_PACKAGE=${PACKAGE}`,
    NODE, '--no-addons', ADAPTER,
  ], {
    cwd: site,
    input,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error('candidate child returned malformed JSON');
  }
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  if (!response.ok) throw new Error(response.message ?? 'candidate call failed');
  return response.value;
}

export const inventory = () => request('inventory');
export const warning = (options, actions) => request('warning', {options, actions});
export const isolation = () => request('isolation');
export const validation = (options, factory = 'warning') => request('validation', {options, factory});
export const spy = (options, calls, lifecycle = {}) => request('spy', {options, calls, ...lifecycle});
