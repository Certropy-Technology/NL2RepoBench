import {spawnSync} from 'node:child_process';
import {chmodSync, copyFileSync, readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;
let callSequence = 0;

function encode(value) {
  if (value === undefined) return {type: 'undefined'};
  if (value instanceof Error) {
    return {type: 'error', name: value.name, message: value.message};
  }
  return value;
}

function emit(payload, code = 0) {
  const text = JSON.stringify(payload);
  if (Buffer.byteLength(text) > MAX_RESPONSE_BYTES) process.exit(70);
  process.stdout.write(`${text}\n`);
  process.exit(code);
}

function getRequest() {
  const bytes = readFileSync(0);
  if (bytes.length > MAX_REQUEST_BYTES) emit({ok: false, error: 'request-too-large'}, 64);
  try {
    const value = JSON.parse(bytes.toString('utf8'));
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error();
    return value;
  } catch {
    emit({ok: false, error: 'malformed-request'}, 64);
  }
}

async function runScenario(universalify, scenario) {
  switch (scenario) {
    case 'shape':
      return {
        keys: Object.keys(universalify).sort(),
        types: {
          fromCallback: typeof universalify.fromCallback,
          fromPromise: typeof universalify.fromPromise,
        },
      };
    case 'callback-name': {
      function callbackSource() {}
      return universalify.fromCallback(callbackSource).name;
    }
    case 'promise-name': {
      function promiseSource() {}
      return universalify.fromPromise(promiseSource).name;
    }
    case 'callback-callback-success': {
      const calls = [];
      const wrapped = universalify.fromCallback(function (a, b, callback) {
        callback(null, {receiver: this, args: [a, b]});
      });
      const returned = wrapped.call({label: 'receiver'}, 1, 2, (...args) => calls.push(args.map(encode)));
      return {returned: encode(returned), calls};
    }
    case 'callback-promise-success': {
      const wrapped = universalify.fromCallback(function (a, b, callback) {
        queueMicrotask(() => callback(null, {receiver: this, args: [a, b]}));
      });
      return await wrapped.call({label: 'receiver'}, 3, 4);
    }
    case 'callback-apply-array': {
      const args = [5, 6];
      const wrapped = universalify.fromCallback((a, b, callback) => callback(null, [a, b]));
      const result = await wrapped.apply(null, args);
      return {args, result};
    }
    case 'callback-callback-error': {
      const calls = [];
      const wrapped = universalify.fromCallback(callback => callback(new TypeError('callback-failure')));
      wrapped((...args) => calls.push(args.map(encode)));
      return calls;
    }
    case 'callback-promise-error': {
      const wrapped = universalify.fromCallback(callback => callback(new RangeError('promise-failure')));
      try {
        await wrapped();
        return {settled: 'resolved'};
      } catch (error) {
        return {settled: 'rejected', error: encode(error)};
      }
    }
    case 'callback-falsey-error': {
      const wrapped = universalify.fromCallback(callback => callback(0, 'ignored'));
      try {
        await wrapped();
        return {settled: 'resolved'};
      } catch (error) {
        return {settled: 'rejected', error};
      }
    }
    case 'callback-null-success': {
      const wrapped = universalify.fromCallback(callback => callback(null, 'null-ok'));
      return await wrapped();
    }
    case 'callback-undefined-success': {
      const wrapped = universalify.fromCallback(callback => callback(undefined, 'undefined-ok'));
      return await wrapped();
    }
    case 'callback-first-result': {
      const wrapped = universalify.fromCallback(callback => callback(null, 'first', 'second'));
      return await wrapped();
    }
    case 'callback-nonfinal-function': {
      function marker() {}
      const wrapped = universalify.fromCallback((fn, value, callback) => {
        callback(null, {sameFunction: fn === marker, value});
      });
      return await wrapped(marker, 9);
    }
    case 'callback-sync-settlement': {
      const wrapped = universalify.fromCallback(callback => callback(null, 'sync'));
      const promise = wrapped();
      return {isPromise: promise instanceof Promise, value: await promise};
    }
    case 'callback-user-throw': {
      const wrapped = universalify.fromCallback(callback => callback(null, 'ok'));
      try {
        wrapped(() => { throw new Error('user-callback-threw'); });
        return {threw: false};
      } catch (error) {
        return {threw: true, error: encode(error)};
      }
    }
    case 'promise-callback-success': {
      const calls = [];
      const wrapped = universalify.fromPromise(function (a, b) {
        return Promise.resolve({receiver: this, args: [a, b]});
      });
      const returned = wrapped.call({label: 'receiver'}, 1, 2, (...args) => calls.push(args.map(encode)));
      await new Promise(resolve => setImmediate(resolve));
      return {returned: encode(returned), calls};
    }
    case 'promise-passthrough': {
      const sourcePromise = Promise.resolve('same');
      const wrapped = universalify.fromPromise(() => sourcePromise);
      const returned = wrapped();
      return {same: returned === sourcePromise, value: await returned};
    }
    case 'promise-promise-this': {
      const wrapped = universalify.fromPromise(function (...args) {
        return Promise.resolve({receiver: this, args});
      });
      return await wrapped.call({label: 'promise-receiver'}, 7, 8);
    }
    case 'promise-optional-callback': {
      const calls = [];
      const wrapped = universalify.fromPromise(function (...args) {
        return Promise.resolve({receiver: this, args});
      });
      wrapped.call({label: 'callback-receiver'}, 7, (...args) => calls.push(args.map(encode)));
      await new Promise(resolve => setImmediate(resolve));
      return calls;
    }
    case 'promise-callback-error': {
      const calls = [];
      const wrapped = universalify.fromPromise(() => Promise.reject(new SyntaxError('rejected')));
      wrapped((...args) => calls.push(args.map(encode)));
      await new Promise(resolve => setImmediate(resolve));
      return calls;
    }
    case 'promise-promise-error': {
      const wrapped = universalify.fromPromise(() => Promise.reject(new URIError('promise-rejected')));
      try {
        await wrapped();
        return {settled: 'resolved'};
      } catch (error) {
        return {settled: 'rejected', error: encode(error)};
      }
    }
    case 'promise-falsey-error': {
      const calls = [];
      const wrapped = universalify.fromPromise(() => Promise.reject(0));
      wrapped((...args) => calls.push(args.map(encode)));
      await new Promise(resolve => setImmediate(resolve));
      return calls;
    }
    case 'promise-user-throw': {
      let callbackCalls = 0;
      const rejection = new Promise(resolve => process.once('unhandledRejection', resolve));
      const wrapped = universalify.fromPromise(() => Promise.resolve('ok'));
      wrapped(() => {
        callbackCalls += 1;
        throw new Error('callback-throw-rejection');
      });
      const error = await rejection;
      return {callbackCalls, error: encode(error)};
    }
    case 'promise-thenable': {
      const calls = [];
      const wrapped = universalify.fromPromise(() => ({then(resolve) { resolve('thenable-ok'); }}));
      const returned = wrapped((...args) => calls.push(args.map(encode)));
      return {returned: encode(returned), calls};
    }
    default:
      throw new Error('scenario-not-allowlisted');
  }
}

async function childMain() {
  try {
    const request = getRequest();
    if (typeof request.scenario !== 'string' || request.scenario.length > 64) {
      emit({ok: false, error: 'scenario-not-allowlisted'}, 64);
    }
    const site = process.env.NODE_CANDIDATE_SITE;
    if (!site) emit({ok: false, error: 'candidate-site-missing'}, 64);
    const require = createRequire(pathToFileURL(`${site}/package.json`));
    const universalify = require('universalify');
    const value = await runScenario(universalify, request.scenario);
    emit({ok: true, value});
  } catch (error) {
    emit({
      ok: false,
      error: 'candidate-call-failed',
      exception_type: error?.constructor?.name ?? 'Error',
      message: String(error?.message ?? error),
    });
  }
}

export function callCandidate(scenario) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const adapter = `${site}/tmp/universalify-candidate-adapter-${process.pid}-${callSequence++}.mjs`;
  copyFileSync(process.env.NODE_TEST_CLIENT, adapter);
  chmodSync(adapter, 0o555);
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM', '--kill-after=2s', '8s', 'runuser', '-u', 'candidate', '--',
    '/usr/bin/prlimit', '--cpu=8', '--nproc=32', '--nofile=128', '--',
    'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
    `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, '/usr/local/bin/node',
    '--no-addons', adapter,
  ], {
    cwd: site,
    input: `${JSON.stringify({scenario})}\n`,
    encoding: 'utf8',
    timeout: 12_000,
    maxBuffer: MAX_RESPONSE_BYTES,
  });
  if (result.error) throw result.error;
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {ok: false, error: 'candidate-response-malformed', stderr: result.stderr};
  }
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  await childMain();
}
