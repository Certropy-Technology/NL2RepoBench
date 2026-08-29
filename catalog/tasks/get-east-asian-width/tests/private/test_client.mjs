import {spawnSync} from 'node:child_process';
import {dirname, join} from 'node:path';

const packageName = 'get-east-asian-width';
const clientPath = process.env.NODE_TEST_CLIENT;
const runnerPath = join(dirname(clientPath), '..', 'runtime', 'node', 'candidate_runner.mjs');

export function call(exportName, args) {
	const result = spawnSync(process.execPath, [runnerPath], {
		cwd: process.env.NODE_CANDIDATE_SITE,
		input: JSON.stringify({package: packageName, export: exportName, args}),
		encoding: 'utf8',
		timeout: 10_000,
		maxBuffer: 256 * 1024,
	});
	if (result.error) {
		throw result.error;
	}
	const line = result.stdout.trim().split(/\r?\n/).at(-1);
	return JSON.parse(line);
}
