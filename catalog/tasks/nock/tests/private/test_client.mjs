import { chmodSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER_SOURCE = process.env.NODE_CANDIDATE_ADAPTER_SOURCE ?? '/tests/private/candidate_adapter.txt';
const ADAPTER = '/tmp/nock-candidate-adapter.mjs';
let sequence = 0;
let adapterReady = false;

function ensureAdapter() {
  if (adapterReady) return;
  const source = readFileSync(ADAPTER_SOURCE);
  try {
    writeFileSync(ADAPTER, source, { flag: 'wx', mode: 0o555 });
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
  }
  chmodSync(ADAPTER, 0o555);
  adapterReady = true;
}

export function scenario(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const input = JSON.stringify({ id, operation, payload });
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error('request is too large');

  const constrained = [
    '--signal=TERM', '--kill-after=2s', '12s',
    'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=20', '--nproc=32', '--nofile=128', '--',
    'env', '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    NODE, '--no-addons', ADAPTER,
  ];
  const direct = [NODE, '--no-addons', ADAPTER];
  const result = spawnSync(
    process.env.NOCK_DIRECT_ADAPTER === '1' ? direct[0] : '/usr/bin/timeout',
    process.env.NOCK_DIRECT_ADAPTER === '1' ? direct.slice(1) : constrained,
    {
      cwd: site,
      input,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 15_000,
      env: process.env.NOCK_DIRECT_ADAPTER === '1' ? { ...process.env, HOME: `${site}/home`, TMPDIR: `${site}/tmp` } : undefined,
    },
  );
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error('candidate child returned malformed JSON');
  }
  if (response?.id !== id) throw new Error('candidate response id mismatch');
  if (Buffer.byteLength(JSON.stringify(response)) > 256 * 1024) throw new Error('candidate response is too large');
  return response;
}

export function value(operation, payload = {}) {
  const response = scenario(operation, payload);
  if (!response.ok) throw new Error(`${response.error}: ${response.message ?? ''}`);
  return response.value;
}
