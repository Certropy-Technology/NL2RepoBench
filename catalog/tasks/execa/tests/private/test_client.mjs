import {spawnSync} from 'node:child_process';

const runner = '/tests/runtime/node/candidate_runner.mjs';
const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error('NODE_CANDIDATE_SITE is required');

export function call(exportName, args = []) {
	const child = spawnSync(process.execPath, [runner], {
		cwd: site,
		env: {...process.env, NODE_ALLOWED_PACKAGE: 'execa', NODE_OPTIONS: undefined, NODE_PATH: undefined},
		input: JSON.stringify({package: 'execa', export: exportName, args}),
		encoding: 'utf8',
		 timeout: 120_000,
	});
	const line = (child.stdout ?? '').trim().split(/\r?\n/).at(-1);
	let response;
	try {
		response = JSON.parse(line ?? 'null');
	} catch {
		throw new Error(`candidate runner returned malformed JSON: ${child.stderr ?? ''}`);
	}
	if (!response?.ok) throw new Error(response?.message ?? response?.error ?? 'candidate call failed');
	return response.value;
}
