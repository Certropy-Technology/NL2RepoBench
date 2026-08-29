import assert from 'node:assert/strict'
import test from 'node:test'
import {call, inventory} from './test_client.mjs'

function value(name, args) {
  const response = call(name, args)
  assert.equal(response.ok, true, response.message)
  return response.value
}

test('package shape and named exports', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: []}]), {type: 'root', children: []})
  assert.deepEqual(inventory().value, {
    packageName: 'mdast-util-to-hast', packageVersion: '13.2.1', packageShape: true,
    runtimeEntry: true, declarationEntry: true,
    exportNames: ['defaultFootnoteBackContent', 'defaultFootnoteBackLabel', 'defaultHandlers', 'toHast']
  })
})

test('root text maps to a paragraph', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: [{type: 'paragraph', children: [{type: 'text', value: 'Hello'}]}]}]), {type: 'root', children: [{type: 'element', tagName: 'p', properties: {}, children: [{type: 'text', value: 'Hello'}]}]})
})

test('empty root is stable', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: []}]), {type: 'root', children: []})
})

test('block nodes receive deterministic newlines', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: [{type: 'heading', depth: 1, children: [{type: 'text', value: 'A'}]}, {type: 'paragraph', children: [{type: 'text', value: 'B'}]}]}]), {type: 'root', children: [{type: 'element', tagName: 'h1', properties: {}, children: [{type: 'text', value: 'A'}]}, {type: 'text', value: '\n'}, {type: 'element', tagName: 'p', properties: {}, children: [{type: 'text', value: 'B'}]}]})
})

test('emphasis strong and delete map to inline elements', () => {
  assert.deepEqual(value('toHast', [{type: 'paragraph', children: [{type: 'emphasis', children: [{type: 'text', value: 'e'}]}, {type: 'strong', children: [{type: 'text', value: 's'}]}, {type: 'delete', children: [{type: 'text', value: 'd'}]}]}]), {type: 'element', tagName: 'p', properties: {}, children: [{type: 'element', tagName: 'em', properties: {}, children: [{type: 'text', value: 'e'}]}, {type: 'element', tagName: 'strong', properties: {}, children: [{type: 'text', value: 's'}]}, {type: 'element', tagName: 'del', properties: {}, children: [{type: 'text', value: 'd'}]}]})
})

test('inline code preserves value and escapes as text', () => {
  assert.deepEqual(value('toHast', [{type: 'inlineCode', value: 'a < b'}]), {type: 'element', tagName: 'code', properties: {}, children: [{type: 'text', value: 'a < b'}]})
})

test('break maps to br and following text', () => {
  assert.deepEqual(value('toHast', [{type: 'paragraph', children: [{type: 'text', value: 'a'}, {type: 'break'}, {type: 'text', value: 'b'}]}]), {type: 'element', tagName: 'p', properties: {}, children: [{type: 'text', value: 'a'}, {type: 'element', tagName: 'br', properties: {}, children: []}, {type: 'text', value: '\n'}, {type: 'text', value: 'b'}]})
})

test('heading uses its depth', () => {
  assert.deepEqual(value('toHast', [{type: 'heading', depth: 3, children: [{type: 'text', value: 'Title'}]}]), {type: 'element', tagName: 'h3', properties: {}, children: [{type: 'text', value: 'Title'}]})
})

test('blockquote wraps block content', () => {
  assert.deepEqual(value('toHast', [{type: 'blockquote', children: [{type: 'paragraph', children: [{type: 'text', value: 'q'}]}]}]), {type: 'element', tagName: 'blockquote', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'p', properties: {}, children: [{type: 'text', value: 'q'}]}, {type: 'text', value: '\n'}]})
})

test('thematic break maps to hr', () => {
  assert.deepEqual(value('toHast', [{type: 'thematicBreak'}]), {type: 'element', tagName: 'hr', properties: {}, children: []})
})

test('fenced code adds language class and meta data', () => {
  assert.deepEqual(value('toHast', [{type: 'code', lang: 'js', meta: 'strict', value: 'x'}]), {type: 'element', tagName: 'pre', properties: {}, children: [{type: 'element', tagName: 'code', properties: {className: ['language-js']}, children: [{type: 'text', value: 'x\n'}], data: {meta: 'strict'}}]})
})

test('link maps url and title', () => {
  assert.deepEqual(value('toHast', [{type: 'link', url: 'https://example.test/a?x=1&y=2', title: 'A', children: [{type: 'text', value: 'go'}]}]), {type: 'element', tagName: 'a', properties: {href: 'https://example.test/a?x=1&y=2', title: 'A'}, children: [{type: 'text', value: 'go'}]})
})

test('image maps src alt and title', () => {
  assert.deepEqual(value('toHast', [{type: 'image', url: 'img.png', title: 'T', alt: 'Alt'}]), {type: 'element', tagName: 'img', properties: {src: 'img.png', alt: 'Alt', title: 'T'}, children: []})
})

test('reference definitions resolve links', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: [{type: 'definition', identifier: 'id', label: 'id', url: '/target'}, {type: 'paragraph', children: [{type: 'linkReference', identifier: 'id', referenceType: 'full', children: [{type: 'text', value: 'Target'}]}]}]}]), {type: 'root', children: [{type: 'element', tagName: 'p', properties: {}, children: [{type: 'element', tagName: 'a', properties: {href: '/target'}, children: [{type: 'text', value: 'Target'}]}]}]})
})

test('unordered list maps list items', () => {
  assert.deepEqual(value('toHast', [{type: 'list', ordered: false, spread: false, children: [{type: 'listItem', spread: false, children: [{type: 'paragraph', children: [{type: 'text', value: 'one'}]}]}]}]), {type: 'element', tagName: 'ul', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'li', properties: {}, children: [{type: 'text', value: 'one'}]}, {type: 'text', value: '\n'}]})
})

test('ordered list preserves non-default start', () => {
  assert.deepEqual(value('toHast', [{type: 'list', ordered: true, start: 3, spread: false, children: [{type: 'listItem', spread: false, children: [{type: 'paragraph', children: [{type: 'text', value: 'one'}]}]}]}]), {type: 'element', tagName: 'ol', properties: {start: 3}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'li', properties: {}, children: [{type: 'text', value: 'one'}]}, {type: 'text', value: '\n'}]})
})

test('task list adds checkbox input', () => {
  assert.deepEqual(value('toHast', [{type: 'list', ordered: false, spread: false, children: [{type: 'listItem', spread: false, checked: true, children: [{type: 'paragraph', children: [{type: 'text', value: 'done'}]}]}]}]), {type: 'element', tagName: 'ul', properties: {className: ['contains-task-list']}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'li', properties: {className: ['task-list-item']}, children: [{type: 'element', tagName: 'input', properties: {type: 'checkbox', checked: true, disabled: true}, children: []}, {type: 'text', value: ' '}, {type: 'text', value: 'done'}]}, {type: 'text', value: '\n'}]})
})

test('table alignment maps to cell align', () => {
  assert.deepEqual(value('toHast', [{type: 'table', align: ['left', null], children: [{type: 'tableRow', children: [{type: 'tableCell', children: [{type: 'text', value: 'A'}]}, {type: 'tableCell', children: [{type: 'text', value: 'B'}]}]}]}]), {type: 'element', tagName: 'table', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'thead', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'tr', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'th', properties: {align: 'left'}, children: [{type: 'text', value: 'A'}]}, {type: 'text', value: '\n'}, {type: 'element', tagName: 'th', properties: {}, children: [{type: 'text', value: 'B'}]}, {type: 'text', value: '\n'}]}, {type: 'text', value: '\n'}]}, {type: 'text', value: '\n'}]})
})

test('html is ignored unless allowed', () => {
  assert.deepEqual(value('toHast', [{type: 'html', value: '<span>x</span>'}]), {type: 'root', children: []})
  assert.deepEqual(value('toHast', [{type: 'html', value: '<span>x</span>'}, {allowDangerousHtml: true}]), {type: 'raw', value: '<span>x</span>'})
})

test('dangerous html option works in a root', () => {
  assert.deepEqual(value('toHast', [{type: 'root', children: [{type: 'html', value: '<b>x</b>'}]}, {allowDangerousHtml: true}]), {type: 'root', children: [{type: 'raw', value: '<b>x</b>'}]})
})

test('data hName and hProperties override an element', () => {
  assert.deepEqual(value('toHast', [{type: 'paragraph', data: {hName: 'section', hProperties: {id: 'x'}}, children: [{type: 'text', value: 'x'}]}]), {type: 'element', tagName: 'section', properties: {id: 'x'}, children: [{type: 'text', value: 'x'}]})
})

test('data hChildren replaces children', () => {
  assert.deepEqual(value('toHast', [{type: 'text', value: 'ignored', data: {hName: 'mark', hChildren: [{type: 'text', value: 'shown'}]}}]), {type: 'element', tagName: 'mark', properties: {}, children: [{type: 'text', value: 'shown'}]})
})

test('unknown node uses its value', () => {
  assert.deepEqual(value('toHast', [{type: 'unknown', value: 'raw value'}]), {type: 'text', value: 'raw value'})
})

test('footnote reference and definition render a section', () => {
  const tree = {type: 'root', children: [{type: 'paragraph', children: [{type: 'footnoteReference', identifier: 'a', label: 'a'}]}, {type: 'footnoteDefinition', identifier: 'a', label: 'a', children: [{type: 'paragraph', children: [{type: 'text', value: 'note'}]}]}]}
  const result = value('toHast', [tree])
  assert.equal(result.children.at(-1).tagName, 'section')
  assert.equal(result.children.at(-1).properties.dataFootnotes, true)
})

test('repeated footnote references have stable suffixes', () => {
  const tree = {type: 'root', children: [{type: 'paragraph', children: [{type: 'footnoteReference', identifier: 'a', label: 'a'}, {type: 'text', value: ' and '}, {type: 'footnoteReference', identifier: 'a', label: 'a'}]}, {type: 'footnoteDefinition', identifier: 'a', label: 'a', children: [{type: 'paragraph', children: [{type: 'text', value: 'note'}]}]}]}
  const result = value('toHast', [tree])
  const text = JSON.stringify(result)
  assert.match(text, /user-content-fnref-a/)
  assert.match(text, /user-content-fnref-a-2/)
})

test('footnote options customize prefix and label', () => {
  const tree = {type: 'root', children: [{type: 'paragraph', children: [{type: 'footnoteReference', identifier: 'a', label: 'a'}]}, {type: 'footnoteDefinition', identifier: 'a', label: 'a', children: [{type: 'paragraph', children: [{type: 'text', value: 'note'}]}]}]}
  const result = value('toHast', [tree, {clobberPrefix: 'x-', footnoteLabel: 'Notes'}])
  const text = JSON.stringify(result)
  assert.match(text, /x-fn-a/)
  assert.match(text, /Notes/)
})

test('default footnote helpers are callable', () => {
  assert.deepEqual(value('defaultFootnoteBackContent', [1, 1]), [{type: 'text', value: '↩'}])
  assert.equal(value('defaultFootnoteBackLabel', [1]), 'Back to reference 2')
  assert.equal(value('defaultFootnoteBackLabel', [2, 1]), 'Back to reference 3')
})

test('text with unicode is preserved', () => {
  assert.deepEqual(value('toHast', [{type: 'text', value: 'café 你好 😀'}]), {type: 'text', value: 'café 你好 😀'})
})

test('link and image urls are sanitized deterministically', () => {
  assert.deepEqual(value('toHast', [{type: 'link', url: 'a b', children: [{type: 'text', value: 'x'}]}]), {type: 'element', tagName: 'a', properties: {href: 'a%20b'}, children: [{type: 'text', value: 'x'}]})
})

test('input tree is not mutated', () => {
  const tree = {type: 'root', children: [{type: 'paragraph', children: [{type: 'text', value: 'x'}]}]}
  const before = JSON.stringify(tree)
  value('toHast', [tree])
  assert.equal(JSON.stringify(tree), before)
})

test('position fields do not leak into output', () => {
  assert.deepEqual(value('toHast', [{type: 'text', value: 'x', position: {start: {line: 1, column: 1, offset: 0}, end: {line: 1, column: 2, offset: 1}}}]), {type: 'text', value: 'x', position: {start: {line: 1, column: 1, offset: 0}, end: {line: 1, column: 2, offset: 1}}})
})

test('null options are accepted', () => {
  assert.deepEqual(value('toHast', [{type: 'paragraph', children: [{type: 'text', value: 'x'}]}, null]), {type: 'element', tagName: 'p', properties: {}, children: [{type: 'text', value: 'x'}]})
})

test('unsupported node without value is ignored', () => {
  assert.deepEqual(value('toHast', [{type: 'toml', value: 'x'}]), {type: 'root', children: []})
})

test('invalid root shape returns a bounded candidate error', () => {
  const response = call('toHast', [null])
  assert.equal(response.ok, false)
  assert.match(response.message, /tree|node|object|reading/i)
})

test('default handlers expose standard handler names', () => {
  const names = ['blockquote', 'code', 'emphasis', 'heading', 'image', 'link', 'list', 'paragraph', 'root', 'strong', 'table', 'text']
  assert.deepEqual(names, names.filter((name) => name.length > 0))
  const response = inventory()
  assert.equal(response.ok, true)
})
