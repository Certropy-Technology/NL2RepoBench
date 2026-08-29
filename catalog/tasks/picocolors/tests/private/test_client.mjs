import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import vm from 'node:vm';

const request = JSON.parse(readFileSync(0, 'utf8'));
const site = process.cwd();
const root = join(site, 'node_modules', 'picocolors');
const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const require = createRequire(join(root, 'package.json'));
const pc = require('picocolors');

function style(name, args) {
  const value = pc.createColors(true);
  const method = value[name];
  if (typeof method !== 'function' || !Array.isArray(args) || args.length > 0) {
    throw new Error('style is not allowlisted');
  }
  return method;
}

function format(payload) {
  if (!Number.isInteger(payload.enabled) || !Array.isArray(payload.steps) || !Array.isArray(payload.values)) {
    throw new Error('format payload is malformed');
  }
  const colors = pc.createColors(payload.enabled !== 0);
  let value = payload.values.length === 0 ? undefined : payload.values[0];
  for (const step of [...payload.steps].reverse()) {
    if (!step || typeof step.name !== 'string' || !Array.isArray(step.args)) throw new Error('style step is malformed');
    if (step.args.length !== 0) throw new Error('style arguments are not allowed');
    const formatter = colors[step.name];
    if (typeof formatter !== 'function') throw new Error('style name is not allowlisted');
    value = formatter(value);
  }
  return String(value);
}

function isolatedSupport(payload) {
  const source = readFileSync(join(root, 'picocolors.js'), 'utf8');
  const env = Object.assign({}, payload.env);
  const fakeProcess = {
    env,
    argv: Array.isArray(payload.argv) ? payload.argv : [],
    platform: payload.platform ?? 'linux',
    stdout: {isTTY: Boolean(payload.stdoutTTY)},
  };
  const context = vm.createContext({process: fakeProcess, module: {exports: {}}, require: undefined});
  new vm.Script(source).runInContext(context);
  return context.module.exports.isColorSupported;
}

function inventory() {
  const browser = require(join(root, 'picocolors.browser.js'));
  return {
    name: manifest.name,
    version: manifest.version,
    main: manifest.main,
    browser: manifest.browser,
    files: manifest.files,
    keys: Object.keys(pc),
    support: pc.isColorSupported,
    factoryFalse: pc.createColors(false).isColorSupported,
    factoryTrue: pc.createColors(true).isColorSupported,
    browserSupport: browser.isColorSupported,
    browserRed: browser.red('x'),
    browserKeys: Object.keys(browser),
  };
}

let value;
if (request.operation === 'format') value = format(request.payload);
else if (request.operation === 'inventory') value = inventory();
else if (request.operation === 'support') value = isolatedSupport(request.payload);
else throw new Error('operation is not allowlisted');
process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
`;

export function call(operation, payload) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    NODE, '--no-addons', '--input-type=module', '--eval', ADAPTER,
  ], {cwd: site, input: JSON.stringify({operation, payload}), encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(response.message ?? 'candidate call failed');
  return response.value;
}

export const format = payload => call('format', payload);
export const inventory = () => call('inventory', {});
export const support = payload => call('support', payload);
