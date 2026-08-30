import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const node = process.execPath;
const adapter = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const site = process.env.NODE_CANDIDATE_SITE;
const request = JSON.parse(readFileSync(0, 'utf8'));
const root = join(site, 'node_modules', 'string-width');
const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const entry = manifest.exports?.default ?? manifest.main;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) throw new Error('unsafe entry');
const module = await import(pathToFileURL(join(root, entry)).href);
if (typeof module.default !== 'function') throw new Error('default export is not callable');
function decode(value) {
  return value && typeof value === 'object' && value.type === 'undefined' ? undefined : value;
}
try {
  const value = module.default(decode(request.input), request.options ?? {});
  process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, name: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error)}) + '\n');
  process.exitCode = 1;
}
`;

export function call(input, options = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', `NODE_CANDIDATE_SITE=${site}`, 'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`, `TMPDIR=${site}/tmp`, 'LC_ALL=C.UTF-8', node,
    '--no-addons', '--input-type=module', '--eval', adapter,
  ], {
    cwd: site,
    input: JSON.stringify({input, options}),
    encoding: 'utf8',
    timeout: 35_000,
    maxBuffer: 256 * 1024,
  });
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1);
  if (!line) throw new Error(result.error?.message ?? 'candidate produced no response');
  const payload = JSON.parse(line);
  if (!payload.ok) throw new Error(payload.message ?? 'candidate call failed');
  return payload.value;
}

export function packageInventory() {
  const site = process.env.NODE_CANDIDATE_SITE;
  const root = join(site, 'node_modules', 'string-width');
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  return {
    name: manifest.name,
    version: manifest.version,
    type: manifest.type,
    exports: manifest.exports,
    dependencies: manifest.dependencies,
    files: ['index.js', 'index.d.ts'].map(file => readFileSync(join(root, file), 'utf8').length > 0),
  };
}
