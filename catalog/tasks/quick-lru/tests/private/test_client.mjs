import {spawnSync} from 'node:child_process';

const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const input = JSON.parse(readFileSync(0, 'utf8'));
const site = process.env.NODE_CANDIDATE_SITE;
const moduleUrl = pathToFileURL(join(site, 'node_modules', 'quick-lru', 'index.js')).href;
const {default: QuickLRU} = await import(moduleUrl);
const realNow = Date.now;
let clock = 0;
Date.now = () => clock;
const refs = new Map();
const evictions = [];
const options = {...(input.options ?? {})};
if (options.callback) {
  delete options.callback;
  options.onEviction = (key, value) => evictions.push([key, value]);
}
if ((input.commands ?? []).some(command => command.op === 'metadata')) {
  const manifest = JSON.parse(readFileSync(join(site, 'node_modules', 'quick-lru', 'package.json'), 'utf8'));
  process.stdout.write(JSON.stringify({
    result: [{name: manifest.name, version: manifest.version, type: manifest.type, exports: manifest.exports}],
    evictions: [],
  }));
  process.exit(0);
}
const cache = new QuickLRU(options);
const resolve = value => value && typeof value === 'object' && Object.keys(value).length === 1 && '$ref' in value
  ? refs.get(value.$ref)
  : value;
const result = [];
for (const command of input.commands ?? []) {
  const key = resolve(command.key);
  const value = resolve(command.value);
  switch (command.op) {
    case 'bind': refs.set(command.name, value); result.push(true); break;
    case 'set': {
      const returned = Object.hasOwn(command, 'options')
        ? cache.set(key, value, command.options)
        : cache.set(key, value);
      result.push(returned === cache);
      break;
    }
    case 'get': result.push(cache.get(key)); break;
    case 'has': result.push(cache.has(key)); break;
    case 'peek': result.push(cache.peek(key)); break;
    case 'delete': result.push(cache.delete(key)); break;
    case 'clear': cache.clear(); result.push(true); break;
    case 'expiresIn': result.push(cache.expiresIn(key)); break;
    case 'resize': cache.resize(command.value); result.push(cache.maxSize); break;
    case 'evict': cache.evict(command.value); result.push(cache.size); break;
    case 'advance': clock += command.value; result.push(clock); break;
    case 'size': result.push(cache.size); break;
    case 'maxSize': result.push(cache.maxSize); break;
    case 'maxAge': result.push(cache.maxAge); break;
    case 'keys': result.push([...cache.keys()]); break;
    case 'values': result.push([...cache.values()]); break;
    case 'entries': result.push([...cache.entries()]); break;
    case 'ascending': result.push([...cache.entriesAscending()]); break;
    case 'descending': result.push([...cache.entriesDescending()]); break;
    case 'iterator': result.push([...cache]); break;
    case 'forEach': {
      const rows = [];
      const thisArg = command.thisArg ?? null;
      cache.forEach(function (item, itemKey, owner) {
        rows.push([item, itemKey, owner === cache, this?.name ?? null]);
      }, thisArg);
      result.push(rows);
      break;
    }
    case 'toString': result.push(cache.toString()); break;
    case 'tag': result.push(cache[Symbol.toStringTag]); break;
    default: throw new Error('unknown adapter operation');
  }
}
Date.now = realNow;
const replacer = (_key, item) => item === undefined ? '__undefined__'
  : item === Infinity ? '__infinity__'
  : item === -Infinity ? '__negative_infinity__'
  : Number.isNaN(item) ? '__nan__'
  : item;
process.stdout.write(JSON.stringify({result, evictions}, replacer));
`;

function decode(value) {
  if (Array.isArray(value)) return value.map(decode);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, decode(item)]));
  if (value === '__undefined__') return undefined;
  if (value === '__infinity__') return Infinity;
  if (value === '__negative_infinity__') return -Infinity;
  if (value === '__nan__') return NaN;
  return value;
}

export function scenario(commands, options) {
  const site = process.env.NODE_CANDIDATE_SITE;
  const run = spawnSync('/usr/sbin/runuser', [
    '-u', 'candidate', '--', process.execPath, '--no-addons', '--input-type=module', '--eval', ADAPTER,
  ], {
    cwd: site,
    env: {PATH: '/usr/local/bin:/usr/bin:/bin', NODE_CANDIDATE_SITE: site},
    input: JSON.stringify({commands, options}),
    encoding: 'utf8',
    timeout: 30_000,
    maxBuffer: 256 * 1024,
  });
  if (run.error || run.status !== 0) {
    throw new Error(`candidate adapter failed: ${run.error?.message ?? run.stderr ?? run.status}`);
  }
  return decode(JSON.parse(run.stdout));
}
