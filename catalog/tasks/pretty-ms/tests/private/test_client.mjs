import {spawnSync} from 'node:child_process';

const runner = process.env.NODE_CANDIDATE_RUNNER ?? '/tests/runtime/node/candidate_runner.mjs';

export function invoke(milliseconds, options) {
	const request = {package: 'pretty-ms', export: 'default', args: [milliseconds]};
	if (options !== undefined) request.args.push(options);
	const result = spawnSync(process.execPath, [runner], {
		cwd: process.env.NODE_CANDIDATE_SITE,
		input: `${JSON.stringify(request)}\n`,
		encoding: 'utf8',
		timeout: 10_000,
		maxBuffer: 256 * 1024,
	});
	const line = (result.stdout ?? '').trim().split(/\r?\n/).at(-1);
	if (!line) return {ok: false, error: result.error?.message ?? result.stderr?.trim() ?? 'no response'};
	return JSON.parse(line);
}

export function value(milliseconds, options) {
	const response = invoke(milliseconds, options);
	if (!response.ok) throw new Error(`${response.exception_type ?? response.error}: ${response.message ?? ''}`);
	return response.value;
}
