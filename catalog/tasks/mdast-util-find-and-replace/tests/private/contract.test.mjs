import assert from 'node:assert/strict'
import test from 'node:test'
import {scenario} from './test_client.mjs'

const text = (value, extra = {}) => ({type: 'text', value, ...extra})
const paragraph = (...children) => ({type: 'paragraph', children})
const root = (...children) => ({type: 'root', children})
const stringFind = (value) => ({kind: 'string', value})
const regexFind = (source, flags = '') => ({kind: 'regex', source, flags})
const pair = (find, replace) => replace === undefined ? {find} : {find, replace}
const transform = (tree, pairs, extra = {}) => scenario('transform', {tree, pairs, ...extra})

test('package is scripts-free ESM with the exact public surface and dependency pins', () => {
  const value = scenario('inventory')
  assert.deepEqual(value, {
    name: 'mdast-util-find-and-replace',
    version: '3.0.2',
    type: 'module',
    exports: ['findAndReplace'],
    callable: true,
    typesPresent: true,
    dependencies: {
      '@types/mdast': '4.0.4',
      'escape-string-regexp': '5.0.0',
      'unist-util-is': '6.0.1',
      'unist-util-visit-parents': '6.0.2'
    },
    scriptNames: [],
    workspacesPresent: false
  })
})

test('findAndReplace returns undefined and mutates the supplied tree', () => {
  const value = transform(paragraph(text('alpha')), [pair(stringFind('alpha'), {kind: 'string', value: 'beta'})], {form: 'tuple'})
  assert.equal(value.resultIsUndefined, true)
  assert.deepEqual(value.tree, paragraph(text('beta')))
})

test('invalid boolean replacement lists throw the documented TypeError', () => {
  const value = scenario('invalid', {list: true})
  assert.equal(value.threw, true)
  assert.equal(value.type, 'TypeError')
  assert.match(value.message, /Expected find and replace tuple or list of tuples/)
})

test('invalid object replacement lists throw the documented TypeError', () => {
  const value = scenario('invalid', {list: {find: 'x'}})
  assert.equal(value.threw, true)
  assert.equal(value.type, 'TypeError')
})

test('string find values are treated literally rather than as regex source', () => {
  const value = transform(paragraph(text('a.b..c')), [pair(stringFind('.'), {kind: 'string', value: 'X'})])
  assert.deepEqual(value.tree, paragraph(text('a'), text('X'), text('b'), text('X'), text('X'), text('c')))
})

test('an omitted replacement removes every string match', () => {
  const value = transform(paragraph(text('one x two x three')), [pair(stringFind(' x'))])
  assert.deepEqual(value.tree, paragraph(text('one'), text(' two'), text(' three')))
})

test('a null replacement removes a match', () => {
  const value = transform(paragraph(text('abc')), [pair(stringFind('b'), {kind: 'null'})])
  assert.deepEqual(value.tree, paragraph(text('a'), text('c')))
})

test('an undefined callback result removes a match', () => {
  const value = transform(paragraph(text('abc')), [pair(stringFind('b'), {kind: 'undefined'})])
  assert.deepEqual(value.tree, paragraph(text('a'), text('c')))
})

test('an empty string replacement removes a match', () => {
  const value = transform(paragraph(text('abc')), [pair(stringFind('b'), {kind: 'empty'})])
  assert.deepEqual(value.tree, paragraph(text('a'), text('c')))
})

test('a string replacement becomes a text node', () => {
  const value = transform(paragraph(text('before target after')), [pair(stringFind('target'), {kind: 'string', value: 'done'})])
  assert.deepEqual(value.tree, paragraph(text('before '), text('done'), text(' after')))
})

test('a non-global regular expression replaces only its first match per text node', () => {
  const value = transform(paragraph(text('aba aba')), [pair(regexFind('a'), {kind: 'string', value: 'X'})])
  assert.deepEqual(value.tree, paragraph(text('X'), text('ba aba')))
})

test('a global regular expression replaces every match in a text node', () => {
  const value = transform(paragraph(text('aba aba')), [pair(regexFind('a', 'g'), {kind: 'string', value: 'X'})])
  assert.deepEqual(value.tree, paragraph(text('X'), text('b'), text('X'), text(' '), text('X'), text('b'), text('X')))
})

test('regular expression flags such as case-insensitive and unicode are honored', () => {
  const value = transform(paragraph(text('A a A')), [pair(regexFind('a', 'giu'), {kind: 'string', value: 'x'})])
  assert.deepEqual(value.tree, paragraph(text('x'), text(' '), text('x'), text(' '), text('x')))
})

test('capture groups are supplied to replacement callbacks in order', () => {
  const value = transform(paragraph(text('name: Ada')), [pair(regexFind('(name):\\s+(\\w+)', 'g'), {kind: 'capture-template', template: '$2/$1/$0'})])
  assert.deepEqual(value.tree, paragraph(text('Ada/name/name: Ada')))
})

test('match info exposes whole match, captures, index, and input', () => {
  const value = transform(paragraph(text('xx-ab-yy')), [pair(regexFind('(a)(b)', 'g'), {kind: 'match-node', nodeType: 'emphasis'})])
  assert.deepEqual(value.tree.children[1].data, {
    whole: 'ab', captures: ['a', 'b'], index: 3, input: 'xx-ab-yy', stackTypes: ['paragraph', 'text']
  })
})

test('match info stack lists all ancestors followed by the text node', () => {
  const tree = root({type: 'blockquote', children: [paragraph({type: 'emphasis', children: [text('hit')]})]})
  const value = transform(tree, [pair(stringFind('hit'), {kind: 'match-node', nodeType: 'strong'})])
  assert.deepEqual(value.tree.children[0].children[0].children[0].children[0].data.stackTypes,
    ['root', 'blockquote', 'paragraph', 'emphasis', 'text'])
})

test('a callback can replace a match with one phrasing node', () => {
  const replacement = {type: 'delete', children: [{type: 'break'}]}
  const value = transform(paragraph(text('x')), [pair(stringFind('x'), {kind: 'callback-node', value: replacement})])
  assert.deepEqual(value.tree, paragraph(replacement))
})

test('a callback can replace a match with multiple phrasing nodes', () => {
  const replacements = [{type: 'delete', children: []}, {type: 'break'}]
  const value = transform(paragraph(text('x')), [pair(stringFind('x'), {kind: 'callback-nodes', value: replacements})])
  assert.deepEqual(value.tree, paragraph(...replacements))
})

test('returning false leaves every rejected match unchanged', () => {
  const tree = paragraph(text('alpha alpha'))
  const value = transform(tree, [pair(stringFind('alpha'), {kind: 'callback-false'})])
  assert.deepEqual(value.tree, tree)
})

test('false resets global matching so a later overlapping match can succeed', () => {
  const value = transform(root(text(':1:2:')), [pair(regexFind(':(\\d+):', 'g'), {
    kind: 'conditional', when: ':2:', then: {kind: 'node', value: {type: 'strong', children: [text('2')]}}
  })])
  assert.deepEqual(value.tree, root(text(':1'), {type: 'strong', children: [text('2')]}))
})

test('one pair does not recurse into the text it just inserted', () => {
  const value = transform(paragraph(text('asd.')), [pair(stringFind('asd'), {kind: 'callback-string', value: 'asd'})])
  assert.deepEqual(value.tree, paragraph(text('asd'), text('.')))
})

test('a later pair processes text inserted by an earlier pair', () => {
  const value = transform(paragraph(text('first')), [
    pair(stringFind('first'), {kind: 'callback-node', value: {type: 'emphasis', children: [text('second')]}}),
    pair(stringFind('second'), {kind: 'string', value: 'done'})
  ])
  assert.deepEqual(value.tree, paragraph({type: 'emphasis', children: [text('done')]}))
})

test('an empty list is a no-op', () => {
  const tree = root(paragraph(text('unchanged')))
  assert.deepEqual(transform(tree, []).tree, tree)
})

test('ignore as a node type skips text below matching ancestors', () => {
  const tree = paragraph({type: 'emphasis', children: [text('x')]}, {type: 'strong', children: [text('x')]})
  const value = transform(tree, [pair(stringFind('x'), {kind: 'string', value: 'y'})], {ignore: {kind: 'type', value: 'strong'}})
  assert.deepEqual(value.tree, paragraph({type: 'emphasis', children: [text('y')]}, {type: 'strong', children: [text('x')]}))
})

test('ignore as a partial node object skips matching ancestors', () => {
  const tree = paragraph({type: 'emphasis', id: 'skip', children: [text('x')]}, {type: 'emphasis', id: 'keep', children: [text('x')]})
  const value = transform(tree, [pair(stringFind('x'), {kind: 'string', value: 'y'})], {ignore: {kind: 'object', value: {type: 'emphasis', id: 'skip'}}})
  assert.equal(value.tree.children[0].children[0].value, 'x')
  assert.equal(value.tree.children[1].children[0].value, 'y')
})

test('ignore as an array combines multiple tests', () => {
  const tree = paragraph({type: 'emphasis', children: [text('x')]}, {type: 'strong', children: [text('x')]}, {type: 'delete', children: [text('x')]})
  const value = transform(tree, [pair(stringFind('x'), {kind: 'string', value: 'y'})], {ignore: {kind: 'array', value: ['emphasis', 'strong']}})
  assert.deepEqual(value.tree, paragraph({type: 'emphasis', children: [text('x')]}, {type: 'strong', children: [text('x')]}, {type: 'delete', children: [text('y')]}))
})

test('ignore accepts a predicate based on ancestor type', () => {
  const tree = paragraph({type: 'strong', children: [text('x')]}, text('x'))
  const value = transform(tree, [pair(stringFind('x'), {kind: 'string', value: 'y'})], {ignore: {kind: 'predicate-type', value: 'strong'}})
  assert.deepEqual(value.tree, paragraph({type: 'strong', children: [text('x')]}, text('y')))
})

test('ignore predicates receive ancestor index and parent', () => {
  const tree = root(paragraph(text('x')), paragraph(text('x')))
  const value = transform(tree, [pair(stringFind('x'), {kind: 'string', value: 'y'})], {ignore: {kind: 'predicate-index-parent', index: 1, parentType: 'root'}})
  assert.deepEqual(value.tree, root(paragraph(text('y')), paragraph(text('x'))))
})

test('matches can cover part of one text value', () => {
  const value = transform(paragraph(text('emphasis')), [pair(regexFind('mp', 'g'), {kind: 'string', value: 'MP'})])
  assert.deepEqual(value.tree, paragraph(text('e'), text('MP'), text('hasis')))
})

test('matches never span adjacent text nodes', () => {
  const tree = paragraph(text('ab'), text('cd'))
  assert.deepEqual(transform(tree, [pair(stringFind('bc'), {kind: 'string', value: 'X'})]).tree, tree)
})

test('only text nodes are searched', () => {
  const tree = paragraph({type: 'inlineCode', value: 'target'}, {type: 'image', url: 'target', alt: 'target'}, text('target'))
  const value = transform(tree, [pair(stringFind('target'), {kind: 'string', value: 'done'})])
  assert.deepEqual(value.tree, paragraph({type: 'inlineCode', value: 'target'}, {type: 'image', url: 'target', alt: 'target'}, text('done')))
})

test('nested text nodes are visited in preorder', () => {
  const tree = root(paragraph(text('x'), {type: 'emphasis', children: [text('x')]}, text('x')))
  const value = transform(tree, [pair(stringFind('x'), {kind: 'match-node', nodeType: 'strong'})])
  assert.deepEqual(value.tree.children[0].children.map((node) => node.type), ['strong', 'emphasis', 'strong'])
  assert.deepEqual(value.tree.children[0].children[1].children.map((node) => node.type), ['strong'])
})

test('a text node without a parent is not replaced', () => {
  const tree = text('target')
  assert.deepEqual(transform(tree, [pair(stringFind('target'), {kind: 'string', value: 'done'})]).tree, tree)
})

test('all matching text siblings are replaced without skipping later siblings', () => {
  const value = transform(paragraph(text('x'), text('x'), text('x')), [pair(stringFind('x'), {kind: 'string', value: 'y'})])
  assert.deepEqual(value.tree, paragraph(text('y'), text('y'), text('y')))
})

test('a match at the start does not create a leading empty text node', () => {
  const value = transform(paragraph(text('x-tail')), [pair(stringFind('x'), {kind: 'string', value: 'y'})])
  assert.deepEqual(value.tree, paragraph(text('y'), text('-tail')))
})

test('a match at the end does not create a trailing empty text node', () => {
  const value = transform(paragraph(text('head-x')), [pair(stringFind('x'), {kind: 'string', value: 'y'})])
  assert.deepEqual(value.tree, paragraph(text('head-'), text('y')))
})

test('adjacent matches do not create empty text nodes between replacements', () => {
  const value = transform(paragraph(text('xx')), [pair(stringFind('x'), {kind: 'string', value: 'y'})])
  assert.deepEqual(value.tree, paragraph(text('y'), text('y')))
})

test('removing a complete text value removes that child from its parent', () => {
  const value = transform(paragraph(text('x')), [pair(stringFind('x'), {kind: 'null'})])
  assert.deepEqual(value.tree, paragraph())
})

test('several nonoverlapping string pairs produce deterministic output', () => {
  const value = transform(paragraph(text('emphasis importance code')), [
    pair(stringFind('importance'), {kind: 'callback-node', value: {type: 'strong', children: [text('importance')]}}),
    pair(stringFind('code'), {kind: 'callback-node', value: {type: 'inlineCode', value: 'code'}}),
    pair(stringFind('emphasis'), {kind: 'callback-node', value: {type: 'emphasis', children: [text('emphasis')]}})
  ])
  assert.deepEqual(value.tree.children.map((node) => node.type), ['emphasis', 'text', 'strong', 'text', 'inlineCode'])
})

test('pair order is observable when later pairs match earlier output', () => {
  const forward = transform(paragraph(text('a')), [pair(stringFind('a'), {kind: 'string', value: 'b'}), pair(stringFind('b'), {kind: 'string', value: 'c'})])
  const reverse = transform(paragraph(text('a')), [pair(stringFind('b'), {kind: 'string', value: 'c'}), pair(stringFind('a'), {kind: 'string', value: 'b'})])
  assert.deepEqual(forward.tree, paragraph(text('c')))
  assert.deepEqual(reverse.tree, paragraph(text('b')))
})

test('global regex state resets before each text node', () => {
  const value = transform(paragraph(text('aba'), text('aba')), [pair(regexFind('a', 'g'), {kind: 'string', value: 'x'})])
  assert.deepEqual(value.tree, paragraph(text('x'), text('b'), text('x'), text('x'), text('b'), text('x')))
})

test('a non-global regex handles the first match in every text node', () => {
  const value = transform(paragraph(text('aa'), text('aa')), [pair(regexFind('a'), {kind: 'string', value: 'x'})])
  assert.deepEqual(value.tree, paragraph(text('x'), text('a'), text('x'), text('a')))
})

test('optional unmatched captures reach callbacks as undefined', () => {
  const value = transform(paragraph(text('b')), [pair(regexFind('(a)?b', 'g'), {kind: 'match-node', nodeType: 'emphasis'})])
  assert.deepEqual(value.tree.children[0].data.captures, [null])
})

test('match indexes count JavaScript UTF-16 code units', () => {
  const value = transform(paragraph(text('x😀a')), [pair(regexFind('a', 'u'), {kind: 'match-node', nodeType: 'emphasis'})])
  assert.equal(value.tree.children[1].data.index, 3)
})

test('unaffected parent and sibling node data remain intact', () => {
  const tree = paragraph(text('x', {position: {start: {line: 1, column: 1}}}), {type: 'image', url: '/x', data: {id: 1}})
  tree.data = {role: 'content'}
  const value = transform(tree, [pair(stringFind('missing'), {kind: 'string', value: 'y'})])
  assert.deepEqual(value.tree, tree)
})

test('replacement nodes preserve caller-provided data fields', () => {
  const replacement = {type: 'link', url: '/user/ada', title: null, data: {mention: true}, children: [text('@ada')]}
  const value = transform(paragraph(text('@ada')), [pair(stringFind('@ada'), {kind: 'callback-node', value: replacement})])
  assert.deepEqual(value.tree, paragraph(replacement))
})

test('single tuple form supports regex find and callback replacement', () => {
  const value = transform(paragraph(text('v12')), [pair(regexFind('v(\\d+)', 'g'), {kind: 'capture-template', template: '$1'})], {form: 'tuple'})
  assert.deepEqual(value.tree, paragraph(text('12')))
})

test('callback string results are normalized to text nodes', () => {
  const value = transform(paragraph(text('a-b')), [pair(stringFind('-'), {kind: 'callback-string', value: ' / '})])
  assert.deepEqual(value.tree, paragraph(text('a'), text(' / '), text('b')))
})
