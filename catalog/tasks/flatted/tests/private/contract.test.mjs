import assert from 'node:assert/strict';
import test from 'node:test';
import {call, inventory} from './test_client.mjs';

function ok(response) { assert.equal(response.ok, true, response.message); return response.value; }
function error(response) { assert.equal(response.ok, false); return response; }
const objectCycle = {root: {$ref: 0}, nodes: [{type: 'object', properties: {name: 'root', self: {$ref: 0}}}]};
const arrayCycle = {root: {$ref: 0}, nodes: [{type: 'array', items: [{$ref: 0}, 'x', {$ref: 0}]}]};
const shared = {root: {$ref: 0}, nodes: [{type: 'object', properties: {left: {$ref: 1}, right: {$ref: 1}}}, {type: 'object', properties: {value: 42}}]};

test('package root exposes the frozen dual module shape', () => {
  assert.deepEqual(ok(inventory()), {packageName: 'flatted', packageVersion: '3.4.4', packageShape: true,
    runtimeEntries: ['cjs/index.js', 'esm/index.js'], declarationEntry: true,
    exportNames: ['fromJSON', 'parse', 'stringify', 'toJSON']});
});
test('stringify null root', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'null'})), '[null]'));
test('stringify primitive roots', () => { assert.equal(ok(call('stringify', 'stringify', {fixture: 'number'})), '[42]'); assert.equal(ok(call('stringify', 'stringify', {fixture: 'string'})), '["hello"]'); });
test('stringify empty array', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'empty-array'})), '[[]]'));
test('stringify empty object', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'empty-object'})), '[{}]'));
test('stringify self-referencing object', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'cycle-object'})), '[{"name":"1","self":"0"},"root"]'));
test('stringify self-referencing array', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'cycle-array'})), '[["0","1","0"],"x"]'));
test('stringify shared object identity', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'shared-object'})), '[{"left":"1","right":"1"},{"value":42}]'));
test('stringify nested cyclic graph', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'nested-cycle'})), '[{"a":"1","list":"2"},{"value":"3","parent":"0"},["1","0"],"nested"]'));
test('stringify preserves index-like strings', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'index-strings'})), '[{"zero":"1","one":"2","nested":"3"},"0","1",{"zero":"1"}]'));
test('stringify function replacer omits a property', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'cycle-object', replacer: 'drop'})), '[{"name":"1","self":"0"},"root"]'));
test('stringify array replacer filters object keys', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'index-strings', replacer: 'array'})), '[{}]'));
test('stringify numeric indentation', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'shared-object', space: 2})), '[{\n  "left": "1",\n  "right": "1"\n},{\n  "value": 42\n}]'));
test('stringify string indentation is clamped', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'shared-object', space: 'abcdefghijklmnop'})), '[{\nabcdefghij"left": "1",\nabcdefghij"right": "1"\n},{\nabcdefghij"value": 42\n}]'));
test('stringify Date through toJSON', () => assert.equal(ok(call('stringify', 'stringify', {fixture: 'date'})), '["2020-01-02T03:04:05.000Z"]'));
test('parse primitive root', () => assert.equal(ok(call('parse', 'parse', {input: 'primitive'})).root, 1));
test('parse primitive string root', () => assert.equal(ok(call('parse', 'parse', {input: 'string'})).root, 'x'));
test('parse restores object cycle', () => assert.deepEqual(ok(call('parse', 'parse', {input: 'cycleObject'})), objectCycle));
test('parse restores array cycle', () => assert.deepEqual(ok(call('parse', 'parse', {input: 'cycleArray'})), arrayCycle));
test('parse restores shared identity', () => assert.deepEqual(ok(call('parse', 'parse', {input: 'shared'})), shared));
test('parse reviver transforms values', () => { const value = ok(call('parse', 'parse', {input: 'reviver', reviver: 'increment'})); assert.equal(value.nodes[0].properties.count, 2); });
test('parse reviver deletes properties', () => { const value = ok(call('parse', 'parse', {input: 'reviver', reviver: 'drop'})); assert.deepEqual(value.nodes[0].properties, {count: 1}); });
test('parse preserves special strings', () => { const value = ok(call('parse', 'parse', {input: 'special'})); assert.equal(value.nodes[0].properties.a, '~\\x7e'); assert.equal(value.nodes[0].properties.b, '\\x7e'); });
test('parse rejects malformed JSON', () => assert.equal(error(call('parse', 'parse', {input: 'bad'})).error_type, 'SyntaxError'));
test('toJSON returns an acyclic object cycle table', () => assert.deepEqual(ok(call('toJSON', 'toJSON', {fixture: 'cycle-object'})), [{name: '1', self: '0'}, 'root']));
test('toJSON returns a shared table', () => assert.deepEqual(ok(call('toJSON', 'toJSON', {fixture: 'shared-object'})), [{left: '1', right: '1'}, {value: 42}]));
test('fromJSON restores object cycle', () => assert.deepEqual(ok(call('fromJSON', 'fromJSON', {table: '[{"self":"0"}]'})), objectCycleFromSimple()));
test('fromJSON restores aliases', () => assert.deepEqual(ok(call('fromJSON', 'fromJSON', {table: '[{"a":"1","b":"1"},{"x":1}]'})), {root: {$ref: 0}, nodes: [{type: 'object', properties: {a: {$ref: 1}, b: {$ref: 1}}}, {type: 'object', properties: {x: 1}}]}));
test('roundtrip preserves object identity', () => assert.deepEqual(ok(call('parse', 'roundtrip', {fixture: 'cycle-object'})), objectCycle));
test('roundtrip preserves array identity', () => assert.deepEqual(ok(call('parse', 'roundtrip', {fixture: 'cycle-array'})), arrayCycle));
test('roundtrip preserves aliases', () => assert.deepEqual(ok(call('parse', 'roundtrip', {fixture: 'shared-object'})), shared));
test('helpers roundtrip preserves nested identity', () => { const value = ok(call('parse', 'helpersRoundtrip', {fixture: 'nested-cycle'})); assert.equal(value.nodes[0].properties.a.$ref, 1); assert.equal(value.nodes[1].properties.parent.$ref, 0); });
test('helpers roundtrip preserves primitive', () => assert.deepEqual(ok(call('parse', 'helpersRoundtrip', {fixture: 'string'})), {root: 'hello', nodes: []}));
test('stringify does not mutate cyclic input', () => { const value = ok(call('stringify', 'stringify', {fixture: 'cycle-object'})); assert.equal(value, '[{"name":"1","self":"0"},"root"]'); });
test('repeated calls are deterministic', () => { const first = ok(call('stringify', 'stringify', {fixture: 'nested-cycle'})); const second = ok(call('stringify', 'stringify', {fixture: 'nested-cycle'})); assert.equal(first, second); });

function objectCycleFromSimple() { return {root: {$ref: 0}, nodes: [{type: 'object', properties: {self: {$ref: 0}}}]}; }
