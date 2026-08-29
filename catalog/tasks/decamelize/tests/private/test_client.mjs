import {spawnSync} from 'node:child_process';

const runner = '/tests/runtime/node/candidate_runner.mjs';
const node = '/usr/local/bin/node';

export function callCandidate(args) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--',
    'env', '-i', `PATH=/usr/local/bin:/usr/bin:/bin`, `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'NODE_ALLOWED_PACKAGE=decamelize', node, '--no-addons', runner,
  ], {
    cwd: site,
    input: `${JSON.stringify({package: 'decamelize', export: 'default', args})}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 30_000,
  });
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (!payload.ok) {
    const error = new Error(payload.message ?? payload.error ?? 'candidate-call-failed');
    error.code = payload.error;
    throw error;
  }
  return payload.value;
}
