import {chmodSync, copyFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = '/tmp/nl2repobench-p-queue-adapter.mjs';
const ADAPTER_SOURCE = new URL('./adapter-source.js.txt', import.meta.url);
const OPERATIONS = new Set([
	'inventory', 'construct', 'schedule', 'add-all', 'clear-paused',
	'clear-running', 'waiters', 'abort-queued', 'abort-running', 'rate-limit',
	'priority-queue', 'validation', 'timeout-error',
]);

copyFileSync(ADAPTER_SOURCE, ADAPTER);
chmodSync(ADAPTER, 0o555);

export function call(operation, payload = {}) {
	if (!OPERATIONS.has(operation)) throw new Error('candidate operation is not allowlisted');
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) throw new Error('candidate site is not configured');
	const encoded = JSON.stringify({operation, payload});
	if (Buffer.byteLength(encoded) > 64 * 1024) throw new Error('request exceeds the bound');
	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM',
		'--kill-after=5s',
		'45s',
		'runuser',
		'-u',
		'candidate',
		'--',
		'/usr/bin/prlimit',
		'--cpu=40',
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
		timeout: 50_000,
	});
	if (result.error || !result.stdout) throw new Error('candidate child failed');
	let response;
	try {
		response = JSON.parse(result.stdout);
	} catch {
		throw new Error('candidate child returned malformed JSON');
	}
	if (!response?.ok) throw new Error(response?.message ?? 'candidate call failed');
	return response.value;
}
