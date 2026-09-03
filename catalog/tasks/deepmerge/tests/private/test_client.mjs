import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {mkdirSync} from 'node:fs';
import {join} from 'node:path';

const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error('candidate site is not configured');
const adapter = join(import.meta.dirname, 'candidate_adapter.txt');

export function call(operation, args = {}) {
  mkdirSync(join(site, 'tmp'), {recursive: true});
  mkdirSync(join(site, 'home'), {recursive: true});
  const result = spawnSync(process.execPath, ['--no-addons', '-e', readFileSync(adapter, 'utf8')], {
    input: JSON.stringify({operation, args}) + '\n',
    encoding: 'utf8',
    timeout: 15000,
    maxBuffer: 256 * 1024,
    env: {
      PATH: '/usr/local/bin:/usr/bin:/bin',
      HOME: join(site, 'home'),
      TMPDIR: join(site, 'tmp'),
      NODE_CANDIDATE_SITE: site,
      LC_ALL: 'C.UTF-8',
    },
  });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(String(result.stderr || result.stdout));
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(response.message);
  return response.value;
}
