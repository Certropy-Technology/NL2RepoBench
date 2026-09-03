import assert from 'node:assert/strict';
import test from 'node:test';
import {callCandidate} from './test_client.mjs';

test('package identity and root export', () => {
  assert.deepEqual(callCandidate('package'), {
    name: 'mimic-function',
    version: '5.0.1',
    type: 'module',
    default: 'function',
    hasTypes: true,
  });
});

test('returns the destination function', () => assert.equal(callCandidate('return-value'), true));
test('copies name', () => assert.deepEqual(callCandidate('copy-name'), {before: 'wrapper', after: 'source'}));
test('copies other properties', () => assert.equal(callCandidate('copy-property'), 'unicorn'));
test('copies symbol properties', () => assert.equal(callCandidate('copy-symbol'), 'sparkles'));
test('does not copy length', () => assert.deepEqual(callCandidate('keep-length'), {source: 2, destination: 0}));
test('keeps property descriptors', () => assert.equal(callCandidate('descriptors'), true));
test('copies inherited properties', () => assert.equal(callCandidate('inherited'), true));
test('does not delete extra configurable properties', () => assert.equal(callCandidate('extra-property'), true));
test('does not copy function prototype objects', () => assert.equal(callCandidate('keep-prototype'), true));
test('supports class constructors', () => assert.deepEqual(callCandidate('classes'), {name: 'SourceClass', distinctPrototype: true}));
test('patches toString for ordinary functions', () => assert.equal(callCandidate('to-string'), true));
test('patches toString for arrow functions', () => assert.equal(callCandidate('to-string-arrow'), true));
test('patches toString for bound functions', () => assert.equal(callCandidate('to-string-bound'), true));
test('patches toString for Function constructor values', () => assert.equal(callCandidate('to-string-constructor'), true));
test('supports repeated wrapping', () => assert.equal(callCandidate('to-string-repeated'), true));
test('keeps toString non-enumerable', () => assert.equal(callCandidate('to-string-enumerable'), false));
test('does not change Function.prototype.toString output', () => assert.equal(callCandidate('native-to-string'), true));
test('supports String coercion', () => assert.equal(callCandidate('string-coercion'), true));
test('keeps toString.name', () => assert.equal(callCandidate('to-string-name'), 'toString'));
test('uses a patched source toString', () => assert.equal(callCandidate('patched-source-to-string'), true));
test('accepts identical non-configurable descriptors', () => assert.equal(callCandidate('nonconfig-same'), true));
test('accepts writable non-configurable value changes', () => assert.deepEqual(callCandidate('nonconfig-writable-value'), {threw: false, value: false}));
test('rejects non-writable non-configurable value changes', () => assert.equal(callCandidate('nonconfig-value-throw'), true));
test('can ignore non-writable value conflicts', () => assert.deepEqual(callCandidate('nonconfig-value-ignore'), {threw: false, value: true}));
test('rejects configurability conflicts', () => assert.equal(callCandidate('nonconfig-configurable-throw'), true));
test('can ignore configurability conflicts', () => assert.equal(callCandidate('nonconfig-configurable-ignore'), true));
test('rejects writability conflicts', () => assert.equal(callCandidate('nonconfig-writable-throw'), true));
test('can ignore writability conflicts', () => assert.equal(callCandidate('nonconfig-writable-ignore'), true));
test('rejects enumerability conflicts', () => assert.equal(callCandidate('nonconfig-enumerable-throw'), true));
test('can ignore enumerability conflicts', () => assert.equal(callCandidate('nonconfig-enumerable-ignore'), true));
test('defaults ignoreNonConfigurable to false', () => assert.equal(callCandidate('nonconfig-default-throw'), true));
