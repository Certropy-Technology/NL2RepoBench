import assert from 'node:assert/strict'
import test from 'node:test'
import {callCandidate} from './test_client.mjs'

function ok(request) {
  const response = callCandidate(request)
  assert.equal(response.ok, true, response.message ?? response.error)
  return response.value
}

function node(id, children = undefined, extra = {}) {
  const value = {type: id === 'root' ? 'root' : id.startsWith('p') ? 'paragraph' : 'text', id, ...extra}
  if (children !== undefined) value.children = children
  return value
}

function sample() {
  return node('root', [
    node('a', undefined, {value: 'a'}),
    node('p1', [node('b', undefined, {value: 'b'}), node('c', undefined, {value: 'c'})]),
    node('d', undefined, {value: 'd'})
  ])
}

function walk(options = {}) {
  return ok({operation: 'walk', tree: sample(), ...options})
}

function ids(result) {
  return result.events.map((event) => event.id)
}

test('exports the exact public runtime surface', () => {
  assert.deepEqual(ok({operation: 'inventory'}).exports, ['CONTINUE', 'EXIT', 'SKIP', 'visitParents'])
})

test('exports the documented action constants', () => {
  assert.deepEqual(ok({operation: 'inventory'}).constants, {CONTINUE: true, EXIT: false, SKIP: 'skip'})
})

test('exports visitParents as a function', () => {
  assert.equal(ok({operation: 'inventory'}).visitParentsType, 'function')
})

test('has exact package identity and ESM metadata', () => {
  const value = ok({operation: 'inventory'}).package
  assert.deepEqual({name: value.name, version: value.version, type: value.type}, {
    name: 'unist-util-visit-parents', version: '6.0.2', type: 'module'
  })
})

test('declares only the exact runtime dependencies', () => {
  assert.deepEqual(ok({operation: 'inventory'}).package.dependencies, {
    '@types/unist': '3.0.3', 'unist-util-is': '6.0.1'
  })
})

test('does not declare dev dependencies, scripts, or workspaces', () => {
  const value = ok({operation: 'inventory'}).package
  assert.deepEqual([value.devDependencies, value.scripts, value.workspaces], [null, null, null])
})

test('ships declarations for visitParents and action constants', () => {
  const value = ok({operation: 'inventory'})
  assert.deepEqual(
    [value.hasDeclaration, value.declarationExportsVisitParents, value.declarationExportsActions],
    [true, true, true]
  )
})

test('returns undefined', () => {
  assert.equal(walk().returnedUndefined, true)
})

test('walks preorder by default', () => {
  assert.deepEqual(ids(walk()), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('walks reverse preorder when requested', () => {
  assert.deepEqual(ids(walk({reverse: true})), ['root', 'd', 'p1', 'c', 'b', 'a'])
})

test('reports the full ordered ancestor stack', () => {
  const value = walk().events.find((event) => event.id === 'c')
  assert.deepEqual(value.ancestors, ['root', 'p1'])
})

test('reports current sibling indexes', () => {
  const value = walk().events.find((event) => event.id === 'c')
  assert.equal(value.index, 1)
})

test('visits a leaf root once with no ancestors', () => {
  const value = ok({operation: 'walk', tree: {type: 'text', id: 'solo', value: 'x'}})
  assert.deepEqual(value.events, [{id: 'solo', type: 'text', value: 'x', index: null, ancestors: []}])
})

test('treats an explicit null test as no filter', () => {
  assert.deepEqual(ids(walk({test: null})), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('filters by node type string', () => {
  assert.deepEqual(ids(walk({test: 'paragraph'})), ['p1'])
})

test('filters by multiple type strings', () => {
  assert.deepEqual(ids(walk({test: {kind: 'array', values: ['root', 'paragraph']}})), ['root', 'p1'])
})

test('filters by a partial object', () => {
  assert.deepEqual(ids(walk({test: {kind: 'partial', value: {value: 'c'}}})), ['c'])
})

test('combines string and partial-object tests', () => {
  const value = walk({test: {kind: 'array', values: ['paragraph', {kind: 'partial', value: {value: 'd'}}]}})
  assert.deepEqual(ids(value), ['p1', 'd'])
})

test('function tests receive sibling indexes', () => {
  assert.deepEqual(ids(walk({test: {kind: 'index-greater-than', value: 0}})), ['p1', 'c', 'd'])
})

test('function tests receive direct parents', () => {
  assert.deepEqual(ids(walk({test: {kind: 'parent-type', value: 'paragraph'}})), ['b', 'c'])
})

test('function tests can inspect node data', () => {
  const tree = sample()
  tree.children[1].children[0].data = {flag: 'yes'}
  const value = ok({operation: 'walk', tree, test: {kind: 'data-flag', value: 'yes'}})
  assert.deepEqual(ids(value), ['b'])
})

test('filtered reverse traversal preserves reverse preorder', () => {
  assert.deepEqual(ids(walk({test: 'text', reverse: true})), ['d', 'c', 'b', 'a'])
})

test('CONTINUE preserves normal traversal', () => {
  assert.deepEqual(ids(walk({defaultResult: {kind: 'continue'}})), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('a CONTINUE tuple preserves normal traversal', () => {
  assert.deepEqual(ids(walk({defaultResult: {kind: 'tuple', action: 'continue'}})), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('a null visitor result preserves normal traversal', () => {
  assert.deepEqual(ids(walk({defaultResult: {kind: 'null'}})), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('EXIT at the root stops immediately', () => {
  assert.deepEqual(ids(walk({actions: [{when: {id: 'root'}, result: {kind: 'exit'}}]})), ['root'])
})

test('EXIT at a descendant stops the whole traversal', () => {
  assert.deepEqual(ids(walk({actions: [{when: {id: 'b'}, result: {kind: 'exit'}}]})), ['root', 'a', 'p1', 'b'])
})

test('an EXIT tuple stops the whole traversal', () => {
  const actions = [{when: {id: 'p1'}, result: {kind: 'tuple', action: 'exit'}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1'])
})

test('EXIT also stops reverse traversal', () => {
  const actions = [{when: {id: 'c'}, result: {kind: 'exit'}}]
  assert.deepEqual(ids(walk({reverse: true, actions})), ['root', 'd', 'p1', 'c'])
})

test('SKIP omits descendants but continues with siblings', () => {
  const actions = [{when: {id: 'p1'}, result: {kind: 'skip'}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1', 'd'])
})

test('a SKIP tuple omits descendants', () => {
  const actions = [{when: {id: 'p1'}, result: {kind: 'tuple', action: 'skip'}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1', 'd'])
})

test('SKIP has the same child effect in reverse traversal', () => {
  const actions = [{when: {id: 'p1'}, result: {kind: 'skip'}}]
  assert.deepEqual(ids(walk({reverse: true, actions})), ['root', 'd', 'p1', 'a'])
})

test('a numeric index selects the next forward sibling', () => {
  const actions = [{when: {id: 'a'}, result: {kind: 'index', index: 2}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'd'])
})

test('a tuple index selects the next forward sibling', () => {
  const actions = [{when: {id: 'a'}, result: {kind: 'tuple', action: 'continue', index: 2}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'd'])
})

test('an index at children length stops that parent', () => {
  const actions = [{when: {id: 'a'}, result: {kind: 'index', index: 3}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a'])
})

test('a negative index stops that parent', () => {
  const actions = [{when: {id: 'c'}, result: {kind: 'index', index: -1}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1', 'b', 'c', 'd'])
})

test('index zero can revisit earlier siblings', () => {
  const actions = [{when: {id: 'p1', occurrence: 1}, result: {kind: 'index', index: 0}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1', 'b', 'c', 'a', 'p1', 'b', 'c', 'd'])
})

test('reverse traversal uses numeric indexes in reverse order', () => {
  const actions = [{when: {id: 'd'}, result: {kind: 'index', index: 0}}]
  assert.deepEqual(ids(walk({reverse: true, actions})), ['root', 'd', 'a'])
})

test('children appended during a parent visit are traversed', () => {
  const actions = [{when: {id: 'p1'}, mutation: {kind: 'append-child', node: {type: 'text', id: 'x', value: 'x'}}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'p1', 'b', 'c', 'x', 'd'])
})

test('a next sibling inserted during a visit is traversed', () => {
  const actions = [{when: {id: 'a'}, mutation: {kind: 'append-sibling', node: {type: 'text', id: 'x', value: 'x'}}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'x', 'p1', 'b', 'c', 'd'])
})

test('removing a next sibling updates traversal naturally', () => {
  const actions = [{when: {id: 'a'}, mutation: {kind: 'remove-next'}}]
  assert.deepEqual(ids(walk({actions})), ['root', 'a', 'd'])
})

test('removing the current node can return its old index', () => {
  const actions = [{when: {id: 'a'}, mutation: {kind: 'remove-current'}, result: {kind: 'index', index: 0}}]
  const value = walk({actions})
  assert.deepEqual(ids(value), ['root', 'a', 'p1', 'b', 'c', 'd'])
  assert.deepEqual(value.tree.children.map((child) => child.id), ['p1', 'd'])
})

test('removing a previous sibling can return the adjusted index', () => {
  const actions = [{when: {id: 'p1'}, mutation: {kind: 'remove-previous'}, result: {kind: 'index', index: 1}}]
  const value = walk({actions})
  assert.deepEqual(ids(value), ['root', 'a', 'p1', 'b', 'c', 'd'])
  assert.deepEqual(value.tree.children.map((child) => child.id), ['p1', 'd'])
})

test('visitors can mutate the direct parent from ancestors', () => {
  const actions = [{when: {id: 'b'}, mutation: {kind: 'set-parent-data', key: 'seen', value: true}}]
  const value = walk({actions})
  assert.equal(value.tree.children[1].data.seen, true)
})

test('replacing a node still traverses the original node descendants', () => {
  const tree = sample()
  const actions = [{when: {id: 'p1'}, mutation: {kind: 'replace-current', node: {type: 'text', id: 'x', value: 'x'}}}]
  const value = ok({operation: 'walk', tree, actions})
  assert.deepEqual(ids(value), ['root', 'a', 'p1', 'b', 'c', 'd'])
  assert.equal(value.tree.children[1].id, 'x')
})

test('handles a bounded one-thousand-node depth', () => {
  assert.deepEqual(ok({operation: 'deep', depth: 1000}), {count: 1000, deepest: 999})
})

test('throws a TypeError when tree and visitor are missing', () => {
  const response = callCandidate({operation: 'invalid', variant: 'missing-tree'})
  assert.deepEqual([response.ok, response.exceptionType], [false, 'TypeError'])
})

test('throws a TypeError when visitor is missing', () => {
  const response = callCandidate({operation: 'invalid', variant: 'missing-visitor', tree: sample()})
  assert.deepEqual([response.ok, response.exceptionType], [false, 'TypeError'])
})

test('propagates visitor exceptions unchanged', () => {
  const response = callCandidate({operation: 'throw', tree: sample(), id: 'b', message: 'expected boom'})
  assert.deepEqual([response.ok, response.exceptionType, response.message], [false, 'Error', 'expected boom'])
})

test('repeated traversals are deterministic and stateless', () => {
  assert.deepEqual(ids(walk()), ids(walk()))
})
