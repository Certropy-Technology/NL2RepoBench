import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const MAX_BYTES = 256 * 1024;
let circuitFailure;

async function candidateMain() {
	const {readFileSync, statSync} = await import('node:fs');
	const {join} = await import('node:path');
	const {pathToFileURL} = await import('node:url');

	const emit = (payload, code = 0) => {
		const output = JSON.stringify(payload);
		if (Buffer.byteLength(output) > 256 * 1024) {
			process.exit(70);
		}

		process.stdout.write(`${output}\n`);
		process.exit(code);
	};

	try {
		const input = readFileSync(0);
		if (input.byteLength > 64 * 1024) {
			emit({ok: false, error: 'request-too-large'}, 64);
		}

		const request = JSON.parse(input.toString('utf8'));
		const packageRoot = join(process.cwd(), 'node_modules', 'npm-run-path');
		const manifest = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
		const exportsField = manifest.exports;
		const rootExport = typeof exportsField === 'string' ? exportsField : (exportsField?.['.'] ?? exportsField);
		const entry = typeof rootExport === 'string'
			? rootExport
			: (rootExport?.import ?? rootExport?.default);
		if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
			throw new Error('package root has no safe ESM entry');
		}

		const candidate = await import(pathToFileURL(join(packageRoot, entry)).href);
		if (request.operation === 'inspect') {
			emit({
				ok: true,
				value: {
					name: manifest.name,
					version: manifest.version,
					type: manifest.type,
					exports: manifest.exports,
					files: manifest.files,
					module_exports: Object.keys(candidate).sort(),
					declaration_exists: statSync(join(packageRoot, 'index.d.ts')).isFile(),
				},
			});
		}

		if (request.operation !== 'invoke' || !['npmRunPath', 'npmRunPathEnv'].includes(request.export)) {
			emit({ok: false, error: 'operation-not-allowlisted'}, 64);
		}

		let options = request.options;
		const before = JSON.stringify(options);
		if (options && typeof options === 'object' && !Array.isArray(options)) {
			options = {...options};
			if (Object.hasOwn(options, 'cwdUrl')) {
				options.cwd = new URL(options.cwdUrl);
				delete options.cwdUrl;
			}

			if (Object.hasOwn(options, 'execPathUrl')) {
				options.execPath = new URL(options.execPathUrl);
				delete options.execPathUrl;
			}
		}

		const value = await candidate[request.export](options);
		emit({
			ok: true,
			value,
			input_unchanged: before === JSON.stringify(request.options),
		});
	} catch (error) {
		emit({
			ok: false,
			error: 'candidate-call-failed',
			exception_type: error?.constructor?.name ?? 'Error',
			message: String(error?.message ?? error).slice(0, 4096),
		}, 1);
	}
}

const adapter = `(${candidateMain.toString()})()`;

export function requestCandidate(payload) {
	if (circuitFailure) {
		return {ok: false, error: circuitFailure};
	}

	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) {
		throw new Error('candidate site is not configured');
	}

	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM', '--kill-after=1s', '3s',
		'runuser', '-u', 'candidate', '--',
		'/usr/bin/prlimit', '--cpu=3', '--nproc=32', '--nofile=128', '--',
		'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin',
		`HOME=${site}/home`, `TMPDIR=${site}/tmp`,
		NODE, '--no-addons', '--input-type=module', '--eval', adapter,
	], {
		cwd: site,
		input: `${JSON.stringify(payload)}\n`,
		encoding: 'utf8',
		maxBuffer: MAX_BYTES,
		timeout: 5000,
	});

	if (result.error || [124, 137].includes(result.status)) {
		circuitFailure = 'candidate-timeout';
		return {ok: false, error: circuitFailure};
	}

	try {
		return JSON.parse(result.stdout);
	} catch {
		circuitFailure = 'candidate-response-malformed';
		return {ok: false, error: circuitFailure};
	}
}

export function invoke(exportName, options) {
	return requestCandidate({operation: 'invoke', export: exportName, options});
}

export function inspect() {
	return requestCandidate({operation: 'inspect'});
}
