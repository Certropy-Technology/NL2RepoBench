import {spawnSync} from 'node:child_process';
import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const adapterSource = new URL('./candidate_adapter.txt', import.meta.url).pathname;
const adapter = '/tmp/strnum-candidate-adapter.mjs';
let adapterReady = false;
let sequence = 0;

function ensureAdapter() {
  if (adapterReady) return;
  try {
    writeFileSync(adapter, readFileSync(adapterSource), {flag: 'wx', mode: 0o555});
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
  }
  chmodSync(adapter, 0o555);
  adapterReady = true;
}

export function call(input, options = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `request-${++sequence}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s',
    'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${join(site, 'home')}`, `TMPDIR=${join(site, 'tmp')}`,
    `NODE_CANDIDATE_SITE=${site}`, 'LC_ALL=C.UTF-8',
    '/usr/local/bin/node', '--no-addons', adapter,
  ], {
    cwd: site,
    input: `${JSON.stringify({id, input, options})}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error || !result.stdout) {
    throw new Error(`candidate child failed: ${result.error?.message ?? result.stderr ?? `exit ${result.status}`}`);
  }
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error('candidate response is not JSON');
  }
  if (response.id !== id) throw new Error('candidate response id mismatch');
  return response;
}
