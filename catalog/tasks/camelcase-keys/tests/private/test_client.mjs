import {spawnSync} from 'node:child_process';

const RUNNER = '/tests/runtime/node/candidate_runner.mjs';
const NODE = '/usr/local/bin/node';
const PACKAGE = 'camelcase-keys';

export function callCandidate(input, options) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    `NODE_ALLOWED_PACKAGE=${PACKAGE}`, NODE, '--no-addons', RUNNER,
  ], {
    cwd: site,
    input: `${JSON.stringify({
      package: PACKAGE,
      export: 'default',
      args: options === undefined ? [input] : [input, options],
    })}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(response.error ?? 'candidate-call-failed');
  return response.value;
}

export function inventory() {
  const site = process.env.NODE_CANDIDATE_SITE;
  const script = `
    const fs = await import('node:fs');
    const manifest = JSON.parse(fs.readFileSync('${site}/node_modules/${PACKAGE}/package.json'));
    const module = await import('${PACKAGE}');
    process.stdout.write(JSON.stringify({
      packageName: manifest.name,
      packageVersion: manifest.version,
      moduleType: manifest.type,
      exportMap: manifest.exports,
      exportNames: Object.keys(module).sort(),
      callableDefault: typeof module.default === 'function',
    }));
  `;
  const result = spawnSync(NODE, ['--no-addons', '--input-type=module', '-e', script], {
    cwd: site,
    env: {PATH: '/usr/local/bin:/usr/bin:/bin', NODE_PATH: ''},
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
  });
  if (result.status !== 0) throw new Error(result.stderr || 'inventory failed');
  return JSON.parse(result.stdout);
}
