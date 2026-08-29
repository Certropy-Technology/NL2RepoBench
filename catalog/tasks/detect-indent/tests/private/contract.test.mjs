import assert from 'node:assert/strict';
import test from 'node:test';
import {callCandidate} from './test_client.mjs';

const spaces = [
  'function test() {\n    return true;\n}',
  'const value = {\n    first: 1,\n    second: 2\n};',
  'if (a) {\n    if (b) {\n        deep();\n    }\n}',
].join('\n');
const tabs = 'function test() {\n\treturn true;\n\tif (ok) {\n\t\twork();\n\t}\n}';

test('detects four-space indentation', () => {
  assert.deepEqual(callCandidate(spaces), {amount: 4, indent: '    ', type: 'space'});
});

test('detects a four-tab indentation unit', () => {
  assert.deepEqual(callCandidate('\t\t\t\t\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\t\t\t'), {amount: 4, indent: '\t\t\t\t', type: 'tab'});
});

test('detects one-tab indentation', () => {
  assert.deepEqual(callCandidate(tabs), {amount: 1, indent: '\t', type: 'tab'});
});

test('tie uses the first strongest indentation evidence', () => {
  assert.deepEqual(callCandidate('    four spaces\n    more spaces\n\tone tab\n\tmore tabs'), {amount: 4, indent: '    ', type: 'space'});
});

test('prefers the majority space transition', () => {
  assert.equal(callCandidate('root\n    one\n    two\n        three\n    four').indent, '    ');
});

test('returns complete stats for majority spaces', () => {
  assert.deepEqual(callCandidate('root\n    one\n    two\n        three\n    four'), {amount: 4, indent: '    ', type: 'space'});
});

test('ignores a single aligned comment space', () => {
  assert.equal(callCandidate('function f() {\n    const object = {\n        // aligned\n         key: true,\n        other: true\n    };\n}').indent, '    ');
});

test('supports CRLF line endings', () => {
  assert.deepEqual(callCandidate('function f() {\r\n    return true;\r\n}\r\n').amount, 4);
});

test('returns zero amount for unindented text', () => {
  assert.equal(callCandidate('<ul></ul>').amount, 0);
});

test('returns the empty result when no indentation exists', () => {
  assert.deepEqual(callCandidate('<ul></ul>'), {amount: 0, indent: '', type: null});
});

test('spaces win when they occur first in an even split', () => {
  assert.equal(callCandidate('    spaces\n    spaces\n\ttabs\n\ttabs').type, 'space');
});

test('tabs win when they occur first in an even split', () => {
  assert.equal(callCandidate('\ttabs\n\ttabs\n    spaces\n    spaces').type, 'tab');
});

test('later tab evidence can win after a space transition', () => {
  assert.deepEqual(callCandidate('    spaces\n    spaces\n\ttabs\n\ttabs\n\tmore'), {amount: 1, indent: '\t', type: 'tab'});
});

test('handles a file containing documentation comments', () => {
  const code = '/**\n * docs\n * @param value\n */\nfunction f() {\n    return true;\n}';
  assert.deepEqual(callCandidate(code), {amount: 4, indent: '    ', type: 'space'});
});

test('detects one-space indentation when it is the only signal', () => {
  assert.deepEqual(callCandidate('a\n b\n c'), {amount: 1, indent: ' ', type: 'space'});
});

test('does not let one unusual transition override repeated four-space transitions', () => {
  assert.equal(callCandidate('root\n    a\n    b\n    c\n        d\n    e').amount, 4);
});

test('ignores aligned multi-line comment prefixes', () => {
  const code = 'interface Test {\n    // a\n    a: boolean\n    // b\n    b: boolean\n    /**\n     * note\n     */\n    c: boolean\n}';
  assert.equal(callCandidate(code).amount, 4);
});

test('ignores single-space alignment after a tab', () => {
  const code = '{\n\tkey: value,\n\t other: value,\n\tnested: {\n\t\tdeep: true\n\t}\n}';
  assert.deepEqual(callCandidate(code), {amount: 1, indent: '\t', type: 'tab'});
});

test('handles an empty string', () => {
  assert.deepEqual(callCandidate(''), {amount: 0, indent: '', type: null});
});

test('detects two-space indentation', () => {
  const code = "module.exports = {\n  name: 'test',\n  nested: {\n    deep: true\n  }\n};";
  assert.deepEqual(callCandidate(code).type, 'space');
  assert.equal(callCandidate(code).amount, 2);
});

test('detects deeply nested four-space code', () => {
  const code = 'if (a) {\n    if (b) {\n        if (c) {\n            deep();\n        }\n    }\n}';
  assert.deepEqual(callCandidate(code), {amount: 4, indent: '    ', type: 'space'});
});

test('detects sparse indentation', () => {
  const code = '#ifndef HEADER_H\n#define HEADER_H\n\ntypedef struct {\n    int x;\n    int y;\n} Point;\n\n#endif';
  assert.equal(callCandidate(code).amount, 4);
});

test('does not treat a continuation alignment as the main unit', () => {
  const code = 'function test(argumentOne,\n               argumentTwo) {\n    const a = 1;\n    const b = 2;\n    if (a) {\n        return b;\n    }\n}';
  assert.deepEqual(callCandidate(code), {amount: 4, indent: '    ', type: 'space'});
});

test('detects three-space indentation', () => {
  const code = 'function test() {\n   if (condition) {\n      doSomething();\n      if (nested) {\n         deepCall();\n      }\n   }\n}';
  assert.deepEqual(callCandidate(code), {amount: 3, indent: '   ', type: 'space'});
});

test('handles one indent transition', () => {
  assert.deepEqual(callCandidate('if (true) {\n    return 1;\n}'), {amount: 4, indent: '    ', type: 'space'});
});

test('uses whitespace-only lines as evidence', () => {
  assert.deepEqual(callCandidate('    \n    \n    \n'), {amount: 4, indent: '    ', type: 'space'});
});

test('detects indentation when the document starts indented', () => {
  assert.deepEqual(callCandidate('    function inner() {\n        return true;\n    }'), {amount: 4, indent: '    ', type: 'space'});
});

test('throws TypeError for a number', () => {
  assert.throws(() => callCandidate(42), {name: 'TypeError', message: 'Expected a string'});
});

test('throws TypeError for null', () => {
  assert.throws(() => callCandidate(null), {name: 'TypeError', message: 'Expected a string'});
});

test('returns a fresh object for each call', () => {
  const first = callCandidate('a\n    b');
  const second = callCandidate('a\n    b');
  assert.notEqual(first, second);
  assert.deepEqual(second, {amount: 4, indent: '    ', type: 'space'});
});
