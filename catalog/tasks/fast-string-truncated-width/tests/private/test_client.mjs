import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const maxRequestBytes = 256 * 1024;

function fail(message) {
  process.stdout.write(JSON.stringify({ok: false, message: String(message).slice(0, 2048)}) + '\n');
  process.exit(1);
}

function safeEntry(value, label) {
  if (typeof value !== 'string' || !value.startsWith('./') || value.includes('..')) {
    throw new Error('fast-string-truncated-width package has no safe ' + label);
  }
  return value;
}

async function loadPackage() {
  const root = join(process.cwd(), 'node_modules', 'fast-string-truncated-width');
  const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const rootExport = packageJson.exports?.['.'] ?? packageJson.exports;
  const runtimeEntry = safeEntry(
    typeof rootExport === 'string'
      ? rootExport
      : rootExport?.import ?? rootExport?.default ?? packageJson.module ?? packageJson.main,
    'ESM root export',
  );
  const declarationEntry = safeEntry(packageJson.types ?? rootExport?.types, 'declaration entry');
  const api = await import(pathToFileURL(join(root, runtimeEntry)).href);
  return {api, packageJson, root, runtimeEntry, declarationEntry};
}

function packageShape(loaded) {
  const {api, packageJson, root, runtimeEntry, declarationEntry} = loaded;
  const declaration = readFileSync(join(root, declarationEntry), 'utf8');
  readFileSync(join(root, runtimeEntry));
  return {
    name: packageJson.name,
    version: packageJson.version,
    type: packageJson.type,
    defaultCallable: typeof api.default === 'function',
    runtimeEntry,
    declarationEntry,
    declaration: declaration.slice(0, 32768),
    runtimeDependencies: Object.keys(packageJson.dependencies ?? {}).sort(),
  };
}

function invoke(api, request) {
  return api.default(
    request.input,
    request.truncationOptions ?? {},
    request.widthOptions ?? {},
  );
}

async function main() {
  const input = readFileSync(0);
  if (input.byteLength > maxRequestBytes) throw new Error('request is too large');
  const request = JSON.parse(input.toString('utf8'));
  if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.operation !== 'string') {
    throw new Error('request is malformed');
  }
  const loaded = await loadPackage();
  let value;
  if (request.operation === 'inspect') {
    value = packageShape(loaded);
  } else if (request.operation === 'measure') {
    if (typeof request.input !== 'string') throw new Error('measure input must be a string');
    value = invoke(loaded.api, request);
  } else if (request.operation === 'repeat') {
    if (typeof request.input !== 'string') throw new Error('repeat input must be a string');
    const count = request.count;
    if (!Number.isInteger(count) || count < 1 || count > 10) throw new Error('repeat count is invalid');
    value = Array.from({length: count}, () => invoke(loaded.api, request));
  } else {
    throw new Error('operation is not allowlisted');
  }
  process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
}

main().catch(error => fail(error?.message ?? error));
`;

function call(request) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM',
		'--kill-after=5s',
		'30s',
		'runuser',
		'-u',
		'candidate',
		'--',
		'/usr/bin/prlimit',
		'--cpu=30',
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
		maxBuffer: 256 * 1024,
		timeout: 35_000,
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
export const measure = (input, truncationOptions, widthOptions) => call({
	operation: 'measure',
	input,
	truncationOptions,
	widthOptions,
});
export const repeat = (input, count, truncationOptions, widthOptions) => call({
	operation: 'repeat',
	input,
	count,
	truncationOptions,
	widthOptions,
});
