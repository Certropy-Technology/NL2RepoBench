import {chmodSync, copyFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const ADAPTER = '/tmp/ip-address-candidate-adapter.mjs';
copyFileSync(new URL('./candidate_adapter.txt', import.meta.url), ADAPTER);
chmodSync(ADAPTER, 0o555);

function invoke(payload) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded) > 64 * 1024) throw new Error('request exceeds bound');
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--', 'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'LC_ALL=C.UTF-8', '/usr/local/bin/node', '--no-addons', ADAPTER], {cwd: site, input: `${encoded}\n`, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  try { return JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
}

export function call(spec) {
  const response = invoke({operation: 'call', spec});
  if (!response.ok) throw new Error(response.error?.message ?? 'candidate call failed');
  return response.value;
}

export function failure(spec) {
  return invoke({operation: 'call', spec});
}

export function inventory() {
  return invoke({operation: 'inventory'});
}
