import assert from 'node:assert/strict'
import {test as nodeTest} from 'node:test'
import {walk} from './test_client.mjs'

const tree = {
  type: 'root',
  children: [
    {type: 'paragraph', children: [
      {type: 'text', value: 'a'},
      {type: 'emphasis', children: [{type: 'text', value: 'b'}]},
      {type: 'text', value: 'c'}
    ]},
    {type: 'quote', children: [
      {type: 'paragraph', children: [{type: 'text', value: 'd'}]}
    ]}
  ]
}

function result(request) {
  const response = walk({...request, tree: request.tree ?? tree})
  assert.equal(response.ok, true, response.error)
  return response
}

function types(response) {
  return response.visits.map((item) => item.type)
}

nodeTest('exports the required ESM API through the adapter', () => {
  assert.deepEqual(result({mode: 'record'}).exports, ['CONTINUE', 'EXIT', 'SKIP'])
})

nodeTest('visits a root before descendants in preorder', () => {
  assert.deepEqual(types(result({mode: 'record'})), ['root', 'paragraph', 'text', 'emphasis', 'text', 'text', 'quote', 'paragraph', 'text'])
})

nodeTest('preserves callback index and parent type', () => {
  assert.deepEqual(result({mode: 'record'}).visits.slice(0, 5), [
    {type: 'root'},
    {type: 'paragraph', index: 0, parentType: 'root'},
    {type: 'text', index: 0, parentType: 'paragraph'},
    {type: 'emphasis', index: 1, parentType: 'paragraph'},
    {type: 'text', index: 0, parentType: 'emphasis'}
  ])
})

nodeTest('reverse mode keeps root first and reverses each child list', () => {
  assert.deepEqual(types(result({mode: 'record', reverse: true})), ['root', 'quote', 'paragraph', 'text', 'paragraph', 'text', 'emphasis', 'text', 'text'])
})

nodeTest('matches one node type string', () => {
  assert.deepEqual(types(result({mode: 'record', test: 'text'})), ['text', 'text', 'text', 'text'])
})

nodeTest('matches a list of node types', () => {
  assert.deepEqual(types(result({mode: 'record', test: ['quote', 'emphasis']})), ['emphasis', 'quote'])
})

nodeTest('matches a plain object test', () => {
  assert.deepEqual(types(result({mode: 'record', test: {type: 'paragraph'}})), ['paragraph', 'paragraph'])
})

nodeTest('supports a predicate selected by index', () => {
  assert.deepEqual(types(result({mode: 'record', predicateIndexAtLeast: 1})), ['emphasis', 'text', 'quote'])
})

nodeTest('continues when the visitor returns CONTINUE', () => {
  assert.equal(result({mode: 'continue'}).calls, 9)
})

nodeTest('continues when the visitor returns undefined', () => {
  assert.equal(result({mode: 'undefined'}).calls, 9)
})

nodeTest('skips descendants for a matching node', () => {
  assert.deepEqual(types(result({mode: 'record', skipType: 'paragraph'})), ['root', 'paragraph', 'quote', 'paragraph'])
})

nodeTest('skips descendants in reverse mode', () => {
  assert.deepEqual(types(result({mode: 'record', reverse: true, skipType: 'paragraph'})), ['root', 'quote', 'paragraph', 'paragraph'])
})

nodeTest('exits after the requested callback count', () => {
  const response = result({mode: 'record', exitAfter: 4})
  assert.deepEqual(types(response), ['root', 'paragraph', 'text', 'emphasis'])
  assert.equal(response.calls, 4)
})

nodeTest('exits at the same count in reverse mode', () => {
  assert.deepEqual(types(result({mode: 'record', reverse: true, exitAfter: 3})), ['root', 'quote', 'paragraph'])
})

nodeTest('restarts the current sibling list from an explicit index', () => {
  const response = result({mode: 'record', restartOnceType: 'emphasis'})
  assert.deepEqual(types(response), ['root', 'paragraph', 'text', 'emphasis', 'text', 'text', 'emphasis', 'text', 'text', 'quote', 'paragraph', 'text'])
  assert.equal(response.restartCount, 1)
})

nodeTest('uses an explicit next index to skip a sibling', () => {
  assert.deepEqual(types(result({mode: 'record', jumpAtType: 'paragraph', jumpIndex: 2})), ['root', 'paragraph', 'text', 'emphasis', 'text', 'text'])
})

nodeTest('visits a tree with one scalar child without descending into the scalar', () => {
  assert.deepEqual(types(result({mode: 'record', tree: {type: 'root', children: [{type: 'text', value: 'x'}]}})), ['root', 'text'])
})

nodeTest('visits a leaf root exactly once', () => {
  const response = result({mode: 'record', tree: {type: 'text', value: 'x'}})
  assert.deepEqual(types(response), ['text'])
  assert.equal(response.calls, 1)
})

nodeTest('does not mutate an unmarked tree during a normal walk', () => {
  assert.deepEqual(result({mode: 'record'}).tree, tree)
})

nodeTest('allows a visitor to mutate visited nodes', () => {
  const response = result({mode: 'record', markVisited: true})
  assert.equal(response.tree.children[0].marked, true)
  assert.equal(response.tree.children[0].children[1].marked, true)
})

nodeTest('returns the root callback metadata as undefined values', () => {
  assert.deepEqual(result({mode: 'record', tree: {type: 'root'}}).visits, [{type: 'root'}])
})

nodeTest('handles an empty parent deterministically', () => {
  assert.deepEqual(result({mode: 'record', tree: {type: 'root', children: []}}).visits, [{type: 'root'}])
})

nodeTest('handles unicode and punctuation node values without changing traversal', () => {
  const response = result({mode: 'record', tree: {type: 'root', children: [{type: 'text', value: '你好, cafe — 😀'}]}})
  assert.deepEqual(types(response), ['root', 'text'])
  assert.equal(response.tree.children[0].value, '你好, cafe — 😀')
})

nodeTest('is deterministic across repeated calls', () => {
  const first = types(result({mode: 'record'}))
  for (let index = 0; index < 3; index++) assert.deepEqual(types(result({mode: 'record'})), first)
})

nodeTest('combines a type test, reverse order, and skip action', () => {
  assert.deepEqual(types(result({mode: 'record', test: 'paragraph', reverse: true, skipType: 'paragraph'})), ['paragraph', 'paragraph'])
})

nodeTest('combines a type list and early exit', () => {
  assert.deepEqual(types(result({mode: 'record', test: ['text', 'paragraph'], exitAfter: 3})), ['paragraph', 'text', 'text'])
})

nodeTest('does not call the visitor for unmatched descendants', () => {
  const response = result({mode: 'record', test: 'quote'})
  assert.equal(response.calls, 1)
  assert.deepEqual(response.visits, [{type: 'quote', index: 1, parentType: 'root'}])
})

nodeTest('preserves arbitrary node fields while traversing', () => {
  const response = result({mode: 'record', tree: {type: 'root', data: {source: 'fixture'}, children: [{type: 'text', value: 'x', position: {start: {line: 1}}}]}})
  assert.deepEqual(response.tree.data, {source: 'fixture'})
  assert.deepEqual(response.tree.children[0].position, {start: {line: 1}})
})

nodeTest('reverse traversal is stable for a three-sibling parent', () => {
  assert.deepEqual(types(result({mode: 'record', reverse: true, tree: {type: 'root', children: [{type: 'a'}, {type: 'b'}, {type: 'c'}]}})), ['root', 'c', 'b', 'a'])
})

nodeTest('nested parents retain their immediate callback parent', () => {
  assert.deepEqual(result({mode: 'record'}).visits[4], {type: 'text', index: 0, parentType: 'emphasis'})
})

nodeTest('skip leaves later siblings reachable', () => {
  assert.deepEqual(types(result({mode: 'record', skipType: 'emphasis'})), ['root', 'paragraph', 'text', 'emphasis', 'text', 'quote', 'paragraph', 'text'])
})

nodeTest('the adapter reports a boolean success envelope', () => {
  const response = result({mode: 'record'})
  assert.equal(response.ok, true)
  assert.equal(typeof response.calls, 'number')
  assert.ok(Array.isArray(response.visits))
})
