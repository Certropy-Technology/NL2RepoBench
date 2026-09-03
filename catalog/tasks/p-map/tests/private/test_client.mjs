import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';

const adapter = import.meta.url.startsWith('data:') ? null : fileURLToPath(import.meta.url);
const site = process.env.NODE_CANDIDATE_SITE;
const childOperation = process.env.P_MAP_OPERATION;

function emit(payload, code = 0) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exit(code);
}

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolve_, reject_) => {
    resolve = resolve_;
    reject = reject_;
  });
  return {promise, resolve, reject};
}

async function turns(count = 2) {
  for (let index = 0; index < count; index++) {
    await new Promise(resolve => setImmediate(resolve));
  }
}

async function loadCandidate() {
  if (!site) throw new Error('NODE_CANDIDATE_SITE is missing');
  const root = join(site, 'node_modules', 'p-map');
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const exportMap = manifest.exports?.['.'] ?? manifest.exports;
  const entry = typeof exportMap === 'string'
    ? exportMap
    : exportMap?.default;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('package has no safe root export');
  }
  return {manifest, module: await import(pathToFileURL(join(root, entry)).href)};
}

async function invoke(request) {
  const {manifest, module: candidate} = await loadCandidate();
  const pMap = candidate.default;
  const {pMapIterable, pMapSkip} = candidate;
  const errorShape = error => ({name: error?.name, message: error?.message});
  const collect = async iterable => {
    const values = [];
    for await (const value of iterable) values.push(value);
    return values;
  };
  const ops = {
    package: () => ({
      name: manifest.name,
      version: manifest.version,
      default: typeof pMap,
      pMapIterable: typeof pMapIterable,
      pMapSkip: typeof pMapSkip,
      type: manifest.type,
      hasTypes: (manifest.exports?.['.'] ?? manifest.exports)?.types === './index.d.ts',
    }),
    basic: () => pMap([1, 2, 3], value => value * 2),
    order: async () => {
      const gates = [deferred(), deferred(), deferred()];
      const task = pMap([0, 1, 2], async index => {
        await gates[index].promise;
        return ['slow', 'fast', 'middle'][index];
      });
      await turns();
      gates[1].resolve();
      await turns();
      gates[2].resolve();
      await turns();
      gates[0].resolve();
      return task;
    },
    index: () => pMap(['a', 'b', 'c'], (value, index) => ({value, index})),
    'promise-input': () => pMap([Promise.resolve(10), Promise.resolve(20), 30], value => value),
    'async-input': async () => pMap((async function * () { yield 1; yield Promise.resolve(2); yield 3; })(), value => value * 3),
    concurrency: async () => {
      const gates = [deferred(), deferred(), deferred(), deferred()];
      let running = 0;
      let maxRunning = 0;
      const task = pMap([0, 1, 2, 3], async value => {
        running++;
        maxRunning = Math.max(maxRunning, running);
        await gates[value].promise;
        running--;
        return value;
      }, {concurrency: 2});
      await turns();
      gates[0].resolve();
      gates[1].resolve();
      await turns();
      gates[2].resolve();
      gates[3].resolve();
      return {maxRunning, values: await task};
    },
    'async-start': async () => {
      let called = false;
      const task = pMap([42], value => { called = true; return value; });
      const beforeTurn = called;
      return {beforeTurn, result: await task};
    },
    infinite: async () => {
      const started = [];
      try {
        await pMap([1, 2, 3], async value => {
          started.push(value);
          await new Promise(resolve => setImmediate(resolve));
          throw new Error(value === 1 ? 'first' : `later-${value}`);
        });
      } catch (error) {
        await turns(2);
        return {started, error: error.message};
      }
      return {started, error: null};
    },
    'invalid-input': async () => {
      try { await pMap(123, value => value); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
    'invalid-mapper': async () => {
      try { await pMap([], 'not-a-function'); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
    'invalid-concurrency': async () => {
      try { await pMap([], value => value, {concurrency: 0}); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
    'invalid-backpressure': async () => {
      try { pMapIterable([], value => value, {concurrency: 2, backpressure: 1}); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
    'mapper-error': async () => {
      try { await pMap([1], () => { throw new Error('mapper failed'); }); } catch (error) { return errorShape(error); }
      return {name: 'none'};
    },
    'source-error': async () => {
      const source = {[Symbol.iterator]: () => ({next() { throw new Error('source failed'); }})};
      try { await pMap(source, value => value); } catch (error) { return errorShape(error); }
      return {name: 'none'};
    },
    'stop-on-error': async () => {
      try { await pMap([1, 2], value => { throw new Error(value === 1 ? 'first' : 'second'); }, {concurrency: 1}); } catch (error) { return errorShape(error); }
      return {name: 'none'};
    },
    'aggregate-error': async () => {
      try { await pMap([1, 2], value => { throw new Error(value === 1 ? 'one' : 'two'); }, {stopOnError: false, concurrency: 1}); } catch (error) { return {name: error.name, errors: error.errors.map(item => item.message)}; }
      return {name: 'none'};
    },
    'aborted-signal': async () => {
      const controller = new AbortController();
      controller.abort();
      try { await pMap([1], value => value, {signal: controller.signal}); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
    'abort-signal': async () => {
      const controller = new AbortController();
      const gate = deferred();
      const task = pMap([1], async value => { await gate.promise; return value; }, {signal: controller.signal});
      await turns();
      controller.abort();
      try { await task; } catch (error) { gate.resolve(); return {name: error.name}; }
      gate.resolve();
      return {name: 'none'};
    },
    skip: () => pMap([1, 2, 3], value => value === 2 ? pMapSkip : value === 1 ? 'keep' : 'also-keep'),
    'skip-all': () => pMap([1, 2, 3], () => pMapSkip),
    'iterable-basic': () => collect(pMapIterable([1, 2, 3], value => value)),
    'iterable-order': async () => {
      const gates = [deferred(), deferred(), deferred()];
      const task = collect(pMapIterable([0, 1, 2], async index => { await gates[index].promise; return ['first', 'second', 'third'][index]; }, {concurrency: 3}));
      await turns();
      gates[2].resolve(); gates[1].resolve(); gates[0].resolve();
      return task;
    },
    'iterable-index': () => collect(pMapIterable(['x', 'y'], (value, index) => ({value, index}))),
    'iterable-async-input': () => collect(pMapIterable((async function * () { yield 4; yield 5; yield 6; })(), value => value)),
    'iterable-skip': () => collect(pMapIterable(['a', 'b', 'c'], value => value === 'b' ? pMapSkip : value)),
    'iterable-mapper-error': async () => {
      try { await collect(pMapIterable([1], () => { throw new Error('iterable mapper failed'); })); } catch (error) { return errorShape(error); }
      return {name: 'none'};
    },
    'iterable-source-error': async () => {
      const source = {[Symbol.iterator]: () => ({next() { throw new Error('iterable source failed'); }})};
      try { await collect(pMapIterable(source, value => value)); } catch (error) { return errorShape(error); }
      return {name: 'none'};
    },
    backpressure: async () => {
      const gates = [deferred(), deferred(), deferred()];
      const started = [];
      const iterator = pMapIterable([1, 2, 3], async value => { started.push(value); await gates[value - 1].promise; return value; }, {concurrency: 2, backpressure: 2})[Symbol.asyncIterator]();
      const firstTask = iterator.next();
      await turns();
      const startedAfterFirst = [...started];
      gates[0].resolve();
      const first = await firstTask;
      gates[1].resolve();
      gates[2].resolve();
      return {first: first.value, startedAfterFirst};
    },
    'bad-iterable-options': async () => {
      try { pMapIterable([], value => value, {concurrency: 2, backpressure: 1}); } catch (error) { return {name: error.name}; }
      return {name: 'none'};
    },
  };
  if (!ops[request.operation]) throw new Error(`unknown operation: ${request.operation}`);
  return await ops[request.operation]();
}

export function callCandidate(operation) {
  if (!site) throw new Error('candidate site is not configured');
  if (!adapter) throw new Error('adapter path is unavailable');
  const source = readFileSync(adapter, 'utf8');
  const moduleUrl = `data:text/javascript;base64,${Buffer.from(source).toString('base64')}`;
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=60', '--nproc=4096', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `NODE_CANDIDATE_SITE=${site}`, `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `P_MAP_OPERATION=${operation}`,
    process.execPath, '--no-addons', '--input-type=module', '--eval', `import(${JSON.stringify(moduleUrl)})`,
  ], {cwd: site, encoding: 'utf8', maxBuffer: 262144});
  const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1) ?? '';
  let payload;
  try { payload = JSON.parse(line); } catch { throw new Error(`candidate response malformed: ${result.stderr ?? result.stdout}`); }
  if (result.status !== 0 || payload.ok !== true) throw new Error(payload.fatal ?? 'candidate call failed');
  return payload.value;
}

if (childOperation) {
  try {
    const value = await invoke({operation: childOperation});
    emit({ok: true, value});
  } catch (error) {
    emit({ok: false, fatal: `${error?.name ?? 'Error'}: ${error?.message ?? error}`}, 1);
  }
}
