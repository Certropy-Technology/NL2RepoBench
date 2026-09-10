import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const node = '/usr/local/bin/node';
const adapter = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const site = process.env.NODE_CANDIDATE_SITE;
const root = join(site, 'node_modules', 'wrap-ansi');
const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const entry = packageJson.exports?.default ?? packageJson.module ?? packageJson.main;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) throw new Error('unsafe package entry');
const api = (await import(pathToFileURL(join(root, entry)).href)).default;
const request = JSON.parse(readFileSync(0, 'utf8'));
if (request.operation === 'wrap') {
  process.stdout.write(JSON.stringify({ok: true, value: api(request.string, request.columns, request.options)}));
} else if (request.operation === 'shape') {
  process.stdout.write(JSON.stringify({ok: true, value: {
    name: packageJson.name,
    version: packageJson.version,
    type: packageJson.type,
    exports: packageJson.exports,
    declaration: readFileSync(join(root, 'index.d.ts'), 'utf8').length > 0,
    functionName: api.name,
    functionLength: api.length,
  }}));
} else throw new Error('operation is not allowlisted');
`;

function call(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', `NODE_CANDIDATE_SITE=${site}`, 'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'LC_ALL=C.UTF-8',
    node, '--no-addons', '--input-type=module', '--eval', adapter,
  ], {cwd: site, input: JSON.stringify({operation, ...payload}), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
  if (!response.ok) throw new Error(response.message ?? 'candidate call failed');
  return response.value;
}

export const wrap = (string, columns, options) => call('wrap', {string, columns, options});
export const shape = () => call('shape');
