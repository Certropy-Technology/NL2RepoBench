import assert from 'node:assert/strict'
import test from 'node:test'
import {classify, inventory} from './test_client.mjs'

test('exports exactly the named phrasing function', () => {
  assert.deepEqual(inventory().exports, ['phrasing'])
})
test('runs the candidate child as uid 10001', () => assert.equal(inventory().uid, 10001))
test('runs the candidate child as gid 10001', () => assert.equal(inventory().gid, 10001))

test('returns false for omitted input', () => assert.equal(classify(undefined, false).value, false))
test('returns false for null', () => assert.equal(classify(null).value, false))
test('returns false for booleans', () => assert.equal(classify(true).value, false))
test('returns false for numbers', () => assert.equal(classify(42).value, false))
test('returns false for strings', () => assert.equal(classify('text').value, false))
test('returns false for arrays', () => assert.equal(classify([{type: 'text'}]).value, false))
test('returns false for an empty object', () => assert.equal(classify({}).value, false))
test('returns false for an unknown node type', () => assert.equal(classify({type: 'unknown'}).value, false))
test('returns false for a null type', () => assert.equal(classify({type: null}).value, false))
test('returns false for a numeric type', () => assert.equal(classify({type: 1}).value, false))
test('matches node types case-sensitively', () => assert.equal(classify({type: 'Link'}).value, false))

for (const type of [
  'break', 'delete', 'emphasis', 'footnote', 'footnoteReference', 'image',
  'imageReference', 'inlineCode', 'inlineMath', 'link', 'linkReference',
  'mdxJsxTextElement', 'mdxTextExpression', 'strong', 'text', 'textDirective'
]) {
  test(`accepts the phrasing node type ${type}`, () => {
    const output = classify({type})
    assert.equal(output.valueType, 'boolean')
    assert.equal(output.value, true)
  })
}

test('rejects paragraph nodes', () => assert.equal(classify({type: 'paragraph'}).value, false))
test('rejects heading nodes', () => assert.equal(classify({type: 'heading'}).value, false))
test('rejects list nodes', () => assert.equal(classify({type: 'list'}).value, false))
test('rejects ambiguous html nodes', () => assert.equal(classify({type: 'html'}).value, false))
test('classifies a parent independently from phrasing children', () => {
  assert.equal(classify({type: 'paragraph', children: [{type: 'text', value: 'Alpha'}]}).value, false)
})
test('ignores extra fields and does not mutate input', () => {
  const output = classify({type: 'link', url: '/x', children: [{type: 'text', value: 'x'}], data: {flag: true}})
  assert.equal(output.value, true)
  assert.equal(output.unchanged, true)
})
