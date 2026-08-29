import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {join} from 'node:path';

const candidateSite = process.env.NODE_CANDIDATE_SITE;
if (!candidateSite) throw new Error('NODE_CANDIDATE_SITE is required');

const childScript = `
const {createRequire} = require('node:module');
const {pathToFileURL} = require('node:url');
const {join} = require('node:path');
const payload = JSON.parse(process.argv[1]);
try {
  const request = createRequire(pathToFileURL(join(payload.site, 'package.json')));
  const moduleValue = request('string.prototype.trim');
  let value;
  if (payload.mode === 'root') {
    value = moduleValue(...payload.args);
  } else if (payload.mode === 'api') {
    value = {
      rootType: typeof moduleValue,
      rootName: moduleValue.name,
      rootLength: moduleValue.length,
      implementationType: typeof moduleValue.implementation,
      polyfillType: typeof moduleValue.getPolyfill,
      shimType: typeof moduleValue.shim,
      implementationEnumerable: Object.prototype.propertyIsEnumerable.call(moduleValue, 'implementation'),
      polyfillEnumerable: Object.prototype.propertyIsEnumerable.call(moduleValue, 'getPolyfill'),
      shimEnumerable: Object.prototype.propertyIsEnumerable.call(moduleValue, 'shim'),
    };
  } else if (payload.mode === 'shim') {
    const result = moduleValue.shim();
    value = {resultType: typeof result, installedType: typeof String.prototype.trim};
  } else {
    throw new Error('unknown test mode');
  }
  process.stdout.write(JSON.stringify({ok: true, value}) + '\\n');
} catch (error) {
  process.stdout.write(JSON.stringify({ok: false, exceptionType: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error)}) + '\\n');
  process.exitCode = 1;
}
`;

function invoke(mode, args = []) {
  const payload = JSON.stringify({site: candidateSite, mode, args});
  const result = spawnSync(
    process.execPath,
    ['--no-addons', '-e', childScript, payload],
    {
      cwd: candidateSite,
      env: {PATH: '/usr/local/bin:/usr/bin:/bin', HOME: join(candidateSite, '.home'), TMPDIR: join(candidateSite, '.tmp')},
      encoding: 'utf8',
      timeout: 30_000,
      maxBuffer: 256 * 1024,
    },
  );
  if (result.error) return {ok: false, exceptionType: result.error.name, message: result.error.message};
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {ok: false, exceptionType: 'ProtocolError', message: 'candidate response was not JSON'};
  }
}

export function trim(...args) {
  return invoke('root', args);
}

export function api() {
  return invoke('api');
}

export function shim() {
  return invoke('shim');
}
