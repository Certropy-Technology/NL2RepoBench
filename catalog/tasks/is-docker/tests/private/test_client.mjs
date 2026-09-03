import {spawnSync} from 'node:child_process';

const candidate = process.env.NODE_CANDIDATE_SITE;
if (!candidate) throw new Error('NODE_CANDIDATE_SITE is required');

export function run(request) {
	const result = spawnSync(
		'/usr/bin/timeout',
		[
			'--signal=TERM', '--kill-after=5s', '30s',
			'/usr/sbin/runuser', '-u', 'candidate', '--',
			'/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
			'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin',
			`HOME=${candidate}/home`, `TMPDIR=${candidate}/tmp`,
			'NODE_ALLOWED_PACKAGE=is-docker',
			'/usr/local/bin/node', '--no-addons', '/tests/runtime/node/candidate_runner.mjs',
		],
		{
			cwd: candidate,
			input: `${JSON.stringify({package: 'is-docker', export: 'run', args: [request]})}\n`,
			encoding: 'utf8',
			timeout: 35_000,
			maxBuffer: 256 * 1024,
		},
	);
	if (result.error) throw result.error;
	let response;
	try {
		response = JSON.parse(result.stdout);
	} catch {
		throw new Error(`candidate returned malformed JSON: ${result.stderr || result.stdout}`);
	}
	if (!response.ok) throw new Error(response.message || response.error || 'candidate call failed');
	return response.value;
}
