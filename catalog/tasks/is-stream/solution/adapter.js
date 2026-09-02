import {
	Duplex,
	PassThrough,
	Readable,
	Stream,
	Transform,
	Writable,
} from 'node:stream';
import {
	isDuplexStream,
	isReadableStream,
	isStream,
	isTransformStream,
	isWritableStream,
} from './index.js';

const predicates = {
	stream: isStream,
	writable: isWritableStream,
	readable: isReadableStream,
	duplex: isDuplexStream,
	transform: isTransformStream,
};
const methods = new Set(['pipe', 'read', 'write', 'end', 'destroy', '_transform']);

function createNative(type) {
	switch (type) {
		case 'stream': return new Stream();
		case 'readable': return new Readable({read() {}});
		case 'writable': return new Writable({write(chunk, encoding, callback) { callback(); }});
		case 'duplex': return new Duplex({read() {}, write(chunk, encoding, callback) { callback(); }});
		case 'transform': return new Transform({transform(chunk, encoding, callback) { callback(null, chunk); }});
		case 'passThrough': return new PassThrough();
		default: throw new Error(`unsupported native type: ${type}`);
	}
}

function createValue(descriptor) {
	if (!descriptor || typeof descriptor !== 'object' || Array.isArray(descriptor)) {
		throw new Error('value descriptor must be an object');
	}

	if (descriptor.kind === 'primitive') {
		if (descriptor.value !== null && !['boolean', 'number', 'string'].includes(typeof descriptor.value)) {
			throw new Error('unsupported primitive value');
		}
		return descriptor.value;
	}

	if (descriptor.kind === 'native') {
		if (descriptor.destroyed !== undefined && typeof descriptor.destroyed !== 'boolean') {
			throw new Error('destroyed must be boolean');
		}
		const value = createNative(descriptor.type);
		if (descriptor.destroyed) value.destroy();
		return value;
	}

	if (descriptor.kind === 'shape') {
		const allowed = new Set(['kind', 'methods', 'readable', 'writable', 'readableObjectMode', 'writableObjectMode', 'destroyed']);
		if (Object.keys(descriptor).some(key => !allowed.has(key))) {
			throw new Error('unsupported shape property');
		}
		const value = {};
		for (const field of ['readable', 'writable', 'readableObjectMode', 'writableObjectMode', 'destroyed']) {
			if (descriptor[field] !== undefined) {
				if (typeof descriptor[field] !== 'boolean') throw new Error(`${field} must be boolean`);
				value[field] = descriptor[field];
			}
		}
		if (descriptor.methods !== undefined && !Array.isArray(descriptor.methods)) {
			throw new Error('methods must be an array');
		}
		for (const method of descriptor.methods ?? []) {
			if (!methods.has(method)) throw new Error(`unsupported method: ${method}`);
			value[method] = () => {};
		}
		return value;
	}

	throw new Error(`unsupported descriptor kind: ${descriptor.kind}`);
}

export async function run(request) {
	if (!request || typeof request !== 'object' || Array.isArray(request)) {
		throw new Error('request must be an object');
	}
	if (request.op === 'version') return {version: '4.0.1'};
	if (request.op !== 'check') throw new Error(`unsupported operation: ${request.op}`);
	if (!(request.predicate in predicates)) throw new Error(`unsupported predicate: ${request.predicate}`);
	if (request.checkOpen !== undefined && typeof request.checkOpen !== 'boolean') {
		throw new Error('checkOpen must be boolean');
	}
	const value = createValue(request.value);
	return predicates[request.predicate](
		value,
		request.checkOpen === undefined ? undefined : {checkOpen: request.checkOpen},
	);
}
