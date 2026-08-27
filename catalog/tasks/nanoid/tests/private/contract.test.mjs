import { deepEqual, equal, match, notEqual, ok, rejects, throws } from 'node:assert/strict'
import { test } from 'node:test'
import {
  callCandidate,
  callFactory,
  callFactorySequence,
  readCandidateExport,
  runCli,
} from './test_client.mjs'

const URL_ALPHABET_RE = /^[A-Za-z0-9_-]+$/

test('nanoid defaults to a 21-character URL-safe id', () => {
  const id = callCandidate('nanoid', [])
  equal(typeof id, 'string')
  equal(id.length, 21)
  ok(URL_ALPHABET_RE.test(id))
})

test('nanoid accepts zero and integer-coercible sizes', () => {
  equal(callCandidate('nanoid', [0]), '')
  equal(callCandidate('nanoid', ['10']).length, 10)
  equal(callCandidate('nanoid', [10.9]).length, 10)
})

test('nanoid supports IDs larger than one crypto request', () => {
  const id = callCandidate('nanoid', [70000])
  equal(id.length, 70000)
  ok(URL_ALPHABET_RE.test(id))
})

test('nanoid rejects negative sizes promptly', () => {
  throws(() => callCandidate('nanoid', [-1]), /Wrong ID size|Invalid typed array length/)
})

test('urlAlphabet is the distinct 64-symbol URL alphabet', () => {
  const alphabet = readCandidateExport('urlAlphabet')
  equal(typeof alphabet, 'string')
  equal(alphabet.length, 64)
  equal(new Set(alphabet).size, 64)
  match(alphabet, /^[A-Za-z0-9_-]+$/)
})

test('customAlphabet honors its default and requested sizes', () => {
  equal(callFactory('customAlphabet', 'nanoid', ['a', 5], []), 'aaaaa')
  equal(callFactory('customAlphabet', 'nanoid', ['a', 5], [0]), '')
})

test('customAlphabet supports one-character and bounded alphabets', () => {
  const id = callFactory('customAlphabet', 'nanoid', ['abc'], [0])
  equal(id, '')
  const ten = callFactory('customAlphabet', 'nanoid', ['abc'], [10])
  equal(ten.length, 10)
  ok(/^[abc]+$/.test(ten))
})

test('customAlphabet supports Unicode alphabets', () => {
  const id = callFactory('customAlphabet', 'nanoid', ['абвгд', 10], [])
  equal(id.length, 10)
  for (const char of id) ok('абвгд'.includes(char))
})

test('customAlphabet supports JSON array alphabets', () => {
  const id = callFactory('customAlphabet', 'nanoid', [['x', 'y'], 12], [])
  equal(id.length, 12)
  for (const char of id) ok(['x', 'y'].includes(char))
})

test('customAlphabet handles large alphabets without hanging at zero', () => {
  equal(callFactory('customAlphabet', 'nanoid', ['a'.repeat(300), 5], [0]), '')
})

test('customAlphabet does not pollute subsequent pool slices', () => {
  const [first, second, third] = callFactorySequence(
    'customAlphabet',
    'nanoid',
    ['abcdefghijklmnopqrstuvwxyz', 21],
    [[2.1], [], []],
  )
  equal(first.length, 2)
  equal(second.length, 21)
  equal(third.length, 21)
  notEqual(second, third)
})

test('customRandom is exported and constructible', () => {
  const value = callFactory(
    'customRandom',
    'nanoid',
    ['abc', 4],
    [],
    [255, 0, 1, 2, 255, 0, 1],
  )
  equal(value, 'bacb')
})

test('customRandom uses deterministic bytes and supports power-of-two alphabets', () => {
  equal(callFactory('customRandom', 'nanoid', ['abcd', 4], [], [0, 1, 2, 3]), 'dcba')
})

test('random returns the requested number of bounded bytes', () => {
  const bytes = callCandidate('random', [32])
  const values = Array.isArray(bytes?.data) ? bytes.data : Object.values(bytes)
  equal(values.length, 32)
  for (const value of values) ok(Number(value) >= 0 && Number(value) <= 255)
})

test('random rejects negative sizes', () => {
  throws(() => callCandidate('random', [-1]), /Wrong ID size|Invalid typed array length/)
})

test('secure ids from repeated calls do not collide in a small sample', () => {
  const ids = new Set()
  for (let i = 0; i < 100; i++) ids.add(callCandidate('nanoid', []))
  equal(ids.size, 100)
})

test('non-secure nanoid has the same basic size contract', () => {
  const id = callCandidate('nanoid', [], 'nanoid/non-secure')
  equal(id.length, 21)
  ok(URL_ALPHABET_RE.test(id))
  equal(callCandidate('nanoid', [0], 'nanoid/non-secure'), '')
  equal(callCandidate('nanoid', ['10'], 'nanoid/non-secure').length, 10)
})

test('non-secure nanoid does not hang on negative sizes', () => {
  equal(callCandidate('nanoid', [-100], 'nanoid/non-secure'), '')
  equal(callFactory('customAlphabet', 'nanoid/non-secure', ['abc'], [-1]), '')
})

test('non-secure customAlphabet honors fixed alphabets', () => {
  const id = callFactory('customAlphabet', 'nanoid/non-secure', ['a', 5], [])
  equal(id, 'aaaaa')
})

test('non-secure customAlphabet supports Unicode and zero size', () => {
  const id = callFactory('customAlphabet', 'nanoid/non-secure', ['абв', 8], [])
  equal(id.length, 8)
  for (const char of id) ok('абв'.includes(char))
  equal(callFactory('customAlphabet', 'nanoid/non-secure', ['abc', 5], [0]), '')
})

test('CLI prints a default URL-safe id', () => {
  const result = runCli([])
  equal(result.status, 0)
  equal(result.stderr, '')
  match(result.stdout, /^[\w-]{21}\n$/)
})

test('CLI honors the size option', () => {
  const result = runCli(['--size', '10'])
  equal(result.status, 0)
  match(result.stdout, /^[\w-]{10}\n$/)
})

test('CLI honors the alphabet option', () => {
  const result = runCli(['--alphabet', 'abc', '--size', '15'])
  equal(result.status, 0)
  match(result.stdout, /^[abc]{15}\n$/)
})

test('CLI supports short options', () => {
  const result = runCli(['-a', 'x', '-s', '7'])
  equal(result.status, 0)
  equal(result.stdout, 'xxxxxxx\n')
})

test('CLI help contains its usage heading', () => {
  const result = runCli(['--help'])
  equal(result.status, 0)
  equal(result.stderr, '')
  match(result.stdout, /Usage/)
  match(result.stdout, /\$ nanoid \[options\]/)
})

test('CLI version reports 6.0.1', () => {
  const result = runCli(['--version'])
  equal(result.status, 0)
  equal(result.stdout, '6.0.1\n')
})

test('CLI rejects unknown arguments', () => {
  const result = runCli(['-test'])
  notEqual(result.status, 0)
  match(result.stderr, /Unknown argument -test/)
})

test('CLI rejects non-positive and non-numeric sizes', () => {
  const negative = runCli(['--size', '-1'])
  const invalid = runCli(['-s', 'abc'])
  notEqual(negative.status, 0)
  notEqual(invalid.status, 0)
  match(negative.stderr, /Size must be positive integer/)
  match(invalid.stderr, /Size must be positive integer/)
})
