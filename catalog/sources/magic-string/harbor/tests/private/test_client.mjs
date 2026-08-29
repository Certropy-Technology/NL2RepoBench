import {readFileSync, writeFileSync, chmodSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';

const site = process.env.NODE_CANDIDATE_SITE;
const adapterPath = '/tmp/magic-string-candidate-adapter.mjs';
let sequence = 0;
let loaded;

function loadPackage() {
  if (loaded) return loaded;
  const root = join(site, 'node_modules', 'magic-string');
  const metadata = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  loaded = import(pathToFileURL(join(root, 'dist', 'index.mjs')).href).then((module) => ({module, metadata}));
  return loaded;
}

function snapshot(value) {
  return {
    string: value.toString(),
    length: value.length(),
    lastChar: value.lastChar(),
    lastLine: value.lastLine(),
    isEmpty: value.isEmpty(),
    hasChanged: value.hasChanged(),
    indentString: value.getIndentString(),
  };
}

function serial(value) {
  if (value && typeof value === 'object' && typeof value.toString === 'function' && 'version' in value) {
    return JSON.parse(value.toString());
  }
  return value;
}

function runActions(value, actions) {
  const results = [];
  for (const item of actions ?? []) {
    const result = value[item.method](...(item.args ?? []));
    results.push(item.method === 'clone' ? snapshot(result) : serial(result));
  }
  return {results, final: snapshot(value)};
}

async function execute(request) {
  const {module, metadata} = await loadPackage();
  if (request.operation === 'inventory') {
    return {
      packageName: metadata.name,
      packageVersion: metadata.version,
      packageShape: metadata.type === 'module',
      exportNames: Object.keys(module).sort(),
      hasDefault: typeof module.default === 'function',
    };
  }
  if (request.operation === 'magic') {
    const payload = request.payload ?? {};
    const value = new module.default(payload.input ?? '', payload.options ?? {});
    const result = runActions(value, payload.actions);
    if (payload.cloneActions) {
      const clone = value.clone();
      result.clone = runActions(clone, payload.cloneActions);
      result.originalAfterClone = snapshot(value);
    }
    return result;
  }
  if (request.operation === 'bundle') {
    const payload = request.payload ?? {};
    const bundle = new module.Bundle(payload.options ?? {});
    for (const source of payload.sources ?? []) {
      const content = new module.default(source.input ?? '', source.options ?? {});
      runActions(content, source.actions);
      bundle.addSource({content, filename: source.filename, ignoreList: source.ignoreList, separator: source.separator});
    }
    const result = {results: [], final: {
      string: bundle.toString(), length: bundle.length(), isEmpty: bundle.isEmpty(), indentString: bundle.getIndentString(),
    }};
    for (const item of payload.actions ?? []) {
      const actionResult = bundle[item.method](...(item.args ?? []));
      result.results.push(item.method === 'clone'
        ? {string: actionResult.toString(), length: actionResult.length(), isEmpty: actionResult.isEmpty()}
        : serial(actionResult));
    }
    result.final = {string: bundle.toString(), length: bundle.length(), isEmpty: bundle.isEmpty(), indentString: bundle.getIndentString()};
    if (payload.cloneActions) {
      const clone = bundle.clone();
      for (const item of payload.cloneActions) clone[item.method](...(item.args ?? []));
      result.clone = {string: clone.toString(), length: clone.length(), isEmpty: clone.isEmpty()};
      result.originalAfterClone = {string: bundle.toString(), length: bundle.length(), isEmpty: bundle.isEmpty()};
    }
    return result;
  }
  throw new Error('unknown operation');
}

const input = readFileSync(0, 'utf8').trim();
const request = JSON.parse(input);
let response;
try {
  response = {id: request.id, ok: true, value: await execute(request)};
} catch (error) {
  response = {id: request.id, ok: false, error_type: error?.constructor?.name ?? 'Error', name: error?.name ?? 'Error', message: String(error?.message ?? error)};
}
process.stdout.write(`${JSON.stringify(response)}\n`);
