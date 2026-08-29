import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';

const manifest = JSON.parse(readFileSync(
	join(process.env.NODE_CANDIDATE_SITE, 'node_modules', 'get-east-asian-width', 'package.json'),
	'utf8',
));

test('package identity and ESM entry are published', () => {
	assert.equal(manifest.name, 'get-east-asian-width');
	assert.equal(manifest.version, '1.6.0');
	assert.equal(manifest.type, 'module');
	assert.equal(manifest.exports.default, './index.js');
	assert.equal(manifest.exports.types, './index.d.ts');
});

test('published runtime files are present', () => {
	const packageRoot = join(process.env.NODE_CANDIDATE_SITE, 'node_modules', 'get-east-asian-width');
	assert.equal(manifest.files.includes('index.js'), true);
	assert.equal(manifest.files.includes('lookup.js'), true);
	assert.equal(manifest.files.includes('lookup-data.js'), true);
	assert.equal(manifest.files.includes('utilities.js'), true);
	assert.equal(manifest.files.includes('index.d.ts'), true);
	assert.equal(readFileSync(join(packageRoot, 'index.d.ts'), 'utf8').includes('eastAsianWidth'), true);
});
