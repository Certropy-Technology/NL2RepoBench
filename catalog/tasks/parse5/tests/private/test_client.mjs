import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync, statSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const MAX_NODES = 4096;
const MAX_DEPTH = 96;

function emit(payload, code = 0) {
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded) > 2 * 1024 * 1024) {
    process.stderr.write('candidate response exceeds bound\n');
    process.exit(70);
  }
  process.stdout.write(encoded + '\n');
  process.exit(code);
}

function fail(message, code = 1) {
  emit({ok: false, message: String(message).slice(0, 4096)}, code);
}

function request() {
  const data = readFileSync(0);
  if (data.byteLength > 128 * 1024) fail('request-too-large', 64);
  let value;
  try {
    value = JSON.parse(data.toString('utf8'));
  } catch {
    fail('malformed-json', 64);
  }
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('request-must-be-object', 64);
  return value;
}

async function loadPackage() {
  const root = join(process.cwd(), 'node_modules', 'parse5');
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const rootExport = manifest.exports?.['.'] ?? manifest.exports;
  const entry = typeof rootExport === 'string'
    ? rootExport
    : rootExport?.import ?? rootExport?.default ?? manifest.module ?? manifest.main;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('package root has no safe ESM entry');
  }
  return {
    root,
    manifest,
    module: await import(pathToFileURL(join(root, entry)).href),
    entry,
  };
}

function location(value) {
  if (!value || typeof value !== 'object') return value ?? null;
  return Object.fromEntries(Object.entries(value).map(([key, nested]) => [
    key,
    nested && typeof nested === 'object' ? location(nested) : nested,
  ]));
}

function project(root) {
  let count = 0;
  function visit(node, depth) {
    if (!node || typeof node !== 'object') return null;
    count += 1;
    if (count > MAX_NODES || depth > MAX_DEPTH) throw new Error('tree projection exceeds bound');
    const value = {nodeName: node.nodeName};
    for (const key of ['tagName', 'namespaceURI', 'value', 'data', 'name', 'publicId', 'systemId', 'mode']) {
      if (Object.hasOwn(node, key)) value[key] = node[key];
    }
    if (Array.isArray(node.attrs)) {
      value.attrs = node.attrs.map(attr => ({
        name: attr.name,
        value: attr.value,
        namespace: attr.namespace ?? null,
        prefix: attr.prefix ?? null,
      }));
    }
    if (Object.hasOwn(node, 'sourceCodeLocation')) value.sourceCodeLocation = location(node.sourceCodeLocation);
    if (Array.isArray(node.childNodes)) value.childNodes = node.childNodes.map(child => visit(child, depth + 1));
    if (node.content) value.content = visit(node.content, depth + 1);
    return value;
  }
  return visit(root, 0);
}

function parserOptions(input, errors) {
  const options = {};
  if (Object.hasOwn(input, 'scriptingEnabled')) options.scriptingEnabled = Boolean(input.scriptingEnabled);
  if (input.locations) options.sourceCodeLocationInfo = true;
  if (input.errors) options.onParseError = error => errors.push(location(error));
  return options;
}

const input = request();
try {
  const loaded = await loadPackage();
  const m = loaded.module;
  if (input.operation === 'inspect') {
    const types = loaded.manifest.types ?? loaded.manifest.typings;
    const declarationExists = typeof types === 'string' && (() => {
      try { return statSync(join(loaded.root, types)).isFile(); } catch { return false; }
    })();
    emit({ok: true, value: {
      name: loaded.manifest.name,
      version: loaded.manifest.version,
      type: loaded.manifest.type,
      entry: loaded.entry,
      types,
      declarationExists,
      hasBin: loaded.manifest.bin !== undefined,
      exportKinds: Object.fromEntries(Object.keys(m).sort().map(key => [key, typeof m[key]])),
    }});
  }
  if (input.operation === 'constants') {
    emit({ok: true, value: {
      ns: m.html?.NS,
      errorCodes: {
        missingDoctype: m.ErrorCodes?.missingDoctype,
        duplicateAttribute: m.ErrorCodes?.duplicateAttribute,
        unexpectedNullCharacter: m.ErrorCodes?.unexpectedNullCharacter,
      },
      adapterMethods: Object.keys(m.defaultTreeAdapter ?? {}).sort(),
      parserStaticKinds: {
        parse: typeof m.Parser?.parse,
        getFragmentParser: typeof m.Parser?.getFragmentParser,
      },
      tokenizerModeType: typeof m.TokenizerMode,
    }});
  }
  if (input.operation === 'parse') {
    if (typeof input.html !== 'string') throw new TypeError('html must be a string');
    const errors = [];
    const document = m.parse(input.html, parserOptions(input, errors));
    emit({ok: true, value: {tree: project(document), html: m.serialize(document), errors}});
  }
  if (input.operation === 'fragment') {
    if (typeof input.html !== 'string') throw new TypeError('html must be a string');
    const errors = [];
    const options = parserOptions(input, errors);
    let fragment;
    if (typeof input.contextTag === 'string') {
      const namespace = input.contextNamespace ?? m.html.NS.HTML;
      const context = m.defaultTreeAdapter.createElement(input.contextTag, namespace, []);
      fragment = m.parseFragment(context, input.html, options);
    } else {
      fragment = m.parseFragment(input.html, options);
    }
    emit({ok: true, value: {tree: project(fragment), html: m.serialize(fragment), errors}});
  }
  if (input.operation === 'outer') {
    if (typeof input.html !== 'string') throw new TypeError('html must be a string');
    const fragment = m.parseFragment(input.html);
    const index = Number.isSafeInteger(input.index) ? input.index : 0;
    const node = fragment.childNodes[index];
    if (!node) throw new RangeError('child index is out of range');
    emit({ok: true, value: m.serializeOuter(node, {scriptingEnabled: input.scriptingEnabled !== false})});
  }
  fail('unsupported-operation', 64);
} catch (error) {
  emit({
    ok: false,
    message: String(error?.message ?? error).slice(0, 4096),
    exceptionType: error?.constructor?.name ?? 'Error',
  }, 1);
}
`;

function call(request) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM',
		'--kill-after=5s',
		'20s',
		'runuser',
		'-u',
		'candidate',
		'--',
		'/usr/bin/prlimit',
		'--cpu=20',
		'--nproc=32',
		'--nofile=128',
		'--',
		'env',
		'-i',
		'PATH=/usr/local/bin:/usr/bin:/bin',
		`HOME=${site}/home`,
		`TMPDIR=${site}/tmp`,
		NODE,
		'--no-addons',
		'--input-type=module',
		'--eval',
		ADAPTER,
	], {
		cwd: site,
		input: JSON.stringify(request),
		encoding: 'utf8',
		maxBuffer: 2 * 1024 * 1024,
		timeout: 25_000,
	});
	if (result.error || !result.stdout) throw new Error('candidate child failed');
	let response;
	try {
		response = JSON.parse(result.stdout);
	} catch {
		throw new Error('candidate child returned malformed JSON');
	}
	if (!response?.ok) throw new Error(response?.message ?? 'candidate call failed');
	return response.value;
}

export const inspect = () => call({operation: 'inspect'});
export const constants = () => call({operation: 'constants'});
export const parseDocument = (html, options = {}) => call({operation: 'parse', html, ...options});
export const parseFragment = (html, options = {}) => call({operation: 'fragment', html, ...options});
export const serializeOuter = (html, index = 0, options = {}) => call({operation: 'outer', html, index, ...options});
