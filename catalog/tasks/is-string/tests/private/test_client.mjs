import {chmodSync, existsSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';

const adapter = join(dirname(fileURLToPath(import.meta.url)), 'candidate_adapter.txt');
const runtimeAdapter = '/tmp/is-string-candidate-adapter.mjs';
let sequence = 0;

function ensureAdapter() {
  if (!existsSync(adapter)) throw new Error('candidate boundary is unavailable');
  if (!existsSync(runtimeAdapter)) {
    writeFileSync(runtimeAdapter, readFileSync(adapter), {flag: 'wx', mode: 0o555});
  }
  chmodSync(runtimeAdapter, 0o555);
}

export function request(operation, value) {
  const payload = operation === 'inventory'
    ? {operation}
    : {operation, value};
  const input = JSON.stringify(payload);
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is unavailable');
  ensureAdapter();
  const useUserBoundary = process.getuid?.() === 0 && existsSync('/usr/sbin/runuser');
  const command = useUserBoundary ? '/usr/sbin/runuser' : process.execPath;
  const args = useUserBoundary
    ? ['-u', 'candidate', '--', 'env', '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${join(site, 'home')}`,
      `TMPDIR=${join(site, 'tmp')}`,
      `NODE_CANDIDATE_SITE=${site}`,
      'NODE_ALLOWED_PACKAGE=is-string',
      'TERM=dumb', 'CI=true', 'LC_ALL=C.UTF-8',
      process.execPath, '--no-addons', runtimeAdapter]
    : [runtimeAdapter];
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', command, ...args,
  ], {
    cwd: site,
    input,
    encoding: 'utf8',
    env: {
      PATH: '/usr/local/bin:/usr/bin:/bin',
      HOME: join(site, 'home'),
      TMPDIR: join(site, 'tmp'),
      NODE_CANDIDATE_SITE: site,
      NODE_ALLOWED_PACKAGE: 'is-string',
      NODE_OPTIONS: undefined,
      NODE_PATH: undefined,
    },
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error || !result.stdout) {
    const detail = result.error?.message ?? result.stderr ?? `exit ${result.status}`;
    throw new Error(`candidate child failed: ${String(detail).slice(0, 256)}`);
  }
  const response = JSON.parse(result.stdout);
  if (result.status !== 0 || response.ok !== true) {
    throw new Error(response.message ?? 'candidate call failed');
  }
  return response.value;
}

export function inventory() {
  return request('inventory');
}

export function value(kind, extra = {}) {
  return request('call', {kind, ...extra});
}

export function nextId() {
  sequence += 1;
  return `request-${sequence}`;
}
