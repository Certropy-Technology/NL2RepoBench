import { spawnSync } from 'node:child_process';

const RUNNER = '/tests/runtime/node/candidate_runner.mjs';
const NODE = '/usr/local/bin/node';
const MAX_REQUEST_BYTES = 64 * 1024;

export function equal(left, right) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const request = JSON.stringify({
    package: 'fast-deep-equal',
    export: 'equal',
    args: [left, right],
  });
  if (Buffer.byteLength(request) > MAX_REQUEST_BYTES) {
    throw new Error('JSON request exceeds the boundary');
  }
  const result = spawnSync(
    '/usr/bin/timeout',
    [
      '--signal=TERM',
      '--kill-after=5s',
      '30s',
      'runuser',
      '-u',
      'candidate',
      '--',
      '/usr/bin/prlimit',
      '--cpu=60',
      '--nproc=32',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      'NODE_ALLOWED_PACKAGE=fast-deep-equal',
      NODE,
      '--no-addons',
      RUNNER,
    ],
    {
      cwd: site,
      input: `${request}\n`,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 35_000,
    },
  );
  if (result.error) throw result.error;
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error('candidate response was not JSON');
  }
  if (!response?.ok || typeof response.value !== 'boolean') {
    throw new Error(response?.message ?? response?.error ?? 'candidate-call-failed');
  }
  return response.value;
}
