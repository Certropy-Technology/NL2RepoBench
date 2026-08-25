import {chmodSync, copyFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = '/tmp/nl2repobench-cookie-adapter.mjs';
const ADAPTER_SOURCE = new URL('./adapter-source.js.txt', import.meta.url);
const METHODS = new Set([
	'parseCookie',
	'parseSetCookie',
	'stringifyCookie',
	'stringifySetCookie',
]);

copyFileSync(ADAPTER_SOURCE, ADAPTER);
chmodSync(ADAPTER, 0o555);

function request(payload) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const encoded = JSON.stringify(payload);
	if (Buffer.byteLength(encoded) > 64 * 1024) throw new Error('request exceeds the bound');
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM',
		'--kill-after=5s',
		'30s',
		'runuser',
		'-u',
		'candidate',
		'--',
		'/usr/bin/prlimit',
		'--cpu=30',
		'--nproc=32',
		'--nofile=128',
		'--',
		'env',
		'-i',
		'PATH=/usr/local/bin:/usr/bin:/bin',
		`HOME=${site}/home`,
		`TMPDIR=${site}/tmp`,
		'LC_ALL=C.UTF-8',
		NODE,
		'--no-addons',
		ADAPTER,
	], {
		cwd: site,
		input: `${encoded}\n`,
		encoding: 'utf8',
		maxBuffer: 256 * 1024,
		timeout: 35_000,
	});
	if (result.error || !result.stdout) throw new Error('candidate child failed');
	let response;
	try {
		response = JSON.parse(result.stdout);
	} catch {
		throw new Error('candidate child returned malformed JSON');
	}
	return response;
}

export const inventory = () => request({operation: 'inventory'});

export function invoke(method, args) {
	if (!METHODS.has(method) || !Array.isArray(args) || args.length > 2) {
		throw new Error('candidate call is not allowlisted');
	}
	return request({operation: 'call', method, args});
}

export function call(method, args) {
	const response = invoke(method, args);
	if (!response.ok) throw new Error(response.message ?? response.error ?? 'candidate call failed');
	return response.value;
}
