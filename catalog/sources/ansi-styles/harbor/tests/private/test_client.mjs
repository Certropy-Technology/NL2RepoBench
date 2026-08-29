import {spawnSync} from 'node:child_process';

const NODE = process.execPath;
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error('candidate site is not configured');
const root = join(site, 'node_modules', 'ansi-styles');
const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const entry = typeof packageJson.exports === 'string'
  ? packageJson.exports
  : packageJson.exports?.['.'] ?? packageJson.module ?? packageJson.main;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
  throw new Error('ansi-styles package has no safe ESM entry');
}
const api = await import(pathToFileURL(join(root, entry)).href);
const styles = api.default;

function fail(message) {
  process.stdout.write(JSON.stringify({ok: false, message: String(message).slice(0, 2048)}) + '\n');
  process.exit(1);
}

function inventory() {
  const rootExport = packageJson.exports;
  return {
    packageName: packageJson.name,
    packageVersion: packageJson.version,
    type: packageJson.type,
    packageExport: rootExport,
    hasDeclaration: readFileSync(join(root, 'index.d.ts'), 'utf8').length > 0,
    modifiers: api.modifierNames,
    foreground: api.foregroundColorNames,
    background: api.backgroundColorNames,
    underline: api.underlineColorNames,
    colors: api.colorNames,
    aliases: {
      modifier: api.modifiers === undefined ? false : api.modifiers === api.modifierNames,
      foreground: api.foregroundColors === undefined ? false : api.foregroundColors === api.foregroundColorNames,
      background: api.backgroundColors === undefined ? false : api.backgroundColors === api.backgroundColorNames,
      colors: api.colors === undefined ? false : api.colors === api.colorNames,
    },
    enumerableKeys: Object.keys(styles),
    groupEnumerable: {
      modifier: Object.prototype.propertyIsEnumerable.call(styles, 'modifier'),
      color: Object.prototype.propertyIsEnumerable.call(styles, 'color'),
      bgColor: Object.prototype.propertyIsEnumerable.call(styles, 'bgColor'),
      underlineColor: Object.prototype.propertyIsEnumerable.call(styles, 'underlineColor'),
      codes: Object.prototype.propertyIsEnumerable.call(styles, 'codes'),
    },
    codeEntries: [...styles.codes.entries()],
  };
}

function style(name) {
  const value = styles[name];
  if (!value || typeof value !== 'object') throw new Error('unknown style: ' + name);
  return {open: value.open, close: value.close};
}

function group(name) {
  const value = styles[name];
  if (!value || typeof value !== 'object') throw new Error('unknown group: ' + name);
  return {close: value.close, names: Object.keys(value)};
}

function convert(name, args) {
  if (name === 'group-ansi') return styles.color.ansi(args[0]);
  if (name === 'group-ansi256') return styles.color.ansi256(args[0]);
  if (name === 'group-ansi16m') return styles.color.ansi16m(...args);
  if (name === 'bg-ansi') return styles.bgColor.ansi(args[0]);
  if (name === 'bg-ansi256') return styles.bgColor.ansi256(args[0]);
  if (name === 'bg-ansi16m') return styles.bgColor.ansi16m(...args);
  if (name === 'underline-ansi') return styles.underlineColor.ansi(args[0]);
  if (name === 'underline-ansi256') return styles.underlineColor.ansi256(args[0]);
  if (name === 'underline-ansi16m') return styles.underlineColor.ansi16m(...args);
  if (typeof styles[name] !== 'function') throw new Error('unknown conversion: ' + name);
  return styles[name](...args);
}

const request = JSON.parse(readFileSync(0, 'utf8'));
let value;
if (request.operation === 'inventory') value = inventory();
else if (request.operation === 'style') value = style(request.name);
else if (request.operation === 'group') value = group(request.name);
else if (request.operation === 'convert') value = convert(request.name, request.args ?? []);
  else throw new Error('operation is not allowlisted');
process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
`;

function call(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
    'env', '-i', `NODE_CANDIDATE_SITE=${site}`, 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, 'TERM=dumb', 'CI=true', 'FORCE_COLOR=0', 'LC_ALL=C.UTF-8',
    NODE, '--no-addons', '--input-type=module', '--eval', ADAPTER,
  ], {
    cwd: site,
    input: JSON.stringify({operation, ...payload}),
    encoding: 'utf8',
    maxBuffer: 256 * 1024,
    timeout: 35_000,
  });
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
  if (!response?.ok) throw new Error(response?.message ?? 'candidate call failed');
  return response.value;
}

export const inventory = () => call('inventory');
export const style = name => call('style', {name});
export const group = name => call('group', {name});
export const convert = (name, args) => call('convert', {name, args});
