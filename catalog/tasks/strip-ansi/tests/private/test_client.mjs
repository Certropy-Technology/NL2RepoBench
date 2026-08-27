import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const maxRequestBytes = 64 * 1024;

function fail(message) {
  process.stdout.write(JSON.stringify({ok: false, message: String(message).slice(0, 2048)}) + '\n');
  process.exit(1);
}

async function loadPackage() {
  const root = join(process.cwd(), 'node_modules', 'strip-ansi');
  const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const rootExport = packageJson.exports?.['.'] ?? packageJson.exports;
  const entry = typeof rootExport === 'string'
    ? rootExport
    : rootExport?.import ?? rootExport?.default ?? packageJson.module ?? packageJson.main;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('strip-ansi package has no safe ESM entry');
  }
  const api = await import(pathToFileURL(join(root, entry)).href);
  return {api, packageJson, root};
}

function packageShape(api, packageJson, root) {
  const rootExport = packageJson.exports?.['.'] ?? packageJson.exports;
  const runtimeEntry = typeof rootExport === 'string'
    ? rootExport
    : rootExport?.import ?? rootExport?.default;
  const declarationEntry = packageJson.types ?? rootExport?.types;
  let filesExist = true;
  try {
    readFileSync(join(root, runtimeEntry));
    readFileSync(join(root, declarationEntry));
  } catch {
    filesExist = false;
  }
  return {
    name: packageJson.name,
    version: packageJson.version,
    type: packageJson.type,
    defaultCallable: typeof api.default === 'function',
    runtimeEntry,
    declarationEntry,
    filesExist,
  };
}

async function main() {
  const input = readFileSync(0);
  if (input.byteLength > maxRequestBytes) throw new Error('request is too large');
  const request = JSON.parse(input.toString('utf8'));
  if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.operation !== 'string') {
    throw new Error('request is malformed');
  }
  const {api, packageJson, root} = await loadPackage();
  let value;
  if (request.operation === 'inspect') {
    value = packageShape(api, packageJson, root);
  } else if (request.operation === 'strip') {
    try {
      value = {ok: true, result: api.default(request.value)};
    } catch (error) {
      value = {
        ok: false,
        exceptionType: error?.constructor?.name ?? 'Error',
        message: String(error?.message ?? error).slice(0, 2048),
      };
    }
  } else {
    throw new Error('operation is not allowlisted');
  }
  process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
}

main().catch(error => fail(error?.message ?? error));
`;

function call(operation, value) {
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
		input: JSON.stringify({operation, value}),
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

export const inspect = () => call('inspect');
export const strip = value => call('strip', value);
