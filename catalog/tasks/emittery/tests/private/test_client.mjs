import {spawnSync} from 'node:child_process';
import {chmodSync, copyFileSync, mkdirSync} from 'node:fs';

const privateRoot = process.env.NODE_PRIVATE_ROOT ?? '/tests/private';
const adapterDirectory = '/tmp/emittery-adapter';
const adapterPath = `${adapterDirectory}/candidate_adapter.mjs`;
const perCallTimeoutMs = 3000;
const cumulativeTimeoutMs = 12_000;
let cumulativeDurationMs = 0;

mkdirSync(adapterDirectory, {recursive: true, mode: 0o755});
copyFileSync(`${privateRoot}/candidate_adapter.txt`, adapterPath);
chmodSync(adapterPath, 0o555);

export function callCandidate(scenario, input = {}) {
	if (cumulativeDurationMs >= cumulativeTimeoutMs) {
		throw new Error('candidate-call-budget-exhausted');
	}

	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) {
		throw new Error('candidate site is not configured');
	}

	const startedAt = Date.now();
	const result = spawnSync(
		'/usr/bin/timeout',
		[
			'--signal=TERM',
			'--kill-after=1s',
			'3s',
			'runuser',
			'-u',
			'candidate',
			'--',
			'/usr/bin/prlimit',
			'--cpu=6',
			'--nproc=32',
			'--nofile=128',
			'--fsize=1048576',
			'--',
			'env',
			'-i',
			'PATH=/usr/local/bin:/usr/bin:/bin',
			`HOME=${site}/home`,
			`TMPDIR=${site}/tmp`,
			`NODE_CANDIDATE_SITE=${site}`,
			'NODE_ALLOWED_PACKAGE=emittery',
			'/usr/local/bin/node',
			'--no-addons',
			adapterPath,
		],
		{
			cwd: site,
			input: `${JSON.stringify({scenario, input})}\n`,
			encoding: 'utf8',
			maxBuffer: 256 * 1024,
			timeout: perCallTimeoutMs,
		},
	);
	cumulativeDurationMs += Date.now() - startedAt;

	if (result.error) {
		throw new Error(`candidate-call-failed: ${result.error.message}`);
	}

	let payload;
	try {
		payload = JSON.parse(result.stdout);
	} catch {
		throw new Error(`candidate response malformed: ${result.stdout.slice(0, 256)}`);
	}

	if (!payload.ok) {
		throw new Error(`candidate-call-failed: ${payload.error ?? 'unknown-error'}`);
	}

	return payload.value;
}
