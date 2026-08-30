import assert from 'node:assert/strict';
import test from 'node:test';
import {STYLE_NAMES, metadata} from './test_client.mjs';

test('package metadata and ESM export surfaces are exact', () => {
	const value = metadata();
	assert.deepEqual(value.manifest, {
		name: 'yoctocolors',
		version: '2.2.0',
		type: 'module',
		exports: {types: './index.d.ts', default: './index.js'},
		sideEffects: false,
		engines: {node: '>=18'},
		files: ['index.js', 'index.d.ts', 'base.js', 'base.d.ts'],
		dependencies: {},
	});
	assert.deepEqual(value.namedExports, [...STYLE_NAMES, 'default'].sort());
	assert.deepEqual(value.defaultExports, [...STYLE_NAMES].sort());
});

test('TypeScript declarations expose the complete string formatter surface', () => {
	const value = metadata();
	assert.equal(value.hasFormatType, true);
	assert.deepEqual(value.declaredFormats, [...STYLE_NAMES].sort());
	assert.match(value.indexDeclaration, /export \* from ['"]\.\/base\.js['"];?/);
	assert.match(value.indexDeclaration, /export \* as default from ['"]\.\/base\.js['"];?/);
});
