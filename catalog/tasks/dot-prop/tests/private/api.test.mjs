import assert from 'node:assert/strict';
import test from 'node:test';
import {invoke, inventory, scenario} from './test_client.mjs';

const result = (name, args) => invoke(name, args).returned;
const mutated = (name, args) => invoke(name, args).args[0];
const value = output => output?.__undefined ? undefined : output;

test('exports all documented runtime functions', () => {
	assert.deepEqual(inventory(), ['deepKeys', 'deleteProperty', 'escapePath', 'getProperty', 'hasProperty', 'parsePath', 'setProperty', 'stringifyPath', 'unflatten']);
});
test('gets nested values and preserves falsy values', () => {
	assert.equal(result('getProperty', [{foo: {bar: 0}}, 'foo.bar']), 0);
	assert.equal(result('getProperty', [{foo: {bar: false}}, 'foo.bar']), false);
});
test('gets defaults for missing and null intermediates', () => {
	assert.equal(result('getProperty', [{foo: {}}, 'foo.missing.deep', 'fallback']), 'fallback');
	assert.equal(result('getProperty', [{foo: null}, 'foo.bar', 'fallback']), 'fallback');
});
test('supports escaped literal keys', () => {
	assert.equal(result('getProperty', [{foo: {'a.b': 7}}, String.raw`foo.a\.b`]), 7);
});
test('supports bracket and dot array indexes', () => {
	const object = {users: [{name: 'Ada'}, {name: 'Linus'}]};
	assert.equal(result('getProperty', [object, 'users[0].name']), 'Ada');
	assert.equal(result('getProperty', [object, 'users.1.name']), 'Linus');
});
test('supports array path segments and numeric string normalization', () => {
	assert.equal(result('getProperty', [{items: ['x']}, ['items', '0']]), 'x');
});
test('handles non-object get inputs', () => {
	assert.equal(result('getProperty', [42, 'x']), 42);
	assert.equal(result('getProperty', ['text', 'x', 'fallback']), 'fallback');
});
test('sets nested object values and returns the object', () => {
	const object = {};
	const returned = invoke('setProperty', [object, 'user.name', 'Ada']);
	assert.deepEqual(returned.args[0], {user: {name: 'Ada'}});
	assert.deepEqual(returned.returned, {user: {name: 'Ada'}});
});
test('creates arrays for numeric next segments', () => {
	const object = {};
	assert.deepEqual(mutated('setProperty', [object, 'items.0.label', 'first']), {items: [{label: 'first'}]});
});
test('replaces primitive intermediates when setting', () => {
	assert.deepEqual(mutated('setProperty', [{foo: 1}, 'foo.bar', 2]), {foo: {bar: 2}});
});
test('ignores invalid or disallowed set paths', () => {
	const object = {};
	assert.deepEqual(mutated('setProperty', [object, '__proto__.polluted', true]), {});
	assert.deepEqual(mutated('setProperty', [object, [], true]), {});
});
test('deletes own properties with a boolean result', () => {
	const object = {foo: {bar: 1}};
	assert.equal(result('deleteProperty', [object, 'foo.bar']), true);
	assert.deepEqual(mutated('deleteProperty', [object, 'missing']), object);
});
test('deleting an array index leaves a hole and length', () => {
	const output = invoke('deleteProperty', [{items: ['a', 'b']}, 'items[0]']);
	assert.equal(output.returned, true);
	assert.equal(output.args[0].items.length, 2);
	assert.equal(output.args[0].items[0], null, 'JSON adapter represents a hole as null while preserving length');
});
test('hasProperty distinguishes holes from present values', () => {
	assert.equal(result('hasProperty', [{items: ['a']}, 'items.0']), true);
	assert.equal(result('hasProperty', [{items: ['a']}, 'items.2']), false);
});
test('has and get include inherited properties but delete does not', () => {
	assert.deepEqual(scenario('inherited'), {get: 42, has: true, deleted: false});
});
test('escapePath quotes dots brackets and slashes', () => {
	assert.equal(result('escapePath', ['foo.bar[0]']), String.raw`foo\.bar\[0]`);
});
test('parsePath handles basic and numeric paths', () => {
	assert.deepEqual(result('parsePath', ['foo.0.bar']), ['foo', 0, 'bar']);
	assert.deepEqual(result('parsePath', ['foo[2]']), ['foo', 2]);
});
test('parsePath handles escaping and empty segments', () => {
	assert.deepEqual(result('parsePath', [String.raw`foo\.bar`]), ['foo.bar']);
	assert.deepEqual(result('parsePath', ['..']), ['', '', '']);
});
test('parsePath treats empty brackets as literal text', () => {
	assert.deepEqual(result('parsePath', ['foo[]']), ['foo[]']);
	assert.deepEqual(result('parsePath', ['foo.[0]']), ['foo', '', 0]);
});
test('parsePath rejects malformed indexes', () => {
	assert.throws(() => invoke('parsePath', ['foo[bar]']), /Invalid character/);
});
test('stringifyPath emits canonical bracket paths', () => {
	assert.equal(result('stringifyPath', [['foo', 0, 'bar']]), 'foo[0].bar');
	assert.equal(result('stringifyPath', [[0, 1]]), '[0][1]');
});
test('stringifyPath can prefer dot indexes', () => {
	assert.equal(result('stringifyPath', [['foo', 0, 'bar'], {preferDotForIndices: true}]), 'foo.0.bar');
});
test('stringifyPath escapes string segments and preserves leading zeros', () => {
	assert.equal(result('stringifyPath', [['foo.bar', '01']]), String.raw`foo\.bar.01`);
});
test('numeric path rules keep leading-zero keys as strings', () => {
	assert.deepEqual(mutated('setProperty', [{}, 'items.01', 'value']), {items: {'01': 'value'}});
});
test('stringifyPath validates its input', () => {
	assert.throws(() => invoke('stringifyPath', [['foo', null]]), /Expected a string or number/);
});
test('deepKeys lists leaves in insertion order', () => {
	assert.deepEqual(result('deepKeys', [{a: {b: 1, c: 2}, empty: []}]), ['a.b', 'a.c', 'empty']);
});
test('deepKeys includes empty containers but not non-empty containers', () => {
	assert.deepEqual(result('deepKeys', [{a: {}, b: [], c: {d: {}}}]), ['a', 'b', 'c.d']);
});
test('deepKeys skips sparse array holes', () => {
	assert.deepEqual(scenario('sparse'), ['sparse[0]', 'sparse[2]']);
});
test('deepKeys traverses function-valued objects', () => {
	assert.deepEqual(scenario('function'), ['a.prop']);
});
test('deepKeys terminates on cyclic references', () => {
	assert.deepEqual(scenario('cyclic'), []);
});
test('unflatten creates nested objects and arrays', () => {
	assert.deepEqual(result('unflatten', [{'user.name': 'Ada', 'items[0]': 'x'}]), {user: {name: 'Ada'}, items: ['x']});
});
test('unflatten supports escaped keys and last-write conflicts', () => {
	assert.deepEqual(result('unflatten', [{a: 1, 'a.b': 2, [String.raw`a\.c`]: 3}]), {a: {b: 2}, 'a.c': 3});
});
test('unflatten drops prototype-related paths', () => {
	const output = result('unflatten', [{ '__proto__.polluted': true, valid: 1 }]);
	assert.deepEqual(output, {valid: 1});
});
test('unflatten returns a fresh empty object for non-objects', () => {
	assert.deepEqual(result('unflatten', [null]), {});
});
test('undefined values remain present for hasProperty', () => {
	assert.deepEqual(scenario('undefined'), {has: true, get: {__undefined: true}});
});
test('parse and stringify round-trip representative paths', () => {
	const parsed = result('parsePath', [String.raw`foo\.bar[0].name`]);
	const stringified = result('stringifyPath', [parsed]);
	assert.deepEqual(result('parsePath', [stringified]), parsed);
});
