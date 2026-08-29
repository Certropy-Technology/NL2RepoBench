import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync, statSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

function emit(payload, code = 0) {
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded) > 512 * 1024) {
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
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    fail('request-must-be-object', 64);
  }
  return value;
}

async function loadPackage() {
  const root = join(process.cwd(), 'node_modules', 'mdast-util-to-markdown');
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

function options(input) {
  const result = {};
  for (const key of [
    'bulletOther', 'bulletOrdered', 'bullet', 'closeAtx', 'emphasis', 'fences',
    'fence', 'incrementListMarker', 'listItemIndent', 'quote', 'resourceLink',
    'ruleRepetition', 'ruleSpaces', 'rule', 'setext', 'strong',
    'tightDefinitions', 'unsafe',
  ]) {
    if (Object.hasOwn(input, key)) result[key] = input[key];
  }
  if (input.extensionCase === 'handler') {
    result.handlers = {mention(node) { return '@' + node.value; }};
  } else if (input.extensionCase === 'extension') {
    result.extensions = [{handlers: {mention(node) { return '<' + node.value + '>'; }}}];
  } else if (input.extensionCase === 'join') {
    result.join = [
      (left, right) => left.type === 'paragraph' && right.type === 'paragraph' ? 0 : undefined,
    ];
  }
  return result;
}

const input = request();
try {
  const loaded = await loadPackage();
  const module = loaded.module;
  if (input.operation === 'inspect') {
    const types = loaded.manifest.types ?? loaded.manifest.typings ?? 'index.d.ts';
    let declarationExists = false;
    try {
      declarationExists = statSync(join(loaded.root, types)).isFile();
    } catch {}
    emit({ok: true, value: {
      name: loaded.manifest.name,
      version: loaded.manifest.version,
      type: loaded.manifest.type,
      entry: loaded.entry,
      types,
      declarationExists,
      hasBin: loaded.manifest.bin !== undefined,
      hasWorkspaces: loaded.manifest.workspaces !== undefined,
      dependencies: loaded.manifest.dependencies ?? {},
      lifecycleScripts: Object.keys(loaded.manifest.scripts ?? {}).filter((name) =>
        ['preinstall', 'install', 'postinstall', 'prepare', 'prepack', 'postpack'].includes(name),
      ),
      exportKinds: Object.fromEntries(Object.keys(module).sort().map((key) => [key, typeof module[key]])),
      handlerKinds: Object.fromEntries(
        Object.keys(module.defaultHandlers ?? {}).sort().map((key) => [key, typeof module.defaultHandlers[key]]),
      ),
    }});
  }
  if (input.operation === 'serialize') {
    const before = JSON.stringify(input.tree);
    const value = module.toMarkdown(input.tree, options(input.options ?? {}));
    const repeat = Number.isSafeInteger(input.repeat) && input.repeat > 1
      ? Array.from({length: Math.min(input.repeat, 8)}, () => module.toMarkdown(input.tree, options(input.options ?? {})))
      : undefined;
    emit({ok: true, value: {output: value, repeat, mutated: JSON.stringify(input.tree) !== before}});
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

function invoke(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM',
    '--kill-after=1s',
    '2s',
    'runuser',
    '-u',
    'candidate',
    '--',
    '/usr/bin/prlimit',
    '--cpu=2',
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
    maxBuffer: 512 * 1024,
    timeout: 4_000,
  });
  if (result.error || !result.stdout) throw new Error('candidate child failed');
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error('candidate child returned malformed JSON');
  }
}

function value(request) {
  const response = invoke(request);
  if (!response?.ok) throw new Error(response?.message ?? 'candidate call failed');
  return response.value;
}

export const inspect = () => value({operation: 'inspect'});
export const serialize = (tree, options = {}, repeat = 1) => value({operation: 'serialize', tree, options, repeat});
export const serializeResult = (tree, options = {}) => invoke({operation: 'serialize', tree, options});
