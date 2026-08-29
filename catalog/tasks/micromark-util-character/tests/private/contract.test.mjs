import assert from 'node:assert/strict'
import {test} from 'node:test'
import {call, inventory} from './test_client.mjs'

const exportNames = [
  'asciiAlpha',
  'asciiAlphanumeric',
  'asciiAtext',
  'asciiControl',
  'asciiDigit',
  'asciiHexDigit',
  'asciiPunctuation',
  'markdownLineEnding',
  'markdownLineEndingOrSpace',
  'markdownSpace',
  'unicodePunctuation',
  'unicodeWhitespace'
].sort()

function result(exportName, code) {
  const response = call(exportName, code)
  assert.equal(response.ok, true, response.message)
  return response.value
}

function classifierCases(exportName, cases) {
  for (const [label, code, expected] of cases) {
    test(`${exportName}: ${label}`, () => {
      assert.equal(result(exportName, code), expected)
    })
  }
}

test('package metadata and exact named ESM exports', () => {
  const response = inventory()
  assert.equal(response.ok, true, response.message)
  assert.deepEqual(response.value, {
    uid: 10001,
    gid: 10001,
    packageName: 'micromark-util-character',
    packageVersion: '2.1.1',
    moduleType: 'module',
    sideEffects: false,
    exports: {development: './dev/index.js', default: './index.js'},
    types: './index.d.ts',
    dependencies: {
      'micromark-util-symbol': '2.0.1',
      'micromark-util-types': '2.0.2'
    },
    hasLifecycleScript: false,
    exportNames,
    allExportsFunctions: true
  })
})

test('same input is deterministic across isolated child calls', () => {
  assert.equal(result('asciiAlpha', 65), true)
  assert.equal(result('asciiAlpha', 65), true)
})

classifierCases('asciiAlpha', [
  ['before uppercase range', 64, false],
  ['uppercase lower boundary', 65, true],
  ['uppercase upper boundary', 90, true],
  ['between letter ranges', 91, false],
  ['lowercase lower boundary', 97, true],
  ['lowercase upper boundary', 122, true],
  ['after lowercase range', 123, false],
  ['null', null, false]
])

classifierCases('asciiAlphanumeric', [
  ['before digit range', 47, false],
  ['digit lower boundary', 48, true],
  ['digit upper boundary', 57, true],
  ['after digit range', 58, false],
  ['uppercase letter', 81, true],
  ['lowercase letter', 113, true],
  ['null', null, false]
])

classifierCases('asciiAtext', [
  ['exclamation is excluded', 33, false],
  ['number sign is included', 35, true],
  ['apostrophe is included', 39, true],
  ['left parenthesis is excluded', 40, false],
  ['asterisk is included', 42, true],
  ['comma is excluded', 44, false],
  ['dash is included', 45, true],
  ['slash is included', 47, true],
  ['equals is included', 61, true],
  ['at sign is excluded', 64, false],
  ['tilde is included', 126, true],
  ['null', null, false]
])

classifierCases('asciiControl', [
  ['markdown carriage return virtual code', -5, true],
  ['markdown virtual space code', -1, true],
  ['null is not control', null, false],
  ['NUL lower boundary', 0, true],
  ['unit separator upper boundary', 31, true],
  ['space is not control', 32, false],
  ['tilde is not control', 126, false],
  ['DEL is control', 127, true],
  ['above DEL is not control', 128, false]
])

classifierCases('asciiDigit', [
  ['before range', 47, false],
  ['lower boundary', 48, true],
  ['upper boundary', 57, true],
  ['after range', 58, false],
  ['null', null, false]
])

classifierCases('asciiHexDigit', [
  ['digit', 55, true],
  ['uppercase A', 65, true],
  ['uppercase F', 70, true],
  ['uppercase G', 71, false],
  ['lowercase a', 97, true],
  ['lowercase f', 102, true],
  ['lowercase g', 103, false],
  ['null', null, false]
])

classifierCases('asciiPunctuation', [
  ['space before first range', 32, false],
  ['exclamation lower boundary', 33, true],
  ['slash upper boundary', 47, true],
  ['digit is excluded', 48, false],
  ['colon lower boundary', 58, true],
  ['at sign upper boundary', 64, true],
  ['letter is excluded', 65, false],
  ['left bracket lower boundary', 91, true],
  ['tilde upper boundary', 126, true],
  ['DEL after final range', 127, false],
  ['null', null, false]
])

classifierCases('markdownLineEnding', [
  ['virtual carriage return', -5, true],
  ['virtual line feed', -4, true],
  ['virtual CRLF', -3, true],
  ['horizontal tab virtual code', -2, false],
  ['virtual space', -1, false],
  ['concrete NUL', 0, false],
  ['null', null, false]
])

classifierCases('markdownLineEndingOrSpace', [
  ['virtual carriage return', -5, true],
  ['virtual CRLF', -3, true],
  ['horizontal tab virtual code', -2, true],
  ['virtual space', -1, true],
  ['concrete NUL', 0, false],
  ['concrete space', 32, true],
  ['exclamation', 33, false],
  ['null', null, false]
])

classifierCases('markdownSpace', [
  ['horizontal tab virtual code', -2, true],
  ['virtual space', -1, true],
  ['concrete space', 32, true],
  ['line ending virtual code', -3, false],
  ['concrete tab is not preprocessed space', 9, false],
  ['null', null, false]
])

classifierCases('unicodePunctuation', [
  ['ASCII exclamation punctuation', 33, true],
  ['ASCII letter', 65, false],
  ['connector punctuation underscore', 95, true],
  ['inverted question mark', 0x00bf, true],
  ['em dash', 0x2014, true],
  ['euro symbol', 0x20ac, true],
  ['star symbol', 0x2605, true],
  ['nonbreaking space', 0x00a0, false],
  ['negative virtual code', -1, false],
  ['null', null, false]
])

classifierCases('unicodeWhitespace', [
  ['horizontal tab', 9, true],
  ['line feed', 10, true],
  ['vertical tab', 11, true],
  ['form feed', 12, true],
  ['carriage return', 13, true],
  ['ASCII space', 32, true],
  ['nonbreaking space', 0x00a0, true],
  ['ogham space mark', 0x1680, true],
  ['line separator', 0x2028, true],
  ['byte order mark', 0xfeff, true],
  ['ASCII letter', 65, false],
  ['negative virtual code', -1, false],
  ['null', null, false]
])
