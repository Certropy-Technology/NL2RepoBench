import assert from 'node:assert/strict';
import {test} from 'node:test';
import {callCandidate} from './test_client.mjs';

function value(exportName, input) {
  const response = callCandidate(exportName, input);
  assert.equal(response.ok, true, `${response.error}: ${response.message ?? ''}`);
  assert.equal(typeof response.value, 'string');
  return response.value;
}

function exception(exportName, input) {
  const response = callCandidate(exportName, input);
  assert.equal(response.ok, false);
  assert.equal(response.error, 'candidate-call-failed');
  return response.exception_type;
}

test('default export is callable from the package root', () => {
  assert.equal(value('default', '\talpha'), 'alpha');
});

test('named dedent export is callable from the package root', () => {
  assert.equal(value('dedent', '\n\talpha\n'), 'alpha');
});

test('stripIndent removes common spaces from one line', () => {
  assert.equal(value('default', '    alpha'), 'alpha');
});

test('stripIndent removes common tabs from one line', () => {
  assert.equal(value('default', '\t\talpha'), 'alpha');
});

test('stripIndent uses the smallest space prefix', () => {
  assert.equal(value('default', '  alpha\n    beta\n   gamma'), 'alpha\n  beta\n gamma');
});

test('stripIndent uses the smallest tab prefix', () => {
  assert.equal(value('default', '\talpha\n\t\tbeta\n\t\t\tgamma'), 'alpha\n\tbeta\n\t\tgamma');
});

test('spaces and tabs each count as one prefix character', () => {
  assert.equal(value('default', ' \talpha\n\t  beta'), 'alpha\n beta');
});

test('whitespace-only lines do not determine minimum indentation', () => {
  assert.equal(value('default', '\t\talpha\n\t\n\t\t\tbeta'), 'alpha\n\t\n\tbeta');
});

test('internal blank lines remain in place', () => {
  assert.equal(value('default', '  alpha\n\n  beta'), 'alpha\n\nbeta');
});

test('an unindented content line leaves the string unchanged', () => {
  const input = 'alpha\n  beta';
  assert.equal(value('default', input), input);
});

test('stripIndent preserves an empty string', () => {
  assert.equal(value('default', ''), '');
});

test('stripIndent preserves a spaces-only string', () => {
  assert.equal(value('default', '   '), '   ');
});

test('stripIndent preserves a tabs-only string', () => {
  assert.equal(value('default', '\t\t'), '\t\t');
});

test('stripIndent preserves a leading newline', () => {
  assert.equal(value('default', '\n  alpha'), '\nalpha');
});

test('stripIndent preserves a trailing newline', () => {
  assert.equal(value('default', '  alpha\n'), 'alpha\n');
});

test('stripIndent preserves CRLF separators', () => {
  assert.equal(value('default', '  alpha\r\n    beta'), 'alpha\r\n  beta');
});

test('stripIndent preserves trailing spaces after content', () => {
  assert.equal(value('default', '  alpha   \n    beta  '), 'alpha   \n  beta  ');
});

test('stripIndent preserves Unicode content', () => {
  assert.equal(value('default', '\t你好\n\t\t🙂'), '你好\n\t🙂');
  assert.equal(value('default', '  \u00A0\n    alpha'), '  \u00A0\nalpha');
});

test('dedent handles a template-literal shape', () => {
  assert.equal(value('dedent', '\n\t\talpha\n\t\t\tbeta\n\t'), 'alpha\n\tbeta');
});

test('dedent removes multiple leading whitespace-only lines', () => {
  assert.equal(value('dedent', '\n \n\t\n\talpha'), 'alpha');
});

test('dedent removes multiple trailing whitespace-only lines', () => {
  assert.equal(value('dedent', '\talpha\n\t\n \n'), 'alpha');
});

test('dedent removes CRLF boundary lines', () => {
  assert.equal(value('dedent', '\r\n\t\r\n\talpha\r\n\t\r\n'), 'alpha');
});

test('dedent handles mixed LF and CRLF boundary lines', () => {
  assert.equal(value('dedent', '\r\n\n\talpha\n\r\n'), 'alpha');
});

test('dedent returns empty for only whitespace lines', () => {
  assert.equal(value('dedent', '\n \n\t \n'), '');
});

test('dedent preserves an empty string', () => {
  assert.equal(value('dedent', ''), '');
});

test('dedent preserves internal empty lines', () => {
  assert.equal(value('dedent', '\n\talpha\n\n\tbeta\n'), 'alpha\n\nbeta');
});

test('dedent preserves remaining internal whitespace-only content', () => {
  assert.equal(value('dedent', '\n\t\talpha\n\t\t  \n\t\tbeta\n'), 'alpha\n  \nbeta');
});

test('dedent without boundary lines applies stripIndent', () => {
  assert.equal(value('dedent', '\talpha\n\t\tbeta'), 'alpha\n\tbeta');
});

test('stripIndent rejects non-string inputs with TypeError', () => {
  for (const input of [null, 12, true, [], {}]) {
    assert.equal(exception('default', input), 'TypeError');
  }
});

test('dedent rejects non-string inputs with TypeError', () => {
  for (const input of [null, 12, false, [], {}]) {
    assert.equal(exception('dedent', input), 'TypeError');
  }
});

test('repeated calls are deterministic', () => {
  const input = '  alpha\n    beta';
  assert.deepEqual(Array.from({length: 6}, () => value('default', input)), Array(6).fill('alpha\n  beta'));
});

test('alternating exports do not leak state', () => {
  assert.deepEqual([
    value('default', '\talpha'),
    value('dedent', '\n  beta\n'),
    value('default', 'gamma\n  delta'),
    value('dedent', '\n\talpha\n\t\tbeta\n'),
  ], ['alpha', 'beta', 'gamma\n  delta', 'alpha\n\tbeta']);
});
