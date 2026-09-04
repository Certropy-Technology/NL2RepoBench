import assert from 'node:assert/strict'
import test from 'node:test'
import {call, inventory} from './test_client.mjs'

function value(name, args) {
  const response = call(name, args)
  assert.equal(response.ok, true, response.message)
  return response.value
}
function program(tree, options) { return value('toEstree', options === undefined ? [tree] : [tree, options]) }
function expression(tree, options) { return program(tree, options).body.at(-1)?.expression }

test('package-shape', () => {
  assert.deepEqual(inventory().value, {packageName: 'hast-util-to-estree', packageVersion: '3.1.3', packageShape: true, exportNames: ['defaultHandlers', 'toEstree'], toEstree: true, defaultHandlers: true, handlerNames: ['comment', 'doctype', 'element', 'mdxFlowExpression', 'mdxJsxFlowElement', 'mdxJsxTextElement', 'mdxTextExpression', 'mdxjsEsm', 'root', 'text']})
})
test('default-handlers', () => {
  assert.equal(inventory().value.defaultHandlers, true)
})
test('non-node-error', () => { assert.throws(() => program({}), /Cannot handle value/) })
test('unknown-node-error', () => { assert.throws(() => program({type: 'unknown'}), /Cannot handle unknown node/) })
test('empty-element', () => { assert.equal(expression({type: 'element', tagName: 'div', properties: {}, children: []}).type, 'JSXElement') })
test('root-fragment', () => { assert.equal(expression({type: 'root', children: []}).type, 'JSXFragment') })
test('root-text', () => { assert.equal(expression({type: 'text', value: 'hello'}).type, 'JSXFragment') })
test('doctype', () => { assert.deepEqual(program({type: 'doctype'}).body, []) })
test('text', () => { const e = expression({type: 'text', value: 'hello'}); assert.equal(e.children[0].expression.value, 'hello') })
test('comment', () => { const p = program({type: 'comment', value: 'note'}); assert.equal(p.comments[0].value, 'note') })
test('nested-element', () => { const e = expression({type: 'element', tagName: 'p', properties: {}, children: [{type: 'element', tagName: 'b', properties: {}, children: []}]}); assert.equal(e.children[0].type, 'JSXElement') })
test('boolean-property', () => { const a = expression({type: 'element', tagName: 'input', properties: {disabled: true}, children: []}).openingElement.attributes[0]; assert.equal(a.name.name, 'disabled'); assert.equal(a.value, null) })
test('literal-property', () => { const a = expression({type: 'element', tagName: 'a', properties: {title: 'x'}, children: []}).openingElement.attributes[0]; assert.equal(a.value.value, 'x') })
test('omitted-property', () => { assert.equal(expression({type: 'element', tagName: 'x', properties: {title: null}, children: []}).openingElement.attributes.length, 0) })
test('space-list', () => { const a = expression({type: 'element', tagName: 'x', properties: {className: ['a', 'b']}, children: []}).openingElement.attributes[0]; assert.equal(a.value.value, 'a b') })
test('comma-list', () => { const a = expression({type: 'element', tagName: 'x', properties: {accept: ['a', 'b']}, children: []}).openingElement.attributes[0]; assert.equal(a.value.value, 'a, b') })
test('non-identifier-property', () => { const a = expression({type: 'element', tagName: 'x', properties: {'b+': 'c'}, children: []}).openingElement.attributes[0]; assert.equal(a.type, 'JSXSpreadAttribute') })
test('dom-style', () => { const a = expression({type: 'element', tagName: 'x', properties: {style: 'background-color:red'}, children: []}).openingElement.attributes[0]; assert.equal(a.name.name, 'style'); assert.equal(a.value.expression.properties[0].key.name, 'backgroundColor') })
test('css-style', () => { const a = expression({type: 'element', tagName: 'x', properties: {style: 'background-color:red'}, children: []}, {stylePropertyNameCase: 'css'}).openingElement.attributes[0]; assert.equal(a.value.expression.properties[0].key.value, 'background-color') })
test('invalid-style', () => { assert.throws(() => program({type: 'element', tagName: 'x', properties: {style: 'invalid'}, children: []}), /style/i) })
test('table-align', () => { const a = expression({type: 'element', tagName: 'th', properties: {align: 'center'}, children: []}).openingElement.attributes[0]; assert.equal(a.name.name, 'style') })
test('table-align-disabled', () => { const a = expression({type: 'element', tagName: 'th', properties: {align: 'center'}, children: []}, {tableCellAlignToStyle: false}).openingElement.attributes[0]; assert.equal(a.name.name, 'align') })
test('svg-space', () => { const a = expression({type: 'element', tagName: 'svg', properties: {viewBox: '0 0 1 1'}, children: []}).openingElement.attributes[0]; assert.equal(a.name.name, 'viewBox') })
test('nested-svg-space', () => { const e = expression({type: 'element', tagName: 'svg', properties: {}, children: [{type: 'element', tagName: 'path', properties: {strokeWidth: 1}, children: []}]}); assert.equal(e.children[0].openingElement.attributes[0].name.name, 'strokeWidth') })
test('explicit-svg-space', () => { const a = expression({type: 'element', tagName: 'x', properties: {g1: [1, 2]}, children: []}, {space: 'svg'}).openingElement.attributes[0]; assert.equal(a.value.value, '1, 2') })
test('table-whitespace', () => { const e = expression({type: 'element', tagName: 'table', properties: {}, children: [{type: 'text', value: '\n'}, {type: 'element', tagName: 'tr', properties: {}, children: []}, {type: 'text', value: '\n'}]}); assert.equal(e.children.length, 1) })
test('html-attribute-case', () => { const a = expression({type: 'element', tagName: 'x', properties: {className: ['a', 'b']}, children: []}, {elementAttributeNameCase: 'html'}).openingElement.attributes[0]; assert.equal(a.name.name, 'class') })
test('position', () => { const p = program({type: 'element', tagName: 'x', properties: {}, children: [], position: {start: {line: 2, column: 3, offset: 10}, end: {line: 2, column: 7, offset: 14}}}); assert.equal(p.start, 10); assert.equal(p.loc.start.line, 2); assert.equal(p.loc.start.column, 2); assert.deepEqual(p.range, [10, 14]) })
test('data', () => { const e = expression({type: 'element', tagName: 'x', properties: {}, children: [], data: {marker: 'yes'}}); assert.equal(e.data.marker, 'yes') })
test('determinism', () => { const tree = {type: 'root', children: [{type: 'element', tagName: 'x', properties: {}, children: []}]}; assert.deepEqual(program(tree), program(tree)); assert.deepEqual(tree, {type: 'root', children: [{type: 'element', tagName: 'x', properties: {}, children: []}]}) })
test('mdx-expression', () => { const e = expression({type: 'mdxTextExpression', data: {estree: {type: 'Program', body: [], sourceType: 'module'}}}); assert.equal(e.type, 'JSXFragment') })
test('mdx-jsx', () => { const e = expression({type: 'mdxJsxTextElement', name: 'Component', attributes: [], children: []}); assert.equal(e.type, 'JSXElement') })
test('mdx-esm', () => { const p = program({type: 'root', children: [{type: 'mdxjsEsm', data: {estree: {type: 'Program', body: [{type: 'ImportDeclaration', specifiers: [], source: {type: 'Literal', value: 'x'}}], sourceType: 'module'}}}]}); assert.equal(p.body[0].type, 'ImportDeclaration') })
