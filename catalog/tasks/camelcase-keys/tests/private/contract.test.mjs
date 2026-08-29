import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate, inventory} from './test_client.mjs';

test('package shape is a pinned ESM default export', () => {
  assert.deepEqual(inventory(), {
    packageName: 'camelcase-keys',
    packageVersion: '10.0.2',
    moduleType: 'module',
    exportMap: {types: './index.d.ts', default: './index.js'},
    exportNames: ['default'],
    callableDefault: true,
  });
});

test('converts common separators', () => {
  assert.deepEqual(callCandidate({'foo-bar': 1, 'hello_world': 2, 'two words': 3}), {
    fooBar: 1, helloWorld: 2, twoWords: 3,
  });
});

test('preserves property insertion order', () => {
  assert.deepEqual(Object.keys(callCandidate({'z-key': 1, 'a-key': 2, 'm-key': 3})), ['zKey', 'aKey', 'mKey']);
});

test('returns primitive inputs unchanged', () => {
  assert.equal(callCandidate(null), null);
  assert.equal(callCandidate(false), false);
  assert.equal(callCandidate(42), 42);
  assert.equal(callCandidate('plain text'), 'plain text');
});

test('converts top-level arrays of objects', () => {
  assert.deepEqual(callCandidate([{'foo-bar': true}, {'bar-baz': false}]), [{fooBar: true}, {barBaz: false}]);
});

test('leaves non-object array elements unchanged', () => {
  assert.deepEqual(callCandidate([null, 'two words', 7, true]), [null, 'two words', 7, true]);
});

test('does not recurse by default', () => {
  assert.deepEqual(callCandidate({outer_key: {inner_key: 1}, list_items: [{item_name: 'x'}]}), {
    outerKey: {inner_key: 1}, listItems: [{item_name: 'x'}],
  });
});

test('deep converts nested objects', () => {
  assert.deepEqual(callCandidate({outer_key: {inner_key: 1}}, {deep: true}), {outerKey: {innerKey: 1}});
});

test('deep converts objects inside arrays', () => {
  assert.deepEqual(callCandidate({list_items: [{item_name: 'x'}, {item_name: 'y'}]}, {deep: true}), {
    listItems: [{itemName: 'x'}, {itemName: 'y'}],
  });
});

test('deep handles nested arrays', () => {
  assert.deepEqual(callCandidate({matrix_values: [[{cell_value: 1}]]}, {deep: true}), {
    matrixValues: [[{cellValue: 1}]],
  });
});

test('pascalCase capitalizes converted words', () => {
  assert.deepEqual(callCandidate({'foo-bar': 1, hello_world: 2}, {pascalCase: true}), {FooBar: 1, HelloWorld: 2});
});

test('preserveConsecutiveUppercase keeps uppercase runs', () => {
  assert.deepEqual(callCandidate({foo_BAR: 1, api_URL_value: 2}, {preserveConsecutiveUppercase: true}), {
    fooBAR: 1, apiURLValue: 2,
  });
});

test('uppercase runs normalize by default', () => {
  assert.deepEqual(callCandidate({foo_BAR: 1, api_URL_value: 2}), {fooBar: 1, apiUrlValue: 2});
});

test('exclude leaves matching keys unchanged', () => {
  assert.deepEqual(callCandidate({'foo-bar': 1, 'keep-key': 2}, {exclude: ['keep-key']}), {fooBar: 1, 'keep-key': 2});
});

test('exclude can be combined with deep conversion', () => {
  assert.deepEqual(callCandidate({outer_key: {keep_key: 1, change_key: 2}}, {deep: true, exclude: ['keep_key']}), {
    outerKey: {keep_key: 1, changeKey: 2},
  });
});

test('stopPaths stops recursion at an object path', () => {
  assert.deepEqual(callCandidate({outer_key: {inner_key: 1, other_key: 2}}, {deep: true, stopPaths: ['outer_key']}), {
    outerKey: {inner_key: 1, other_key: 2},
  });
});

test('stopPaths works through arrays without indices', () => {
  assert.deepEqual(callCandidate({items_list: [{meta_data: {raw_value: 1}}]}, {deep: true, stopPaths: ['items_list.meta_data']}), {
    itemsList: [{metaData: {raw_value: 1}}],
  });
});

test('preserves numeric-looking string keys', () => {
  assert.deepEqual(callCandidate({'42': 'integer', '4.2': 'float', '1e5': 'scientific'}), {
    '42': 'integer', '4.2': 'float', '1e5': 'scientific',
  });
});

test('transforms keys that only start with digits', () => {
  assert.deepEqual(callCandidate({'42-foo': 1, foo2bar: 2, a1b_text: 3}), {'42Foo': 1, foo2Bar: 2, a1bText: 3});
});

test('preserves leading underscores and dollar signs', () => {
  assert.deepEqual(callCandidate({_foo_bar: 1, $foo_bar: 2, __x_y: 3, $_mixed_key: 4}), {
    _fooBar: 1, $fooBar: 2, __xY: 3, $_mixedKey: 4,
  });
});

test('deep conversion preserves primitive values', () => {
  assert.deepEqual(callCandidate({null_value: null, false_value: false, zero_value: 0, text_value: 'x'}, {deep: true}), {
    nullValue: null, falseValue: false, zeroValue: 0, textValue: 'x',
  });
});

test('empty objects and arrays remain empty', () => {
  assert.deepEqual(callCandidate({empty_object: {}, empty_array: []}, {deep: true}), {emptyObject: {}, emptyArray: []});
});

test('repeated calls are deterministic', () => {
  const input = {user_profile: {first_name: 'Ada', tags_list: [{tag_name: 'math'}]}};
  const options = {deep: true, preserveConsecutiveUppercase: true};
  assert.deepEqual(callCandidate(input, options), callCandidate(input, options));
});

test('pascalCase and deep compose', () => {
  assert.deepEqual(callCandidate({user_profile: {first_name: 'Ada'}}, {deep: true, pascalCase: true}), {
    UserProfile: {FirstName: 'Ada'},
  });
});
