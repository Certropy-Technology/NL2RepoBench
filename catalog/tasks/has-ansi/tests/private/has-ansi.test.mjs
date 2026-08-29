import assert from 'node:assert/strict';
import test from 'node:test';
import {query} from './test_client.mjs';

function check(name, value, expected) {
  test(name, () => {
    const response = query('check', value);
    assert.deepEqual(response.result, expected);
    assert.equal(response.error, undefined);
  });
}

test('package metadata and runtime export', () => {
  const response = query('metadata');
  assert.equal(response.error, undefined);
  assert.equal(response.result.name, 'has-ansi');
  assert.equal(response.result.version, '6.0.2');
  assert.equal(response.result.type, 'module');
  assert.equal(response.result.defaultType, 'function');
  assert.deepEqual(response.result.exports, {
    '.': {
      default: './index.js',
      types: './index.d.ts',
    },
  });
});

test('package includes the typed default declaration', () => {
  const response = query('metadata');
  assert.match(response.result.declaration, /export default function hasAnsi\(string: string\): boolean;/);
});

check('empty string is not ANSI', '', false);
check('ordinary text is not ANSI', 'cake', false);
check('whitespace is not ANSI', ' \t\n ', false);
check('unicode text is not ANSI', '你好 café', false);
check('literal escape notation is not ANSI', '\\u001B[31m', false);
check('lone escape is not ANSI', '\u001B', false);
check('escape plus ordinary character is not ANSI', '\u001BX', false);
check('SGR color sequence is ANSI', '\u001B[31mred\u001B[39m', true);
check('reset sequence is ANSI', '\u001B[0m', true);
check('cursor CSI sequence is ANSI', '\u001B[2J', true);
check('OSC title sequence is ANSI', '\u001B]0;title\u0007', true);
check('eight-bit CSI sequence is ANSI', '\u009B31m', true);
check('parameter CSI prefix is accepted', '\u001B[31', true);
check('embedded sequence is detected', 'before\u001B[4mafter', true);
check('multiline sequence is detected', 'first\n\u001B[32msecond\r\nthird', true);
check('multiple sequences are detected', '\u001B[31mred\u001B[0m plain \u001B[44mblue', true);
check('private CSI parameter is detected', '\u001B[?25l', true);
check('sequence at the end is detected', 'done\u001B[39m', true);
check('sequence at the start is detected', '\u001B[1mstrong', true);
check('control sequence with intermediate byte is detected', '\u001B(0', true);
check('DEL alone is not ANSI', '\u007F', false);
check('multi-parameter SGR sequence is detected', '\u001B[1;2;3m', true);
