import {chmodSync, copyFileSync} from 'node:fs';
import {spawnSync} from 'node:child_process';

const NODE = '/usr/local/bin/node';
const ADAPTER = '/tmp/nl2repobench-p-retry-adapter.mjs';
const ADAPTER_SOURCE = new URL('./adapter-source.js.txt', import.meta.url);

copyFileSync(ADAPTER_SOURCE, ADAPTER);
chmodSync(ADAPTER, 0o555);

export function scenario(operation, payload = {}) {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) {
		throw new Error('candidate site is not configured');
	}

	const encoded = JSON.stringify({operation, ...payload});
	if (Buffer.byteLength(encoded) > 32 * 1024) {
		throw new Error('request exceeds the bound');
	}

	const result = spawnSync('/usr/bin/timeout', [
		'--signal=TERM',
		'--kill-after=3s',
		'12s',
		'runuser',
		'-u',
		'candidate',
		'--',
		'/usr/bin/prlimit',
		'--cpu=12',
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
		timeout: 15_000,
	});

	if (result.error || !result.stdout) {
		throw new Error('candidate child failed');
	}

	let response;
	try {
		response = JSON.parse(result.stdout);
	} catch {
		throw new Error('candidate child returned malformed JSON');
	}

	if (!response?.ok) {
		throw new Error(response?.message ?? 'candidate call failed');
	}

	return response.value;
}
