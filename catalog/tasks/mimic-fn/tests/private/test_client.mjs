import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const adapter = import.meta.url.startsWith('data:') ? null : fileURLToPath(import.meta.url);
const site = process.env.NODE_CANDIDATE_SITE;
const childOperation = process.env.MIMIC_FUNCTION_OPERATION;

function emit(payload, code = 0) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(code);
}

async function loadCandidate() {
  if (!site) throw new Error('NODE_CANDIDATE_SITE is missing');
  const root = join(site, 'node_modules', 'mimic-function');
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const exportMap = manifest.exports?.['.'] ?? manifest.exports;
  const entry = typeof exportMap === 'string' ? exportMap : exportMap?.default;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('package has no safe root export');
  }
  return {root, manifest, module: await import(pathToFileURL(join(root, entry)).href)};
}

function mimicFixture(mimicFunction) {
  const source = function source(first, second) { return first + second; };
  const destination = function wrapper() { return 'destination-body'; };
  return {source, destination, apply: options => mimicFunction(destination, source, options)};
}

function configurableScenario(mimicFunction, options = {}) {
  const destination = function destination() {};
  Object.defineProperty(destination, 'conflict', {
    value: true,
    configurable: false,
    writable: true,
    enumerable: true,
    ...options.destination,
  });
  const source = function source() {};
  Object.defineProperty(source, 'conflict', {
    value: true,
    configurable: false,
    writable: true,
    enumerable: true,
    ...options.source,
  });
  try {
    mimicFunction(destination, source, options.callOptions);
    return {threw: false, value: destination.conflict};
  } catch (error) {
    return {threw: true, name: error?.name};
  }
}

async function invoke(operation) {
  const {root, manifest, module: candidate} = await loadCandidate();
  const mimicFunction = candidate.default;
  const operations = {
    package: () => ({
      name: manifest.name,
      version: manifest.version,
      type: manifest.type,
      default: typeof mimicFunction,
      hasTypes: (manifest.exports?.['.'] ?? manifest.exports)?.types === './index.d.ts'
        && readFileSync(join(root, 'index.d.ts'), 'utf8').length > 0,
    }),
    'return-value': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      return apply() === destination;
    },
    'copy-name': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      const before = destination.name;
      apply();
      return {before, after: destination.name};
    },
    'copy-property': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      source.custom = 'unicorn';
      apply();
      return destination.custom;
    },
    'copy-symbol': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      const symbol = Symbol('marker');
      source[symbol] = 'sparkles';
      apply();
      return destination[symbol];
    },
    'keep-length': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      apply();
      return {source: source.length, destination: destination.length};
    },
    descriptors: () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      Object.defineProperty(source, 'hidden', {value: 42, writable: false, enumerable: false, configurable: false});
      apply();
      const descriptor = Object.getOwnPropertyDescriptor(destination, 'hidden');
      return descriptor.value === 42 && descriptor.writable === false
        && descriptor.enumerable === false && descriptor.configurable === false;
    },
    inherited: () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      const parent = function parent() {};
      parent.inherited = true;
      Object.setPrototypeOf(source, parent);
      apply();
      return destination.inherited;
    },
    'extra-property': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      destination.extra = true;
      apply();
      return destination.extra;
    },
    'keep-prototype': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      const original = destination.prototype;
      apply();
      return destination.prototype === original;
    },
    classes: () => {
      class DestinationClass {}
      class SourceClass {}
      const sourcePrototype = SourceClass.prototype;
      mimicFunction(DestinationClass, SourceClass);
      return {name: DestinationClass.name, distinctPrototype: DestinationClass.prototype !== sourcePrototype};
    },
    'to-string': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      const expected = `/* Wrapped with wrapper() */\n${source.toString()}`;
      apply();
      return destination.toString() === expected;
    },
    'to-string-arrow': () => {
      const destination = function wrapper() {};
      const source = value => value;
      const expected = `/* Wrapped with wrapper() */\n${source.toString()}`;
      mimicFunction(destination, source);
      return destination.toString() === expected;
    },
    'to-string-bound': () => {
      const destination = function wrapper() {};
      const source = (() => {}).bind(null);
      const expected = `/* Wrapped with wrapper() */\n${source.toString()}`;
      mimicFunction(destination, source);
      return destination.toString() === expected;
    },
    'to-string-constructor': () => {
      const destination = function wrapper() {};
      const source = new Function('');
      const expected = `/* Wrapped with wrapper() */\n${source.toString()}`;
      mimicFunction(destination, source);
      return destination.toString() === expected;
    },
    'to-string-repeated': () => {
      const source = function source() {};
      const first = function first() {};
      const second = function second() {};
      mimicFunction(first, source);
      mimicFunction(second, first);
      return second.toString() === `/* Wrapped with second() */\n/* Wrapped with first() */\n${source.toString()}`;
    },
    'to-string-enumerable': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      apply();
      return Object.getOwnPropertyDescriptor(destination, 'toString').enumerable;
    },
    'native-to-string': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      const nativeString = Function.prototype.toString.call(destination);
      apply();
      return Function.prototype.toString.call(destination) === nativeString;
    },
    'string-coercion': () => {
      const {source, destination, apply} = mimicFixture(mimicFunction);
      const expected = `/* Wrapped with wrapper() */\n${source.toString()}`;
      apply();
      return String(destination) === expected;
    },
    'to-string-name': () => {
      const {destination, apply} = mimicFixture(mimicFunction);
      apply();
      return destination.toString.name;
    },
    'patched-source-to-string': () => {
      const source = function source() {};
      source.toString = () => 'custom source body';
      const destination = function wrapper() {};
      mimicFunction(destination, source);
      return destination.toString() === '/* Wrapped with wrapper() */\ncustom source body';
    },
    'nonconfig-same': () => configurableScenario(mimicFunction).threw === false,
    'nonconfig-writable-value': () => configurableScenario(mimicFunction, {source: {value: false}}),
    'nonconfig-value-throw': () => configurableScenario(mimicFunction, {destination: {writable: false}, source: {value: false, writable: false}}).threw,
    'nonconfig-value-ignore': () => configurableScenario(mimicFunction, {destination: {writable: false}, source: {value: false, writable: false}, callOptions: {ignoreNonConfigurable: true}}),
    'nonconfig-configurable-throw': () => configurableScenario(mimicFunction, {source: {configurable: true}}).threw,
    'nonconfig-configurable-ignore': () => configurableScenario(mimicFunction, {source: {configurable: true}, callOptions: {ignoreNonConfigurable: true}}).threw === false,
    'nonconfig-writable-throw': () => configurableScenario(mimicFunction, {destination: {writable: false}, source: {writable: true}}).threw,
    'nonconfig-writable-ignore': () => configurableScenario(mimicFunction, {destination: {writable: false}, source: {writable: true}, callOptions: {ignoreNonConfigurable: true}}).threw === false,
    'nonconfig-enumerable-throw': () => configurableScenario(mimicFunction, {source: {enumerable: false}}).threw,
    'nonconfig-enumerable-ignore': () => configurableScenario(mimicFunction, {source: {enumerable: false}, callOptions: {ignoreNonConfigurable: true}}).threw === false,
    'nonconfig-default-throw': () => configurableScenario(mimicFunction, {source: {enumerable: false}, callOptions: {ignoreNonConfigurable: undefined}}).threw,
  };
  if (!operations[operation]) throw new Error(`unknown operation: ${operation}`);
  return await operations[operation]();
}

export function callCandidate(operation) {
  if (!site) throw new Error('candidate site is not configured');
  if (!adapter) throw new Error('adapter path is unavailable');
  const source = readFileSync(adapter, 'utf8');
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '15s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=30', '--nproc=4096', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `NODE_CANDIDATE_SITE=${site}`,
    `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `MIMIC_FUNCTION_OPERATION=${operation}`,
    process.execPath, '--no-addons', '--input-type=module', '--eval', `import(${JSON.stringify(moduleUrl)})`,
  ], {cwd: site, encoding: 'utf8', maxBuffer: 262144});
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1) ?? '';
  let payload;
  try {
    payload = JSON.parse(line);
  } catch {
    throw new Error(`candidate response malformed: ${result.stderr ?? result.stdout}`);
  }
  if (result.status !== 0 || payload.ok !== true) {
    throw new Error(payload.fatal ?? `candidate call failed with status ${result.status}`);
  }
  return payload.value;
}

if (childOperation) {
  try {
    emit({ok: true, value: await invoke(childOperation)});
  } catch (error) {
    emit({ok: false, fatal: `${error?.name ?? 'Error'}: ${error?.message ?? error}`}, 1);
  }
}
