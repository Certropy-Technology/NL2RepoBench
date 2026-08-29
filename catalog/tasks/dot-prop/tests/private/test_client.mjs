import {chmodSync, readFileSync, writeFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = process.env.NODE_EXECUTABLE ?? '/usr/local/bin/node';
const ADAPTER_SOURCE = process.env.NODE_ADAPTER_SOURCE ?? '/tests/private/adapter-source.js.txt';
const ADAPTER = '/tmp/dot-prop-candidate-adapter.mjs';
let sequence = 0;
let ready = false;

function ensureAdapter() {
	if (ready) return;
	const source = readFileSync(ADAPTER_SOURCE);
	try {
		writeFileSync(ADAPTER, source, {flag: 'wx', mode: 0o555});
	} catch (error) {
		if (error?.code !== 'EEXIST') throw error;
	}
	chmodSync(ADAPTER, 0o555);
	ready = true;
}

function request(operation, payload) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	ensureAdapter();
	const id = `request-${++sequence}`;
	const input = JSON.stringify({id, operation, payload});
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--',
		'/usr/bin/prlimit', '--cpu=30', '--nproc=32', '--nofile=128', '--',
		'env', '-i', 'PATH=/usr/local/bin:/usr/bin:/bin', `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
		'LC_ALL=C.UTF-8', `NODE_CANDIDATE_SITE=${site}`, 'NODE_ALLOWED_PACKAGE=dot-prop', `NODE_ADAPTER_SOURCE=${ADAPTER_SOURCE}`, NODE, '--no-addons', ADAPTER,
	], {cwd: site, input, encoding: 'utf8', maxBuffer: 256 * 1024, timeout: 35_000});
	if (result.error || !result.stdout) throw new Error('candidate child failed');
	let response;
	try { response = JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
	if (response.id !== id) throw new Error('candidate response id mismatch');
	if (!response.ok) throw Object.assign(new Error(response.error?.message), {name: response.error?.name});
	return response.result;
}

export function invoke(name, args) {
	const result = request('invoke', {name, args});
	return result;
}

export function scenario(name) {
	return request('scenario', {name});
}

export function inventory() {
	return request('inventory', {});
}
