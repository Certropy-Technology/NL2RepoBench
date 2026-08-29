import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';

const require = createRequire('file:///tests/private/test_client.mjs');

function emit(payload, code = 0) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(code);
}

function requestFromEnvironment() {
  const raw = process.env.RANGE_PARSER_REQUEST_JSON;
  if (!raw || Buffer.byteLength(raw) > 64 * 1024) throw new Error('request is missing or too large');
  const request = JSON.parse(raw);
  if (!request || typeof request !== 'object' || Array.isArray(request)) throw new Error('request is invalid');
  return request;
}

function invoke(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('NODE_CANDIDATE_SITE is missing');
  const packageRoot = join(site, 'node_modules', 'range-parser');
  const manifest = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
  if (request.operation === 'package-shape' && manifest.range_parser_control === 'hang') {
    throw new Error('package shape control rejected');
  }
  const parser = require(join(packageRoot, manifest.main || 'index.js'));
  if (request.operation === 'package-shape') {
    return {name: manifest.name, version: manifest.version, main: manifest.main || 'index.js', callable: typeof parser};
  }
  const args = request.args;
  if (!Array.isArray(args) || args.length < 2 || args.length > 3) throw new Error('arguments are invalid');
  const result = parser(...args);
  return Array.isArray(result) ? {ranges: [...result], type: result.type} : result;
}

export function callCandidate(...args) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const source = readFileSync(fileURLToPath(import.meta.url), 'utf8');
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=1s', '2s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`,
    `RANGE_PARSER_REQUEST_JSON=${JSON.stringify({args})}`,
    process.execPath, '--no-addons', '--input-type=module', '--eval', `import(${JSON.stringify(moduleUrl)})`,
  ], {cwd: site, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 5_000});
  if (result.error) return {ok: false, error: `candidate process failed: ${result.error.message}`};
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {ok: false, error: `candidate response malformed: ${result.stderr ?? result.stdout}`};
  }
}

export function packageShape() {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const source = readFileSync(fileURLToPath(import.meta.url), 'utf8');
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=1s', '2s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`,
    `RANGE_PARSER_REQUEST_JSON=${JSON.stringify({operation: 'package-shape'})}`,
    process.execPath, '--no-addons', '--input-type=module', '--eval', `import(${JSON.stringify(moduleUrl)})`,
  ], {cwd: site, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 5_000});
  if (result.error) return {ok: false, error: `candidate process failed: ${result.error.message}`};
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {ok: false, error: `candidate response malformed: ${result.stderr ?? result.stdout}`};
  }
}

if (process.env.RANGE_PARSER_REQUEST_JSON) {
  try {
    const request = requestFromEnvironment();
    emit({ok: true, value: invoke(request)});
  } catch (error) {
    emit({ok: false, error: `${error?.name ?? 'Error'}: ${error?.message ?? error}`}, 1);
  }
}
