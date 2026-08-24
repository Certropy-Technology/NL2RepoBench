import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const maxRequestBytes = 64 * 1024;
const maxChainLength = 24;
const modelStyles = new Set(['rgb', 'hex', 'ansi256', 'bgRgb', 'bgHex', 'bgAnsi256', 'underlineRgb', 'underlineHex', 'underlineAnsi256']);
const namedStyles = new Set([
  'reset', 'bold', 'dim', 'italic', 'underline', 'underlineDouble', 'underlineCurly', 'underlineDotted', 'underlineDashed', 'overline', 'inverse', 'hidden', 'strikethrough', 'visible',
  'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'blackBright', 'gray', 'grey', 'redBright', 'greenBright', 'yellowBright', 'blueBright', 'magentaBright', 'cyanBright', 'whiteBright',
  'bgBlack', 'bgRed', 'bgGreen', 'bgYellow', 'bgBlue', 'bgMagenta', 'bgCyan', 'bgWhite', 'bgBlackBright', 'bgGray', 'bgGrey', 'bgRedBright', 'bgGreenBright', 'bgYellowBright', 'bgBlueBright', 'bgMagentaBright', 'bgCyanBright', 'bgWhiteBright',
  'underlineBlack', 'underlineRed', 'underlineGreen', 'underlineYellow', 'underlineBlue', 'underlineMagenta', 'underlineCyan', 'underlineWhite', 'underlineBlackBright', 'underlineGray', 'underlineGrey', 'underlineRedBright', 'underlineGreenBright', 'underlineYellowBright', 'underlineBlueBright', 'underlineMagentaBright', 'underlineCyanBright', 'underlineWhiteBright',
]);

function fail(message) {
  process.stdout.write(JSON.stringify({ok: false, message: String(message).slice(0, 2048)}) + '\n');
  process.exit(1);
}

async function loadChalk() {
  const root = join(process.cwd(), 'node_modules', 'chalk');
  const packageJson = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  const exportsValue = packageJson.exports;
  const entry = typeof exportsValue === 'string'
    ? exportsValue
    : exportsValue?.['.']?.import ?? exportsValue?.['.']?.default ?? exportsValue?.import ?? exportsValue?.default ?? packageJson.module ?? packageJson.main;
  if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
    throw new Error('chalk package has no safe ESM entry');
  }

  return {api: await import(pathToFileURL(join(root, entry)).href), packageJson, root};
}

function validateLevel(level) {
  if (!Number.isSafeInteger(level) || level < 0 || level > 3) {
    throw new Error('level must be an integer from 0 to 3');
  }
}

function chain(instance, steps) {
  if (!Array.isArray(steps) || steps.length > maxChainLength) {
    throw new Error('style chain is not bounded');
  }

  let builder = instance;
  for (const step of steps) {
    if (!step || typeof step !== 'object' || Array.isArray(step) || typeof step.name !== 'string' || !Array.isArray(step.args)) {
      throw new Error('style step is malformed');
    }

    if (modelStyles.has(step.name)) {
      builder = builder[step.name](...step.args);
    } else if (namedStyles.has(step.name) && step.args.length === 0) {
      builder = builder[step.name];
    } else {
      throw new Error('style name is not allowlisted');
    }
  }

  return builder;
}

function support(value) {
  if (value === false) return false;
  if (!value || typeof value !== 'object') return null;
  return {
    level: value.level,
    hasBasic: value.hasBasic,
    has256: value.has256,
    has16m: value.has16m,
  };
}

function packageShape(packageJson, root) {
  const rootExport = packageJson.exports?.['.'];
  const runtimeEntry = rootExport?.default;
  const declarationEntry = rootExport?.types;
  if (packageJson.type !== 'module' || typeof runtimeEntry !== 'string' || typeof declarationEntry !== 'string') {
    return false;
  }

  try { readFileSync(join(root, runtimeEntry)); readFileSync(join(root, declarationEntry)); } catch { return false; }
  return true;
}

function inventory(api, packageJson, root) {
  return {
    packageShape: packageShape(packageJson, root),
    defaultCallable: typeof api.default === 'function',
    chalkConstructor: typeof api.Chalk === 'function',
    chalkStderrCallable: typeof api.chalkStderr === 'function',
    aliases: {
      modifiers: api.modifiers === api.modifierNames,
      foregroundColors: api.foregroundColors === api.foregroundColorNames,
      backgroundColors: api.backgroundColors === api.backgroundColorNames,
      colors: api.colors === api.colorNames,
    },
    modifierNames: api.modifierNames,
    foregroundColorNames: api.foregroundColorNames,
    backgroundColorNames: api.backgroundColorNames,
    underlineColorNames: api.underlineColorNames,
    colorNames: api.colorNames,
    supportsColor: support(api.supportsColor),
    supportsColorStderr: support(api.supportsColorStderr),
  };
}

async function main() {
  const input = readFileSync(0);
  if (input.byteLength > maxRequestBytes) throw new Error('request is too large');
  const request = JSON.parse(input.toString('utf8'));
  if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.operation !== 'string' || !request.payload || typeof request.payload !== 'object' || Array.isArray(request.payload)) {
    throw new Error('request is malformed');
  }

  const {api, packageJson, root} = await loadChalk();
  let value;
  if (request.operation === 'format') {
    const {level, steps, values} = request.payload;
    if (!Array.isArray(values) || values.length > 32) throw new Error('values are not bounded');
    value = chain(new api.Chalk({level}), steps)(...values);
  } else if (request.operation === 'inventory') {
    value = inventory(api, packageJson, root);
  } else if (request.operation === 'level-transition') {
    const {start, next, chain: steps, values} = request.payload;
    validateLevel(start);
    validateLevel(next);
    if (!Array.isArray(values) || values.length > 32) throw new Error('values are not bounded');
    const root = new api.Chalk({level: start});
    const builder = chain(root, steps);
    builder.level = next;
    value = {rootLevel: root.level, builderLevel: builder.level, value: builder(...values)};
  } else if (request.operation === 'level-assignment') {
    const {start, next, chain: steps, values} = request.payload;
    validateLevel(start);
    if (!Array.isArray(values) || values.length > 32) throw new Error('values are not bounded');
    const root = new api.Chalk({level: start});
    const builder = chain(root, steps);
    let error = '';
    try {
      builder.level = next;
    } catch (caught) {
      error = String(caught?.message ?? caught);
    }

    value = {rootLevel: root.level, builderLevel: builder.level, error, value: builder(...values)};
  } else {
    throw new Error('operation is not allowlisted');
  }

  process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
}

main().catch(error => fail(error?.message ?? error));
`;

function call(operation, payload) {
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
		'TERM=dumb',
		'CI=true',
		'FORCE_COLOR=0',
		'LC_ALL=C.UTF-8',
		NODE,
		'--no-addons',
		'--input-type=module',
		'--eval',
		ADAPTER,
	], {
		cwd: site,
		input: JSON.stringify({operation, payload}),
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

export const format = (level, steps, values) => call('format', {level, steps, values});
export const inventory = () => call('inventory', {});
export const levelTransition = payload => call('level-transition', payload);
export const levelAssignment = payload => call('level-assignment', payload);
