import {spawnSync} from 'node:child_process';

const candidate = process.env.NODE_CANDIDATE_SITE;
if (!candidate) {
	throw new Error('NODE_CANDIDATE_SITE is required');
}

export async function run(request) {
	const result = spawnSync(
		'/usr/sbin/runuser',
		[
			'-u',
			'candidate',
			'--',
			process.execPath,
			'--no-addons',
			'/tests/runtime/node/candidate_runner.mjs',
		],
		{
			cwd: candidate,
			env: {
				PATH: '/usr/local/bin:/usr/bin:/bin',
				NODE_ALLOWED_PACKAGE: 'is-stream',
			},
			input: `${JSON.stringify({package: 'is-stream', export: 'run', args: [request]})}\n`,
			encoding: 'utf8',
			timeout: 5000,
			maxBuffer: 256 * 1024,
		},
	);

	if (result.error) {
		throw result.error;
	}

	let payload;
	try {
		payload = JSON.parse(result.stdout);
	} catch {
		throw new Error(`candidate returned malformed JSON: ${result.stderr || result.stdout}`);
	}

	if (!payload.ok) {
		throw new Error(payload.message || payload.error || 'candidate call failed');
	}

	return payload.value;
}
