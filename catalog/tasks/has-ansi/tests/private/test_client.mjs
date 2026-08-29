import {spawnSync} from 'node:child_process';
import {join} from 'node:path';

const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error('NODE_CANDIDATE_SITE is required');

const childProgram = `
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
const request = JSON.parse(readFileSync(0, 'utf8'));
try {
  const packageRoot = join(process.env.NODE_CANDIDATE_SITE, 'node_modules', 'has-ansi');
  const packageJson = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
  const module = await import('has-ansi');
  let result;
  if (request.operation === 'check') {
    result = module.default(request.value);
  } else if (request.operation === 'metadata') {
    result = {
      name: packageJson.name,
      version: packageJson.version,
      type: packageJson.type,
      exports: packageJson.exports,
      defaultType: typeof module.default,
      declaration: readFileSync(join(packageRoot, 'index.d.ts'), 'utf8'),
    };
  } else {
    throw new Error('unknown operation');
  }
  process.stdout.write(JSON.stringify({id: request.id, result}) + '\\n');
} catch (error) {
  process.stdout.write(JSON.stringify({
    id: request.id,
    error: {type: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error).slice(0, 512)},
  }) + '\\n');
}
`;

export function query(operation, value) {
  const id = `request-${Date.now()}-${Math.random()}`;
  const result = spawnSync(
    process.execPath,
    ['--no-addons', '--input-type=module', '--eval', childProgram],
    {
      cwd: site,
      env: {
        PATH: '/usr/local/bin:/usr/bin:/bin',
        HOME: join(site, 'home'),
        NODE_CANDIDATE_SITE: site,
        NODE_OPTIONS: undefined,
        NODE_PATH: undefined,
      },
      input: JSON.stringify({id, operation, value}) + '\n',
      encoding: 'utf8',
      timeout: 5000,
      maxBuffer: 1024 * 1024,
    },
  );
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`candidate child exited ${result.status}: ${result.stderr}`);
  const lines = result.stdout.trim().split(/\r?\n/);
  if (lines.length !== 1) throw new Error(`candidate child emitted ${lines.length} lines`);
  const response = JSON.parse(lines[0]);
  if (response.id !== id) throw new Error('candidate response id mismatch');
  return response;
}
