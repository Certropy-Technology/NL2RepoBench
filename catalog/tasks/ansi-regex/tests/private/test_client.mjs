import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;

function emit(payload, code = 0) {
	const encoded = JSON.stringify(payload);
	if (Buffer.byteLength(encoded) > MAX_RESPONSE_BYTES) {
		process.stderr.write('candidate response exceeds bound\n');
		process.exit(70);
	}
	process.stdout.write(`${encoded}\n`);
	process.exit(code);
}

const data = readFileSync(0);
if (data.byteLength > MAX_REQUEST_BYTES) {
	emit({ok: false, error: 'request-too-large'}, 64);
}

let request;
try {
	request = JSON.parse(data.toString('utf8'));
} catch {
	emit({ok: false, error: 'malformed-json'}, 64);
}

if (!request || typeof request !== 'object' || Array.isArray(request)) {
	emit({ok: false, error: 'request-must-be-object'}, 64);
}

try {
	const site = process.env.NODE_CANDIDATE_SITE;
	if (!site) {
		throw new Error('candidate site missing');
	}
	const packageRoot = join(site, 'node_modules', 'ansi-regex');
	const packageJson = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
	const entry = typeof packageJson.exports === 'string' ? packageJson.exports : undefined;
	if (!entry || !entry.startsWith('./') || entry.includes('..')) {
		throw new Error('candidate has no safe root export');
	}
	const module = await import(pathToFileURL(join(packageRoot, entry)).href);
	if (typeof module.default !== 'function') {
		throw new TypeError('default export is not callable');
	}

	if (request.operation === 'inspect') {
		emit({
			ok: true,
			value: {
				name: packageJson.name,
				version: packageJson.version,
				type: packageJson.type,
				exports: packageJson.exports,
				types: packageJson.types,
				callable: true,
			},
		});
	}

	if (request.operation !== 'match' && request.operation !== 'test') {
		emit({ok: false, error: 'operation-not-allowlisted'}, 64);
	}
	if (typeof request.input !== 'string') {
		emit({ok: false, error: 'input-must-be-string'}, 64);
	}
	if (request.onlyFirst !== undefined && typeof request.onlyFirst !== 'boolean') {
		emit({ok: false, error: 'onlyFirst-must-be-boolean'}, 64);
	}

	const options = request.onlyFirst === undefined ? undefined : {onlyFirst: request.onlyFirst};
	const regex = module.default(options);
	if (!(regex instanceof RegExp)) {
		throw new TypeError('default export did not return RegExp');
	}
	if (request.operation === 'test') {
		emit({ok: true, value: {source: regex.source, flags: regex.flags, result: regex.test(request.input)}});
	}
	const matches = request.input.match(regex);
	emit({ok: true, value: {source: regex.source, flags: regex.flags, matches: matches ? [...matches] : []}});
} catch (error) {
	emit({
		ok: false,
		error: 'candidate-call-failed',
		exception_type: error?.constructor?.name ?? 'Error',
		message: String(error?.message ?? error),
	}, 1);
}
