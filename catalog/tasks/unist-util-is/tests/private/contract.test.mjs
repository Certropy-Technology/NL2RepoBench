import assert from 'node:assert/strict'
import test from 'node:test'
import {request} from './test_client.mjs'

const strong = {type: 'strong', children: [{type: 'text', value: 'a'}]}
const parent = {type: 'paragraph', children: [strong]}

function value(operation, payload) {
  const response = request(operation, payload)
  assert.equal(response.ok, true, response.message)
  return response.value
}

function failure(operation, payload) {
  const response = request(operation, payload)
  assert.equal(response.ok, false)
  return response
}

function isValue(payload) {
  return value('is', payload)
}

test('package metadata identifies the frozen package', () => {
  const inventory = value('inventory', {})
  assert.equal(inventory.packageName, 'unist-util-is')
  assert.equal(inventory.packageVersion, '6.0.1')
  assert.equal(inventory.moduleType, 'module')
  assert.equal(inventory.exportsField, './index.js')
})

test('package root exposes exactly the named exports', () => {
  assert.deepEqual(value('inventory', {}).exportNames, ['convert', 'is'])
})

test('package includes a nonempty root declaration entry', () => {
  assert.equal(value('inventory', {}).declarationEntry, true)
})

test('candidate calls run as the isolated uid and gid', () => {
  const inventory = value('inventory', {})
  assert.equal(inventory.uid, 10001)
  assert.equal(inventory.gid, 10001)
})

test('omitted node is not a node', () => {
  assert.equal(isValue({}).result, false)
})

test('null is not a node', () => {
  assert.equal(isValue({node: null}).result, false)
})

test('primitive values are not nodes', () => {
  for (const node of [false, 0, 'strong']) {
    assert.equal(isValue({node}).result, false)
  }
})

test('arrays without a type property are not nodes', () => {
  assert.equal(isValue({node: []}).result, false)
})

test('plain objects without a type property are not nodes', () => {
  assert.equal(isValue({node: {children: []}}).result, false)
})

test('a present null type property is node-like for a nullish test', () => {
  assert.equal(isValue({node: {type: null}}).result, true)
})

test('an empty type property is node-like for a nullish test', () => {
  assert.equal(isValue({node: {type: ''}}).result, true)
})

test('node recognition ignores extra fields and does not mutate', () => {
  const node = {type: 'strong', data: {score: 1}, children: []}
  assert.equal(isValue({node}).result, true)
  assert.deepEqual(node, {type: 'strong', data: {score: 1}, children: []})
})

test('string tests match an exact type', () => {
  assert.equal(isValue({node: strong, test: 'strong'}).result, true)
})

test('string tests reject another type', () => {
  assert.equal(isValue({node: strong, test: 'emphasis'}).result, false)
})

test('string tests are case-sensitive', () => {
  assert.equal(isValue({node: strong, test: 'Strong'}).result, false)
})

test('string tests do not coerce a non-string node type', () => {
  assert.equal(isValue({node: {type: 7}, test: '7'}).result, false)
})

test('object tests match a property subset', () => {
  assert.equal(isValue({node: strong, test: {type: 'strong'}}).result, true)
})

test('object tests ignore additional node properties', () => {
  assert.equal(
    isValue({node: {type: 'text', value: 'a', extra: true}, test: {type: 'text'}})
      .result,
    true
  )
})

test('object tests reject a mismatched property', () => {
  assert.equal(
    isValue({node: {type: 'heading', depth: 2}, test: {type: 'heading', depth: 3}})
      .result,
    false
  )
})

test('an undefined expected property matches a missing property', () => {
  assert.equal(
    isValue({node: {type: 'text'}, test: {missing: {$undefined: true}}}).result,
    true
  )
})

test('object tests use strict primitive equality', () => {
  assert.equal(isValue({node: {type: 'heading', depth: 2}, test: {depth: '2'}}).result, false)
})

test('separate structurally equal nested objects do not match', () => {
  assert.equal(
    isValue({node: {type: 'x', data: {rank: 1}}, test: {data: {rank: 1}}}).result,
    false
  )
})

test('the same nested object reference matches', () => {
  assert.equal(
    isValue({
      node: {type: 'x', data: {$shared: 'data', value: {rank: 1}}},
      test: {data: {$shared: 'data'}}
    }).result,
    true
  )
})

test('an empty object test matches every node-like object', () => {
  assert.equal(isValue({node: strong, test: {}}).result, true)
})

test('array tests pass when one string test matches', () => {
  assert.equal(isValue({node: strong, test: ['emphasis', 'strong']}).result, true)
})

test('array tests fail when no test matches', () => {
  assert.equal(isValue({node: strong, test: ['delete', 'emphasis']}).result, false)
})

test('an empty array test fails', () => {
  assert.equal(isValue({node: strong, test: []}).result, false)
})

test('array tests combine object and string selectors', () => {
  assert.equal(
    isValue({node: {type: 'heading', depth: 2}, test: [{depth: 3}, 'heading']}).result,
    true
  )
})

test('array tests evaluate a false callback before a later match', () => {
  const result = isValue({
    node: strong,
    test: [{$callback: {mode: 'false'}}, 'strong']
  })
  assert.equal(result.result, true)
  assert.deepEqual(result.trace, [{nodeType: 'strong'}])
})

test('array tests short-circuit before a later callback', () => {
  const result = isValue({
    node: strong,
    test: ['strong', {$callback: {mode: 'true'}}]
  })
  assert.equal(result.result, true)
  assert.deepEqual(result.trace, [])
})

test('a truthy function selector passes', () => {
  assert.equal(
    isValue({node: strong, test: {$callback: {mode: 'true'}}}).result,
    true
  )
})

test('a false function selector fails', () => {
  assert.equal(
    isValue({node: strong, test: {$callback: {mode: 'false'}}}).result,
    false
  )
})

test('a function selector returning undefined fails', () => {
  assert.equal(
    isValue({node: strong, test: {$callback: {mode: 'void'}}}).result,
    false
  )
})

test('function selectors receive the exact node', () => {
  const result = isValue({
    node: strong,
    test: {$callback: {mode: 'match', type: 'strong'}}
  })
  assert.equal(result.result, true)
  assert.deepEqual(result.trace, [{nodeType: 'strong'}])
})

test('function selectors receive the index', () => {
  const result = isValue({
    node: strong,
    test: {$callback: {mode: 'match', index: 0}},
    index: 0,
    parent
  })
  assert.equal(result.result, true)
  assert.equal(result.trace[0].index, 0)
})

test('function selectors receive the parent', () => {
  const result = isValue({
    node: strong,
    test: {$callback: {mode: 'match', parentType: 'paragraph'}},
    index: 0,
    parent
  })
  assert.equal(result.result, true)
  assert.equal(result.trace[0].parentType, 'paragraph')
})

test('function selectors receive the explicit this context', () => {
  const result = isValue({
    node: strong,
    test: {$callback: {mode: 'match', contextToken: 'ctx'}},
    context: {token: 'ctx'}
  })
  assert.equal(result.result, true)
  assert.equal(result.trace[0].contextToken, 'ctx')
})

test('function selectors receive node index parent and context together', () => {
  const result = isValue({
    node: strong,
    test: {
      $callback: {
        mode: 'match',
        type: 'strong',
        index: 0,
        parentType: 'paragraph',
        contextToken: 'all'
      }
    },
    index: 0,
    parent,
    context: {token: 'all'}
  })
  assert.equal(result.result, true)
  assert.deepEqual(result.trace, [
    {contextToken: 'all', index: 0, nodeType: 'strong', parentType: 'paragraph'}
  ])
})

test('a boolean test is rejected', () => {
  assert.match(
    failure('is', {node: strong, test: false}).message,
    /Expected function, string, or object as test/
  )
})

test('a numeric test is rejected', () => {
  assert.match(
    failure('is', {node: strong, test: 1}).message,
    /Expected function, string, or object as test/
  )
})

test('a negative index is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: -1, parent}).message,
    /Expected positive finite index/
  )
})

test('positive infinity as index is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: {$number: 'Infinity'}, parent}).message,
    /Expected positive finite index/
  )
})

test('a non-number index is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: '0', parent}).message,
    /Expected positive finite index/
  )
})

test('a parent without a type property is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: 0, parent: {children: []}}).message,
    /Expected parent node/
  )
})

test('a parent without children is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: 0, parent: {type: 'paragraph'}}).message,
    /Expected parent node/
  )
})

test('an index without a parent is rejected', () => {
  assert.match(
    failure('is', {node: strong, index: 0}).message,
    /Expected both parent and index/
  )
})

test('a parent without an index is rejected', () => {
  assert.match(
    failure('is', {node: strong, parent}).message,
    /Expected both parent and index/
  )
})

test('convert with a nullish test returns an unconditional check', () => {
  assert.deepEqual(
    value('convert', {test: null, calls: [{node: strong}, {node: null}]}).results,
    [true, true]
  )
})

test('convert creates a reusable string check', () => {
  assert.deepEqual(
    value('convert', {
      test: 'strong',
      calls: [{node: strong}, {node: {type: 'emphasis'}}]
    }).results,
    [true, false]
  )
})

test('convert creates a strict object check', () => {
  assert.deepEqual(
    value('convert', {
      test: {type: 'heading', depth: 2},
      calls: [
        {node: {type: 'heading', depth: 2}},
        {node: {type: 'heading', depth: 3}}
      ]
    }).results,
    [true, false]
  )
})

test('convert creates an array disjunction check', () => {
  assert.deepEqual(
    value('convert', {
      test: ['strong', {type: 'heading', depth: 2}],
      calls: [{node: strong}, {node: {type: 'heading', depth: 2}}, {node: {type: 'root'}}]
    }).results,
    [true, true, false]
  )
})

test('convert preserves function selector behavior', () => {
  const result = value('convert', {
    test: {$callback: {mode: 'match', type: 'strong'}},
    calls: [{node: strong}, {node: {type: 'emphasis'}}]
  })
  assert.deepEqual(result.results, [true, false])
  assert.deepEqual(result.trace.map((entry) => entry.nodeType), ['strong', 'emphasis'])
})

test('one converted check remains deterministic across repeated calls', () => {
  assert.deepEqual(
    value('convert', {
      test: 'text',
      calls: Array.from({length: 6}, (_, index) => ({
        node: {type: index % 2 === 0 ? 'text' : 'strong'}
      }))
    }).results,
    [true, false, true, false, true, false]
  )
})

test('converted callbacks normalize a null index to undefined', () => {
  const result = value('convert', {
    test: {$callback: {mode: 'true'}},
    calls: [{node: strong, index: null}]
  })
  assert.deepEqual(result.results, [true])
  assert.deepEqual(result.trace, [{nodeType: 'strong'}])
})

test('converted callbacks normalize a null parent and preserve this', () => {
  const result = value('convert', {
    test: {$callback: {mode: 'match', contextToken: 'converted'}},
    calls: [{node: strong, parent: null, context: {token: 'converted'}}]
  })
  assert.deepEqual(result.results, [true])
  assert.deepEqual(result.trace, [{contextToken: 'converted', nodeType: 'strong'}])
})

test('convert rejects an invalid selector immediately', () => {
  assert.match(
    failure('convert', {test: true, calls: [{node: strong}]}).message,
    /Expected function, string, or object as test/
  )
})
