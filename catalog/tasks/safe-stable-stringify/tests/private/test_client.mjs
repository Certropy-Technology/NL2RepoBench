import { chmodSync, readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
const source = new URL('./candidate_adapter.txt', import.meta.url).pathname;
const adapter = '/tmp/safe-stable-stringify-candidate-adapter.mjs';
let ready = false;
function ensureAdapter() {
  if (ready) return;
  try { writeFileSync(adapter, readFileSync(source), { flag: 'wx', mode: 0o555 }); }
  catch (error) { if (error?.code !== 'EEXIST') throw error; }
  chmodSync(adapter, 0o555); ready = true;
}
export function call(caseId) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  ensureAdapter();
  const id = `case-${caseId}`;
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
    'LC_ALL=C.UTF-8', `NODE_CANDIDATE_SITE=${site}`, '/usr/local/bin/node', '--no-addons', adapter],
    { cwd: site, input: JSON.stringify({ id, caseId }), encoding: 'utf8', maxBuffer: 256 * 1024 });
  if (result.error || !result.stdout) throw new Error(result.error?.message ?? result.stderr ?? `exit ${result.status}`);
  const response = JSON.parse(result.stdout);
  if (response.id !== id) throw new Error('candidate response id mismatch');
  return response;
}
