import {spawnSync} from 'node:child_process';

export const STYLE_CASES = [
	['reset', 0, 0],
	['bold', 1, 22],
	['dim', 2, 22],
	['italic', 3, 23],
	['underline', 4, 24],
	['underlineDouble', '4:2', 24],
	['underlineCurly', '4:3', 24],
	['underlineDotted', '4:4', 24],
	['underlineDashed', '4:5', 24],
	['overline', 53, 55],
	['inverse', 7, 27],
	['hidden', 8, 28],
	['strikethrough', 9, 29],
	['black', 30, 39],
	['red', 31, 39],
	['green', 32, 39],
	['yellow', 33, 39],
	['blue', 34, 39],
	['magenta', 35, 39],
	['cyan', 36, 39],
	['white', 37, 39],
	['gray', 90, 39],
	['bgBlack', 40, 49],
	['bgRed', 41, 49],
	['bgGreen', 42, 49],
	['bgYellow', 43, 49],
	['bgBlue', 44, 49],
	['bgMagenta', 45, 49],
	['bgCyan', 46, 49],
	['bgWhite', 47, 49],
	['bgGray', 100, 49],
	['redBright', 91, 39],
	['greenBright', 92, 39],
	['yellowBright', 93, 39],
	['blueBright', 94, 39],
	['magentaBright', 95, 39],
	['cyanBright', 96, 39],
	['whiteBright', 97, 39],
	['bgRedBright', 101, 49],
	['bgGreenBright', 102, 49],
	['bgYellowBright', 103, 49],
	['bgBlueBright', 104, 49],
	['bgMagentaBright', 105, 49],
	['bgCyanBright', 106, 49],
	['bgWhiteBright', 107, 49],
	['underlineBlack', '58;5;0', 59],
	['underlineRed', '58;5;1', 59],
	['underlineGreen', '58;5;2', 59],
	['underlineYellow', '58;5;3', 59],
	['underlineBlue', '58;5;4', 59],
	['underlineMagenta', '58;5;5', 59],
	['underlineCyan', '58;5;6', 59],
	['underlineWhite', '58;5;7', 59],
	['underlineGray', '58;5;8', 59],
	['underlineRedBright', '58;5;9', 59],
	['underlineGreenBright', '58;5;10', 59],
	['underlineYellowBright', '58;5;11', 59],
	['underlineBlueBright', '58;5;12', 59],
	['underlineMagentaBright', '58;5;13', 59],
	['underlineCyanBright', '58;5;14', 59],
	['underlineWhiteBright', '58;5;15', 59],
];

export const STYLE_NAMES = STYLE_CASES.map(([name]) => name);

const CHILD = String.raw`
import {readFileSync} from 'node:fs';
import {join, normalize, sep} from 'node:path';
import {pathToFileURL} from 'node:url';

const packageRoot = join(process.cwd(), 'node_modules', 'yoctocolors');
const manifestPath = join(packageRoot, 'package.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const rootExport = manifest.exports?.['.'] ?? manifest.exports;
const entry = typeof rootExport === 'string'
  ? rootExport
  : rootExport?.import ?? rootExport?.default;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..') || entry.includes('\\')) {
  throw new Error('package root has no safe ESM default entry');
}
const resolvedEntry = normalize(join(packageRoot, entry));
if (!resolvedEntry.startsWith(packageRoot + sep)) throw new Error('package export escapes root');
const candidate = await import(pathToFileURL(resolvedEntry).href);
const request = JSON.parse(readFileSync(0, 'utf8'));
const allowed = new Set(request.allowedStyles);

function style(surface, name) {
  if (!allowed.has(name) || typeof surface?.[name] !== 'function') {
    throw new Error('style export is unavailable');
  }
  return surface[name];
}

function evaluate(surface, expression, depth = 0) {
  if (depth > 16 || expression === null || typeof expression !== 'object') {
    return expression;
  }
  if (expression.kind === 'literal') return expression.value;
  if (expression.kind === 'coercible') return {toString: () => expression.value};
  if (expression.kind === 'concat') {
    if (!Array.isArray(expression.parts) || expression.parts.length > 32) throw new Error('invalid concat');
    return expression.parts.map(part => evaluate(surface, part, depth + 1)).join('');
  }
  if (expression.kind === 'style') {
    return style(surface, expression.method)(evaluate(surface, expression.value, depth + 1));
  }
  throw new Error('unknown expression');
}

function boundedText(name) {
  const path = join(packageRoot, name);
  const value = readFileSync(path, 'utf8');
  if (Buffer.byteLength(value) > 64 * 1024) throw new Error('declaration too large');
  return value;
}

let value;
if (request.operation === 'evaluate') {
  const surface = request.surface === 'default' ? candidate.default : candidate;
  value = evaluate(surface, request.expression);
} else if (request.operation === 'metadata') {
  const baseDeclaration = boundedText('base.d.ts');
  const indexDeclaration = boundedText('index.d.ts');
  value = {
    manifest: {
      name: manifest.name,
      version: manifest.version,
      type: manifest.type,
      exports: manifest.exports,
      sideEffects: manifest.sideEffects,
      engines: manifest.engines,
      files: manifest.files,
      dependencies: manifest.dependencies ?? {},
    },
    namedExports: Object.keys(candidate).sort(),
    defaultExports: Object.keys(candidate.default ?? {}).sort(),
    declaredFormats: [...baseDeclaration.matchAll(/export const ([A-Za-z0-9_]+): Format;/g)]
      .map(match => match[1]).sort(),
    hasFormatType: /export type Format = \(string: string\) => string;/.test(baseDeclaration),
    indexDeclaration,
  };
} else {
  throw new Error('unknown operation');
}
process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
`;

export function literal(value) {
	return {kind: 'literal', value};
}

export function coercible(value) {
	return {kind: 'coercible', value};
}

export function concat(...parts) {
	return {kind: 'concat', parts};
}

export function styled(method, value) {
	return {kind: 'style', method, value};
}

export function callCandidate(request, {forceColor = '1'} = {}) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const input = JSON.stringify({...request, allowedStyles: STYLE_NAMES});
	if (Buffer.byteLength(input) > 64 * 1024) throw new Error('candidate request is too large');
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM', '--kill-after=1s', '2s',
		'runuser', '-u', 'candidate', '--',
		'/usr/bin/prlimit', '--cpu=2', '--nproc=32', '--nofile=128', '--fsize=262144', '--',
		'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`,
		`TMPDIR=${site}/tmp`, `FORCE_COLOR=${forceColor}`,
		'/usr/local/bin/node', '--no-addons', '--input-type=module', '--eval', CHILD,
	], {
		cwd: site,
		input: `${input}\n`,
		encoding: 'utf8',
		maxBuffer: 256 * 1024,
		timeout: 3000,
	});
	if (result.error) throw result.error;
	let payload;
	try {
		payload = JSON.parse(result.stdout);
	} catch {
		throw new Error(`candidate response malformed (exit ${result.status}): ${result.stderr}`);
	}
	if (!payload?.ok) throw new Error(payload?.error ?? 'candidate operation failed');
	return payload.value;
}

export function evaluate(expression, options) {
	return callCandidate({operation: 'evaluate', surface: 'named', expression}, options);
}

export function evaluateDefault(expression, options) {
	return callCandidate({operation: 'evaluate', surface: 'default', expression}, options);
}

export function metadata() {
	return callCandidate({operation: 'metadata'});
}
