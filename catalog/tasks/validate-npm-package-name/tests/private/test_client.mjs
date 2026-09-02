import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const PACKAGE_NAME = 'validate-npm-package-name';

const CHILD_ADAPTER = String.raw`
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');

function emit(payload, code = 0) {
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded) > 262144) process.exit(70);
  process.stdout.write(encoded + '\n');
  process.exit(code);
}

try {
  const raw = fs.readFileSync(0);
  if (raw.byteLength > 65536) emit({ok: false, error: 'request-too-large'}, 64);
  const request = JSON.parse(raw.toString('utf8'));
  const packageName = process.env.NODE_ALLOWED_PACKAGE;
  const requireFromSite = createRequire(path.join(process.cwd(), 'package.json'));
  const validate = requireFromSite(packageName);
  if (typeof validate !== 'function') emit({ok: false, error: 'module-export-is-not-callable'}, 65);

  if (request.operation === 'metadata') {
    const manifestPath = path.join(process.cwd(), 'node_modules', packageName, 'package.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    emit({ok: true, value: {name: manifest.name, version: manifest.version, callable: true}});
  }

  let input;
  switch (request.inputType) {
    case 'json': input = request.value; break;
    case 'undefined': input = undefined; break;
    case 'nan': input = Number.NaN; break;
    case 'infinity': input = Number.POSITIVE_INFINITY; break;
    case 'negative-infinity': input = Number.NEGATIVE_INFINITY; break;
    case 'bigint': input = 1n; break;
    case 'symbol': input = Symbol('package'); break;
    case 'function': input = function inputFunction() {}; break;
    default: emit({ok: false, error: 'input-type-not-allowlisted'}, 64);
  }
  const result = validate(input);
  if (result && typeof result.then === 'function') {
    emit({ok: false, error: 'result-must-be-synchronous'}, 65);
  }
  emit({ok: true, value: result});
} catch (error) {
  emit({
    ok: false,
    error: 'candidate-call-failed',
    exception_type: error && error.constructor ? error.constructor.name : 'Error',
    message: String(error && error.message ? error.message : error),
  }, 1);
}
`;

function request(payload) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=1s', '2s',
    'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=2', '--nproc=32', '--nofile=128', '--',
    'env', '-i',
    'PATH=/usr/local/bin:/usr/bin:/bin',
    `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`,
    `NODE_ALLOWED_PACKAGE=${PACKAGE_NAME}`,
    NODE, '--no-addons', '-e', CHILD_ADAPTER,
  ], {
    cwd: site,
    input: `${JSON.stringify(payload)}\n`,
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 4_000,
  });
  if (result.error) throw result.error;
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {
      ok: false,
      error: 'candidate-process-failed',
      status: result.status,
      stderr: String(result.stderr || '').slice(0, 1024),
    };
  }
}

export function inspectPackage() {
  return request({operation: 'metadata'});
}

export function callCandidate(value) {
  return request({operation: 'call', inputType: 'json', value});
}

export function callSpecial(inputType) {
  return request({operation: 'call', inputType});
}
