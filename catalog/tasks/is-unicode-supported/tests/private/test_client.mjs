import {spawnSync} from 'node:child_process';

const RUNNER = '/tests/runtime/node/candidate_runner.mjs';
const NODE = '/usr/local/bin/node';

export function callCandidate(state, args = []) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const adapter = String.raw`
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const site = process.env.NODE_CANDIDATE_SITE;
const state = JSON.parse(process.env.NL2REPO_UNICODE_STATE);
Object.defineProperty(process, 'platform', {value: state.platform});
for (const name of ['TERM', 'TERM_PROGRAM', 'WT_SESSION', 'TERMINUS_SUBLIME', 'ConEmuTask', 'TERMINAL_EMULATOR']) {
  delete process.env[name];
}
Object.assign(process.env, state.env ?? {});
const manifest = JSON.parse(readFileSync(join(site, 'node_modules/is-unicode-supported/package.json'), 'utf8'));
const entry = typeof manifest.exports === 'string' ? manifest.exports : manifest.exports?.default ?? manifest.main;
if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) throw new Error('unsafe package entry');
const module = await import(pathToFileURL(join(site, 'node_modules/is-unicode-supported', entry)).href);
const value = await module.default(...JSON.parse(process.env.NL2REPO_UNICODE_ARGS));
process.stdout.write(JSON.stringify({ok: true, value}) + '\n');
`;
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
		'/usr/bin/prlimit', '--cpu=60', '--nproc=32', '--nofile=128', '--',
		'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
		'NODE_CANDIDATE_SITE=' + site, `NL2REPO_UNICODE_STATE=${JSON.stringify(state)}`,
		`NL2REPO_UNICODE_ARGS=${JSON.stringify(args)}`, NODE, '--no-addons', '--input-type=module', '-e', adapter,
	], {
		cwd: site,
		encoding: 'utf8',
		maxBuffer: 256 * 1024,
		timeout: 35_000,
	});
	if (result.error) throw result.error;
	let payload;
	try {
		payload = JSON.parse(result.stdout);
	} catch {
		throw new Error(`candidate response malformed (status ${result.status}): ${(result.stderr ?? '').slice(0, 1024)} ${result.stdout}`);
	}
	if (!payload.ok) throw new Error(payload.error ?? payload.message ?? 'candidate-call-failed');
	return payload.value;
}
