import { chmodSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

const adapterSource = new URL('./candidate_adapter.txt', import.meta.url).pathname;
const adapter = '/tmp/json-stable-stringify-candidate-adapter.mjs';
let sequence = 0;
let adapterReady = false;

function ensureAdapter() {
  if (adapterReady) return;
  const source = readFileSync(adapterSource);
  try { writeFileSync(adapter, source, { flag: 'wx', mode: 0o555 }); }
  catch (error) { if (error?.code !== 'EEXIST') throw error; }
  chmodSync(adapter, 0o555);
  adapterReady = true;
}

export function call(caseId) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `case-${++sequence}`;
  const result = spawnSync(
    '/usr/bin/timeout',
    ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
      '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--',
      'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${join(site, 'home')}`,
      `TMPDIR=${join(site, 'tmp')}`, 'LC_ALL=C.UTF-8', `NODE_CANDIDATE_SITE=${site}`,
      '/usr/local/bin/node',
      '--no-addons', adapter],
    { cwd: site, input: JSON.stringify({ id, caseId }), encoding: 'utf8', maxBuffer: 256 * 1024 },
  );
  if (result.error || !result.stdout) {
    throw new Error(`candidate child failed: ${result.error?.message ?? result.stderr ?? `exit ${result.status}`}`);
  }
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error('candidate response is not JSON'); }
  if (response.id !== id) throw new Error('candidate response id mismatch');
  return response;
}
