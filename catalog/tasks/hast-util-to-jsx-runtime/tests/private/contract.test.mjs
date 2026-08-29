import assert from 'node:assert/strict'
import test from 'node:test'
import {callCandidate} from './test_client.mjs'

let sequence = 0
const root = (...children) => ({type: 'root', children})
const text = (value) => ({type: 'text', value})
const element = (tagName, properties = {}, children = []) => ({type: 'element', tagName, properties, children})
const transform = (tree, options = {}, extra = {}) => callCandidate({id: `case-${++sequence}`, operation: 'transform', tree, options, ...extra})
const errorFor = (tree, options, extra = {}) => callCandidate({id: `case-${++sequence}`, operation: 'transform', tree, options, ...extra})

test('production element creation and primitive text', () => {
  assert.deepEqual(transform(element('p', {title: 'hello'}, [text('world')])), {
    id: 'case-1', success: true, data: {type: 'p', props: {title: 'hello', children: 'world'}}
  })
})

test('root chooses jsxs for multiple children and creates deterministic keys', () => {
  const result = transform(root(element('span', {}, [text('a')]), element('span', {}, [text('b')]))).data
  assert.equal(result.type, 'Fragment')
  assert.deepEqual(result.props.children.map((item) => item.key), ['span-0', 'span-1'])
})

test('root text is wrapped in Fragment', () => {
  assert.deepEqual(transform(root(text('plain'))).data, {type: 'Fragment', props: {children: 'plain'}})
})

test('development runtime receives source metadata and static-child flag', () => {
  const result = transform(element('h1', {}, [text('title')]), {}, {mode: 'development'}).data
  assert.equal(result.dev.isStaticChildren, false)
  assert.deepEqual(result.dev.source, {})
})

test('missing Fragment is rejected', () => {
  assert.throws(() => errorFor(root(), {jsx: true}, {omit: ['Fragment']}), /Expected `Fragment` in options/)
})

test('missing production jsx is rejected', () => {
  assert.throws(() => errorFor(root(), {}, {omit: ['jsx']}), /Expected `jsx` in production options/)
})

test('missing production jsxs is rejected', () => {
  assert.throws(() => errorFor(root(), {jsx: true}, {omit: ['jsxs']}), /Expected `jsxs` in production options/)
})

test('missing development jsxDEV is rejected', () => {
  assert.throws(() => errorFor(root(), {development: true}, {omit: ['jsxDEV']}), /Expected `jsxDEV` in options when `development: true`/)
})

test('HTML properties map React names and ignore nullish values', () => {
  const props = transform(element('label', {className: ['a', 'b'], htmlFor: 'field', hidden: true, title: null}), {passKeys: false}).data.props
  assert.deepEqual(props, {className: 'a b', htmlFor: 'field', hidden: true})
})

test('comma-separated and space-separated property arrays use their schemas', () => {
  const props = transform(element('input', {accept: ['image/png', 'image/jpeg'], className: ['wide', 'active']}), {passKeys: false}).data.props
  assert.equal(props.accept, 'image/png, image/jpeg')
  assert.equal(props.className, 'wide active')
})

test('style strings become DOM-cased style objects', () => {
  const props = transform(element('div', {style: 'color: red; margin-top: 2px'}), {passKeys: false}).data.props
  assert.deepEqual(props.style, {color: 'red', marginTop: '2px'})
})

test('invalid styles raise a VFileMessage unless ignored', () => {
  assert.throws(() => errorFor(element('div', {style: 'color'}), {passKeys: false}), /Cannot parse `style` attribute/)
  const props = transform(element('div', {style: 'color'}), {passKeys: false, ignoreInvalidStyle: true}).data.props
  assert.deepEqual(props.style, {})
})

test('SVG traversal uses SVG property information', () => {
  const result = transform(element('svg', {viewBox: '0 0 10 10'}, [element('circle', {strokeWidth: 2})]), {passKeys: false}).data
  assert.equal(result.type, 'svg')
  assert.equal(result.props.viewBox, '0 0 10 10')
  assert.equal(result.props.children.type, 'circle')
  assert.equal(result.props.children.props.strokeWidth, 2)
})

test('table elements filter whitespace-only children', () => {
  const result = transform(element('table', {}, [text('\n  '), element('tbody', {}, [text(' '), element('tr', {}, [])]), text('\n')])).data
  assert.equal(result.props.children.type, 'tbody')
  assert.equal(result.props.children.props.children.type, 'tr')
})

test('passKeys false omits generated child keys', () => {
  const result = transform(root(element('div'), element('div')), {passKeys: false}).data
  assert.equal(Object.hasOwn(result.props.children[0], 'key'), false)
})

test('mapped components can receive the original node', () => {
  const input = element('Alert', {kind: 'warning'}, [text('watch')])
  const result = transform(input, {components: {Alert: 'AlertComponent'}, passNode: true}).data
  assert.deepEqual(result.type, {name: 'AlertComponent'})
  assert.deepEqual(result.props.node, input)
})

test('mapped components work without passNode', () => {
  const result = transform(element('Alert', {kind: 'info'}), {components: {Alert: 'AlertComponent'}}).data
  assert.deepEqual(result.type, {name: 'AlertComponent'})
  assert.equal(Object.hasOwn(result.props, 'node'), false)
})

test('MDX JSX literal attributes are preserved', () => {
  const tree = {type: 'mdxJsxFlowElement', name: 'Widget', attributes: [{type: 'mdxJsxAttribute', name: 'answer', value: '42'}, {type: 'mdxJsxAttribute', name: 'enabled', value: null}], children: [text('body')]}
  const result = transform(tree, {}, {bindings: {Widget: 'Widget'}}).data
  assert.equal(result.type, 'Widget')
  assert.deepEqual(result.props, {answer: '42', enabled: true, children: 'body'})
})

test('MDX expressions are delegated to the evaluator', () => {
  const tree = {type: 'root', children: [{type: 'mdxTextExpression', value: 'name', data: {estree: {type: 'Program', body: [{type: 'ExpressionStatement', expression: {type: 'Identifier', name: 'name'}}]}}}]}
  assert.deepEqual(transform(tree, {}, {bindings: {name: 'Ada'}}).data, {type: 'Fragment', props: {children: 'Ada'}})
})

test('MDX ESM programs are delegated to evaluateProgram', () => {
  const tree = {type: 'root', children: [{type: 'mdxjsEsm', value: 'export const value = 3', data: {estree: {type: 'Program', body: [{type: 'ExpressionStatement', expression: {type: 'Literal', value: 'module-result'}}]}}}]}
  assert.deepEqual(transform(tree, {}, {bindings: {}}).data, {type: 'Fragment', props: {children: 'module-result'}})
})

test('dynamic member components are evaluated', () => {
  const tree = {type: 'mdxJsxFlowElement', name: 'UI.Button', attributes: [], children: [text('click')]}
  const result = transform(tree, {}, {bindings: {UI: {Button: 'PrimaryButton'}}}).data
  assert.equal(result.type, 'PrimaryButton')
})

test('table-cell align can become CSS-cased style', () => {
  const result = transform(element('td', {align: 'center'}), {stylePropertyNameCase: 'css'}).data
  assert.deepEqual(result.props.style, {'text-align': 'center'})
  assert.equal(Object.hasOwn(result.props, 'align'), false)
})

test('HTML casing and disabled table alignment are selectable', () => {
  const result = transform(element('td', {align: 'right', className: ['cell']}), {elementAttributeNameCase: 'html', tableCellAlignToStyle: false}).data
  assert.equal(result.props.class, 'cell')
  assert.equal(result.props.align, 'right')
})

test('development source positions are one-based lines and zero-based columns', () => {
  const tree = {...element('h2', {}, [text('x')]), position: {start: {line: 4, column: 7}}}
  const result = transform(tree, {filePath: 'input.md'}, {mode: 'development'}).data
  assert.deepEqual(result.dev.source, {columnNumber: 6, fileName: 'input.md', lineNumber: 4})
})
