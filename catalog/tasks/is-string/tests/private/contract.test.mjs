import assert from 'node:assert/strict';
import {test} from 'node:test';
import {inventory, value} from './test_client.mjs';

test('package-inventory', () => {
  assert.deepEqual(inventory(), {
    packageName: 'is-string',
    packageVersion: '1.1.1',
    main: 'index.js',
    types: 'index.d.ts',
    callable: true,
    functionName: 'isString',
  });
});

test('undefined', () => assert.equal(value('undefined'), false));
test('null', () => assert.equal(value('null'), false));
test('boolean', () => assert.equal(value('boolean'), false));
test('number', () => assert.equal(value('number'), false));
test('nan', () => assert.equal(value('nan'), false));
test('infinity', () => assert.equal(value('infinity'), false));
test('bigint', () => assert.equal(value('bigint'), false));
test('symbol', () => assert.equal(value('symbol'), false));
test('function', () => assert.equal(value('function'), false));
test('primitive-empty', () => assert.equal(value('string', {value: ''}), true));
test('primitive-unicode', () => assert.equal(value('string', {value: 'Straße 日本語'}), true));
test('primitive-long', () => assert.equal(value('string', {value: 'x'.repeat(2048)}), true));
test('boxed-empty', () => assert.equal(value('string-object', {value: ''}), true));
test('boxed-unicode', () => assert.equal(value('string-object', {value: '💡'}), true));
test('boxed-altered-tag', () => assert.equal(value('boxed-altered-tag'), true));
test('boxed-cross-realm', () => assert.equal(value('cross-realm-string'), true));
test('boxed-number', () => assert.equal(value('number-object'), false));
test('boxed-boolean', () => assert.equal(value('boolean-object'), false));
test('array', () => assert.equal(value('array', {value: [1, 2]}), false));
test('regexp', () => assert.equal(value('regexp'), false));
test('date', () => assert.equal(value('date'), false));
test('ordinary-object', () => assert.equal(value('object', {value: {answer: 42}}), false));
test('fake-tag', () => assert.equal(value('fake-tag'), false));
test('throwing-tag-getter', () => assert.equal(value('throwing-tag-getter'), false));
test('conversion-methods', () => assert.deepEqual(value('conversion-methods'), {result: false, accessed: 0}));
test('throwing-conversion-methods', () => assert.equal(value('throwing-conversion-methods'), false));
test('prototype-shaped-object', () => assert.equal(value('prototype-shaped-object'), false));
