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
	const packageRoot = join(site, 'node_modules', 'strip-final-newline');
	const packageJson = JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8'));
	const entry = packageJson.exports?.default;
	if (typeof entry !== 'string' || !entry.startsWith('./') || entry.includes('..')) {
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
				callable: true,
			},
		});
	}

	if (request.operation === 'string') {
		if (typeof request.input !== 'string') {
			emit({ok: false, error: 'input-must-be-string'}, 64);
		}
		const value = module.default(request.input);
		emit({ok: true, value: {type: typeof value, value}});
	}

	if (request.operation === 'bytes') {
		if (!Array.isArray(request.bytes) || request.bytes.some(byte => !Number.isInteger(byte) || byte < 0 || byte > 255)) {
			emit({ok: false, error: 'bytes-must-be-array'}, 64);
		}
		const buffer = Uint8Array.from(request.bytes);
		const offset = request.offset ?? 0;
		const length = request.length ?? buffer.byteLength - offset;
		const input = new Uint8Array(buffer.buffer, offset, length);
		const result = module.default(input);
		emit({
			ok: true,
			value: {
				bytes: [...result],
				inputBytes: [...input],
				type: result.constructor.name,
				sameObject: result === input,
				sameBuffer: result.buffer === input.buffer,
				byteOffset: result.byteOffset,
				byteLength: result.byteLength,
			},
		});
	}

	if (request.operation === 'invalid') {
		const inputs = {
			boolean: true,
			null: null,
			object: {},
			dataView: new DataView(new ArrayBuffer(0)),
			uint16: new Uint16Array(new ArrayBuffer(2)),
		};
		try {
			module.default(inputs[request.kind]);
			emit({ok: true, value: {threw: false}});
		} catch (error) {
			emit({ok: true, value: {threw: true, name: error?.constructor?.name ?? 'Error', message: String(error?.message ?? error)}});
		}
	}

	emit({ok: false, error: 'operation-not-allowlisted'}, 64);
} catch (error) {
	emit({
		ok: false,
		error: 'candidate-call-failed',
		exceptionType: error?.constructor?.name ?? 'Error',
		message: String(error?.message ?? error),
	}, 1);
}
