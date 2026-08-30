import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const site = process.env.NODE_CANDIDATE_SITE;
const runner = '/tests/runtime/node/candidate_runner.mjs';
const perCallTimeoutMs = 2000;
const cumulativeTimeoutMs = 45_000;
let cumulativeDurationMs = 0;

if (!site) {
	throw new Error('candidate site is not configured');
}

export function inspectPackage() {
	const packageRoot = join(site, 'node_modules', 'widest-line');
	const manifest = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
	const exports = manifest.exports;
	return {
		name: manifest.name,
		version: manifest.version,
		type: manifest.type,
		defaultExport: exports?.default ?? exports?.['.']?.default,
		typesExport: exports?.types ?? exports?.['.']?.types,
		dependencies: manifest.dependencies ?? {},
	};
}

export function callCandidate(...args) {
	if (cumulativeDurationMs >= cumulativeTimeoutMs) {
		return {ok: false, error: 'candidate-call-budget-exhausted'};
	}

	const startedAt = Date.now();
	const result = spawnSync(
		'/usr/bin/timeout',
		[
			'--signal=TERM',
			'--kill-after=1s',
			'1s',
			'runuser',
			'-u',
			'candidate',
			'--',
			'/usr/bin/prlimit',
			'--cpu=3',
			'--nproc=32',
			'--nofile=128',
			'--fsize=1048576',
			'--',
			'env',
			'-i',
			'PATH=/usr/local/bin:/usr/bin:/bin',
			`HOME=${site}/home`,
			`TMPDIR=${site}/tmp`,
			'NODE_ALLOWED_PACKAGE=widest-line',
			'/usr/local/bin/node',
			'--no-addons',
			runner,
		],
		{
			cwd: site,
			input: `${JSON.stringify({package: 'widest-line', export: 'default', args})}\n`,
			encoding: 'utf8',
			maxBuffer: 256 * 1024,
			timeout: perCallTimeoutMs,
		},
	);
	cumulativeDurationMs += Date.now() - startedAt;

	if (result.error) {
		return {ok: false, error: `candidate-call-failed: ${result.error.message}`};
	}

	try {
		return JSON.parse(result.stdout);
	} catch {
		return {ok: false, error: 'candidate-response-malformed'};
	}
}
