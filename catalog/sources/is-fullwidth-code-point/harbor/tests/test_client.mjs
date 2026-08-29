import {spawnSync} from 'node:child_process';

const RUNNER = '/tests/runtime/node/candidate_runner.mjs';
const NODE = '/usr/local/bin/node';

export function callCandidate(value) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'NODE_ALLOWED_PACKAGE=is-fullwidth-code-point',
    NODE, '--no-addons', RUNNER,
  ], {
    cwd: site,
    input: `${JSON.stringify({package: 'is-fullwidth-code-point', export: 'default', args: [value]})}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error) throw result.error;
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
}
