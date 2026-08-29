import {chmodSync, copyFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const SOURCE_ADAPTER = '/tests/private/candidate_adapter.source';
const ADAPTER = `/tmp/nl2repobench-p-timeout-adapter-${process.pid}.mjs`;

copyFileSync(SOURCE_ADAPTER, ADAPTER);
chmodSync(ADAPTER, 0o555);

export function callScenario(scenario, parameters = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) {
    throw new Error('candidate site is not configured');
  }

  const request = JSON.stringify({scenario, parameters});
  if (Buffer.byteLength(request) > 64 * 1024) {
    throw new Error('candidate request exceeds the bound');
  }

  const result = spawnSync(
    '/usr/bin/timeout',
    [
      '--signal=TERM',
      '--kill-after=1s',
      '2s',
      'runuser',
      '-u',
      'candidate',
      '--',
      '/usr/bin/prlimit',
      '--cpu=4',
      '--nproc=32',
      '--nofile=128',
      '--',
      'env',
      '-i',
      'PATH=/usr/local/bin:/usr/bin:/bin',
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      'NODE_ALLOWED_PACKAGE=p-timeout',
      NODE,
      '--no-addons',
      ADAPTER,
    ],
    {
      cwd: site,
      input: `${request}\n`,
      encoding: 'utf8',
      maxBuffer: 256 * 1024,
      timeout: 2500,
    },
  );

  if (result.error) {
    throw result.error;
  }

  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }

  if (result.status !== 0 || payload?.ok !== true) {
    throw new Error(payload?.error ?? `candidate-call-failed (${result.status})`);
  }

  return payload.value;
}
