import assert from 'node:assert/strict';
import path from 'node:path';
import {test} from 'node:test';
import {inspect, invoke} from './test_client.mjs';

const delimiter = path.delimiter;
const localParts = cwd => {
	const parts = [];
	let current = path.resolve(cwd);
	while (true) {
		parts.push(path.join(current, 'node_modules/.bin'));
		const parent = path.dirname(current);
		if (parent === current) {
			return parts;
		}

		current = parent;
	}
};

const ok = (exportName, options) => {
	const response = invoke(exportName, options);
	assert.equal(response.ok, true, `${response.error}: ${response.message ?? ''}`);
	return response;
};

const value = (exportName, options) => ok(exportName, options).value;
const expectTypeError = (exportName, options) => {
	const response = invoke(exportName, options);
	assert.equal(response.ok, false);
	assert.equal(response.exception_type, 'TypeError');
};

test('package metadata and root exports match the contract', () => {
	const response = inspect();
	assert.equal(response.ok, true, response.error);
	assert.equal(response.value.name, 'npm-run-path');
	assert.equal(response.value.version, '6.0.0');
	assert.equal(response.value.type, 'module');
	assert.deepEqual(response.value.module_exports, ['npmRunPath', 'npmRunPathEnv']);
	assert.equal(response.value.declaration_exists, true);
});

test('npmRunPath prepends every local binary directory and the executable directory', () => {
	const cwd = '/work/project/app';
	assert.equal(
		value('npmRunPath', {cwd, path: '/usr/bin:/bin', execPath: '/usr/local/bin/node'}),
		[...localParts(cwd), '/usr/local/bin', '/usr/bin', '/bin'].join(delimiter),
	);
});

test('preferLocal false omits local binary directories', () => {
	assert.equal(
		value('npmRunPath', {cwd: '/work/app', path: '/bin', execPath: '/opt/node/bin/node', preferLocal: false}),
		'/opt/node/bin:/bin',
	);
});

test('addExecPath false omits the executable directory', () => {
	const cwd = '/work/app';
	assert.equal(
		value('npmRunPath', {cwd, path: '/bin', execPath: '/opt/node/bin/node', addExecPath: false}),
		[...localParts(cwd), '/bin'].join(delimiter),
	);
});

test('both switches false preserve a non-empty supplied PATH', () => {
	assert.equal(value('npmRunPath', {path: '/a:/b', preferLocal: false, addExecPath: false}), '/a:/b');
});

test('both switches false preserve an empty supplied PATH', () => {
	assert.equal(value('npmRunPath', {path: '', preferLocal: false, addExecPath: false}), '');
});

test('empty PATH receives prefixes without a trailing delimiter', () => {
	const result = value('npmRunPath', {cwd: '/a/b', path: '', execPath: '/node/bin/node'});
	assert.equal(result, [...localParts('/a/b'), '/node/bin'].join(delimiter));
});

test('delimiter-only PATH preserves one trailing delimiter', () => {
	const result = value('npmRunPath', {cwd: '/a', path: delimiter, execPath: '/node/bin/node'});
	assert.equal(result, `${[...localParts('/a'), '/node/bin'].join(delimiter)}${delimiter}`);
	assert.equal(result.includes(`${delimiter}${delimiter}`), false);
});

test('PATH beginning with a delimiter keeps the empty leading segment', () => {
	const result = value('npmRunPath', {cwd: '/a', path: `${delimiter}tail`, execPath: '/node/bin/node'});
	assert.equal(result.includes(`${delimiter}${delimiter}tail`), true);
});

test('PATH ending with a delimiter remains delimiter-terminated', () => {
	const result = value('npmRunPath', {cwd: '/a', path: `head${delimiter}`, execPath: '/node/bin/node'});
	assert.equal(result.endsWith(delimiter), true);
	assert.equal(result.includes(`${delimiter}${delimiter}`), false);
});

test('an existing local binary directory is not duplicated', () => {
	const cwd = '/work/app';
	const local = path.join(cwd, 'node_modules/.bin');
	const result = value('npmRunPath', {cwd, path: `${local}:/bin`, execPath: '/node/bin/node'});
	assert.equal(result.split(delimiter).filter(part => part === local).length, 1);
});

test('an existing executable directory is not duplicated', () => {
	const result = value('npmRunPath', {cwd: '/work/app', path: '/node/bin:/bin', execPath: '/node/bin/node'});
	assert.equal(result.split(delimiter).filter(part => part === '/node/bin').length, 1);
});

test('a relative execPath is resolved against cwd', () => {
	const result = value('npmRunPath', {cwd: '/work/app', path: '', execPath: 'runtime/node', preferLocal: false});
	assert.equal(result, '/work/app/runtime');
});

test('cwd accepts a file URL', () => {
	const result = value('npmRunPath', {cwdUrl: 'file:///url/project/app/', path: '', execPath: '/node/bin/node', addExecPath: false});
	assert.equal(result, localParts('/url/project/app').join(delimiter));
});

test('execPath accepts a file URL', () => {
	const result = value('npmRunPath', {cwd: '/work/app', path: '', execPathUrl: 'file:///opt/runtime/node', preferLocal: false});
	assert.equal(result, '/opt/runtime');
});

test('default options use the child cwd, executable, and process PATH', () => {
	const result = value('npmRunPath');
	assert.equal(result.startsWith(`${process.env.NODE_CANDIDATE_SITE}/node_modules/.bin:`), true);
	assert.equal(result.includes('/usr/local/bin'), true);
	assert.equal(result.endsWith('/usr/local/bin:/usr/bin:/bin'), true);
});

test('nested local directories are ordered nearest first', () => {
	const result = value('npmRunPath', {cwd: '/one/two/three', path: '', execPath: '/node/bin/node'}).split(delimiter);
	assert.deepEqual(result.slice(0, 3), [
		'/one/two/three/node_modules/.bin',
		'/one/two/node_modules/.bin',
		'/one/node_modules/.bin',
	]);
});

test('npmRunPath does not mutate its options object', () => {
	const response = ok('npmRunPath', {cwd: '/work/app', path: '/bin', execPath: '/node/bin/node'});
	assert.equal(response.input_unchanged, true);
});

test('npmRunPathEnv returns a cloned environment with augmented PATH', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/bin', KEEP: 'yes'}, cwd: '/work/app', execPath: '/node/bin/node'});
	assert.equal(environment.KEEP, 'yes');
	assert.equal(environment.PATH, [...localParts('/work/app'), '/node/bin', '/bin'].join(delimiter));
});

test('npmRunPathEnv does not mutate its options or input environment', () => {
	const response = ok('npmRunPathEnv', {env: {PATH: '/bin', KEEP: 'yes'}, cwd: '/work/app'});
	assert.equal(response.input_unchanged, true);
});

test('npmRunPathEnv preferLocal false still adds execPath', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/bin'}, cwd: '/work/app', execPath: '/node/bin/node', preferLocal: false});
	assert.equal(environment.PATH, '/node/bin:/bin');
});

test('npmRunPathEnv addExecPath false still adds local directories', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/bin'}, cwd: '/work/app', execPath: '/node/bin/node', addExecPath: false});
	assert.equal(environment.PATH, [...localParts('/work/app'), '/bin'].join(delimiter));
});

test('npmRunPathEnv with both switches false preserves PATH', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/custom'}, preferLocal: false, addExecPath: false});
	assert.equal(environment.PATH, '/custom');
});

test('npmRunPathEnv supports an empty PATH', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: ''}, preferLocal: false, addExecPath: false});
	assert.equal(environment.PATH, '');
});

test('npmRunPathEnv preserves unrelated string variables', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/bin', A: '1', B: 'two'}, preferLocal: false, addExecPath: false});
	assert.deepEqual(environment, {PATH: '/bin', A: '1', B: 'two'});
});

test('npmRunPathEnv accepts URL cwd and execPath options', () => {
	const environment = value('npmRunPathEnv', {
		env: {PATH: '/bin'},
		cwdUrl: 'file:///url/app/',
		execPathUrl: 'file:///runtime/bin/node',
	});
	assert.equal(environment.PATH, [...localParts('/url/app'), '/runtime/bin', '/bin'].join(delimiter));
});

test('npmRunPathEnv resolves relative execPath against cwd', () => {
	const environment = value('npmRunPathEnv', {env: {PATH: '/bin'}, cwd: '/work/app', execPath: 'runtime/node', preferLocal: false});
	assert.equal(environment.PATH, '/work/app/runtime:/bin');
});

test('npmRunPathEnv chooses PATH on Linux and preserves other casing', () => {
	const environment = value('npmRunPathEnv', {env: {Path: '/windows-style'}, preferLocal: false, addExecPath: false});
	assert.equal(environment.Path, '/windows-style');
	assert.equal(environment.PATH, '/usr/local/bin:/usr/bin:/bin');
});

test('null path reports the native TypeError', () => {
	expectTypeError('npmRunPath', {path: null});
});

test('non-path cwd reports the native TypeError', () => {
	expectTypeError('npmRunPath', {cwd: false, path: ''});
});

test('non-path execPath reports the native TypeError', () => {
	expectTypeError('npmRunPath', {execPath: false, path: '', preferLocal: false});
});

test('null options report the native TypeError', () => {
	expectTypeError('npmRunPath', null);
});

test('repeated calls are deterministic', () => {
	const options = {cwd: '/repeat/app', path: '/bin', execPath: '/node/bin/node'};
	const results = Array.from({length: 4}, () => value('npmRunPath', options));
	assert.deepEqual(results, Array(4).fill(results[0]));
});
