if (process.env.NODE_TEST_CONTEXT) process.exit(0);

import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const PACKAGE = 'parse-npm-tarball-url';
const EXPORT = 'parseNpmTarballUrl';
const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;
const MAX_DEPTH = 16;
const NAME_PATTERN = /^[A-Za-z0-9_.@/-]{1,128}$/;

function emit(id, payload, code = 0) {
  const encoded = JSON.stringify({id, ...payload});
  if (Buffer.byteLength(encoded) > MAX_RESPONSE_BYTES) {
    process.stdout.write(JSON.stringify({id, ok: false, error_type: 'response-too-large', message: 'response is too large'}) + '\n');
    process.exit(70);
  }
  process.stdout.write(`${encoded}\n`);
  process.exit(code);
}

function fail(id, errorType, message, code = 64) {
  emit(id, {ok: false, error_type: errorType, message: String(message).slice(0, 512)}, code);
}

function isJsonValue(value, depth = 0) {
  if (depth > MAX_DEPTH) return false;
  if (value === null || typeof value === 'string' || typeof value === 'boolean') return true;
  if (typeof value === 'number') return Number.isFinite(value);
  if (Array.isArray(value)) return value.length <= 64 && value.every(item => isJsonValue(item, depth + 1));
  if (typeof value === 'object') {
    return Object.keys(value).length <= 64 && Object.entries(value).every(([key, item]) => key.length <= 128 && isJsonValue(item, depth + 1));
  }
  return false;
}

function request() {
  const data = readFileSync(0);
  if (data.byteLength > MAX_REQUEST_BYTES) fail('', 'request-too-large', 'request is too large');
  let requestValue;
  try {
    requestValue = JSON.parse(data.toString('utf8'));
  } catch {
    fail('', 'malformed-json', 'request is malformed');
  }
  if (!requestValue || typeof requestValue !== 'object' || Array.isArray(requestValue)) fail('', 'malformed-request', 'request must be an object');
  const id = requestValue.id;
  if (typeof id !== 'string' || id.length < 1 || id.length > 128) fail('', 'invalid-id', 'id is not bounded');
  if (typeof requestValue.operation !== 'string' || !['call', 'inventory'].includes(requestValue.operation)) fail(id, 'operation-not-allowlisted', 'operation is not allowlisted');
  if (!requestValue.payload || typeof requestValue.payload !== 'object' || Array.isArray(requestValue.payload)) fail(id, 'malformed-payload', 'payload must be an object');
  return {id, operation: requestValue.operation, payload: requestValue.payload};
}

function safeEntry(packageJson, root) {
  const rootExport = packageJson.exports?.['.'];
  const runtimeEntry = rootExport?.default ?? rootExport?.import;
  const declarationEntry = rootExport?.types;
  if (packageJson.name !== PACKAGE || packageJson.version !== '5.0.0' || packageJson.type !== 'module' || typeof runtimeEntry !== 'string' || typeof declarationEntry !== 'string') {
    throw new Error('package shape is invalid');
  }
  for (const entry of [runtimeEntry, declarationEntry]) {
    if (!entry.startsWith('./') || entry.includes('..') || entry.includes('\\')) throw new Error('package entry is unsafe');
    readFileSync(join(root, entry));
  }
  return {runtimeEntry, declarationEntry};
}

async function load() {
  const root = join(process.cwd(), 'node_modules', PACKAGE);
  const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const entries = safeEntry(packageJson, root);
  const api = await import(pathToFileURL(join(root, entries.runtimeEntry)).href);
  return {api, packageJson, root, entries};
}

async function main() {
  const {id, operation, payload} = request();
  if (operation === 'inventory') {
    if (Object.keys(payload).length !== 0) fail(id, 'malformed-payload', 'inventory payload must be empty');
    const {api, packageJson, root, entries} = await load();
    emit(id, {
      ok: true,
      value: {
        packageName: packageJson.name,
        packageVersion: packageJson.version,
        packageShape: true,
        runtimeEntry: Boolean(readFileSync(join(root, entries.runtimeEntry))),
        declarationEntry: Boolean(readFileSync(join(root, entries.declarationEntry))),
        exportNames: Object.keys(api).sort(),
      },
    });
  }
  if (Object.keys(payload).length !== 1 || !Array.isArray(payload.args) || payload.args.length !== 1 || !isJsonValue(payload.args[0])) {
    fail(id, 'malformed-arguments', 'call requires one bounded JSON value');
  }
  const {api} = await load();
  if (typeof api[EXPORT] !== 'function' || Object.keys(api).some(name => name !== EXPORT)) fail(id, 'export-shape-invalid', 'named runtime export is invalid');
  try {
    const result = await api[EXPORT](payload.args[0]);
    if (!isJsonValue(result)) fail(id, 'non-json-result', 'result is not JSON-safe');
    emit(id, {ok: true, value: result});
  } catch (error) {
    const type = typeof error?.constructor?.name === 'string' ? error.constructor.name : 'Error';
    fail(id, type, error?.message ?? error, 1);
  }
}

main().catch(error => fail('', error?.constructor?.name ?? 'Error', error?.message ?? error, 1));
