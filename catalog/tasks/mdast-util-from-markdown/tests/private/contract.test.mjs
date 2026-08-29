import assert from 'node:assert/strict'
import {test} from 'node:test'
import {call, inventory, parse, parsePositions} from './test_client.mjs'

test('package root is callable', () => {
  assert.deepEqual(inventory(), {
    packageName: 'mdast-util-from-markdown',
    packageVersion: '2.0.3',
    packageShape: true,
    runtimeEntry: true,
    declarationEntry: true,
    exportNames: ['fromMarkdown']
  })
})

test('parses an empty document', () => {
  assert.deepEqual(parse(''), {type: 'root', children: []})
})

test('parses a paragraph and soft line break', () => {
  assert.deepEqual(parse('a\nb'), {
    type: 'root', children: [{type: 'paragraph', children: [{type: 'text', value: 'a\nb'}]}]
  })
})

test('parses headings, emphasis, and strong emphasis', () => {
  assert.deepEqual(parse('## Hello, *world* and **all**!'), {
    type: 'root', children: [{type: 'heading', depth: 2, children: [
      {type: 'text', value: 'Hello, '},
      {type: 'emphasis', children: [{type: 'text', value: 'world'}]},
      {type: 'text', value: ' and '},
      {type: 'strong', children: [{type: 'text', value: 'all'}]},
      {type: 'text', value: '!'}
    ]}]
  })
})

test('parses inline code and hard breaks', () => {
  assert.deepEqual(parse('`code`  \nnext'), {
    type: 'root', children: [{type: 'paragraph', children: [
      {type: 'inlineCode', value: 'code'}, {type: 'break'}, {type: 'text', value: 'next'}
    ]}]
  })
})

test('parses block quotes', () => {
  assert.deepEqual(parse('> quoted\n> text'), {
    type: 'root', children: [{type: 'blockquote', children: [
      {type: 'paragraph', children: [{type: 'text', value: 'quoted\ntext'}]}
    ]}]
  })
})

test('parses unordered lists', () => {
  assert.deepEqual(parse('- one\n- two'), {
    type: 'root', children: [{type: 'list', ordered: false, start: null, spread: false, children: [
      {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'one'}]}]},
      {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'two'}]}]}
    ]}]
  })
})

test('parses ordered lists and start values', () => {
  assert.deepEqual(parse('3. three\n4. four'), {
    type: 'root', children: [{type: 'list', ordered: true, start: 3, spread: false, children: [
      {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'three'}]}]},
      {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'four'}]}]}
    ]}]
  })
})

test('parses fenced code with language and meta', () => {
  assert.deepEqual(parse('```js title=demo\nconst x = 1\n```'), {
    type: 'root', children: [{type: 'code', lang: 'js', meta: 'title=demo', value: 'const x = 1'}]
  })
})

test('parses indented code and thematic breaks', () => {
  assert.deepEqual(parse('    one\n    two\n\n---'), {
    type: 'root', children: [
      {type: 'code', lang: null, meta: null, value: 'one\ntwo'},
      {type: 'thematicBreak'}
    ]
  })
})

test('parses links and images', () => {
  assert.deepEqual(parse('[link](https://example.test "title")\n\n![alt](image.png "caption")'), {
    type: 'root', children: [
      {type: 'paragraph', children: [{type: 'link', title: 'title', url: 'https://example.test', children: [{type: 'text', value: 'link'}]}]},
      {type: 'paragraph', children: [{type: 'image', title: 'caption', url: 'image.png', alt: 'alt'}]}
    ]
  })
})

test('parses reference links and definitions', () => {
  assert.deepEqual(parse('[read][docs]\n\n[docs]: /guide "Guide"'), {
    type: 'root', children: [
      {type: 'paragraph', children: [{type: 'linkReference', children: [{type: 'text', value: 'read'}], label: 'docs', identifier: 'docs', referenceType: 'full'}]},
      {type: 'definition', identifier: 'docs', label: 'docs', title: 'Guide', url: '/guide'}
    ]
  })
})

test('parses protocol and email autolinks', () => {
  assert.deepEqual(parse('<https://example.test> <person@example.test>'), {
    type: 'root', children: [{type: 'paragraph', children: [
      {type: 'link', title: null, url: 'https://example.test', children: [{type: 'text', value: 'https://example.test'}]},
      {type: 'text', value: ' '},
      {type: 'link', title: null, url: 'mailto:person@example.test', children: [{type: 'text', value: 'person@example.test'}]}
    ]}]
  })
})

test('preserves raw HTML nodes', () => {
  assert.deepEqual(parse('<span>hello</span>'), {
    type: 'root', children: [{type: 'paragraph', children: [
      {type: 'html', value: '<span>'}, {type: 'text', value: 'hello'}, {type: 'html', value: '</span>'}
    ]}]
  })
})

test('decodes escapes and named and numeric character references', () => {
  assert.deepEqual(parse('\\*literal\\* &copy; &amp; &#x41;'), {
    type: 'root', children: [{type: 'paragraph', children: [{type: 'text', value: '*literal* © & A'}]}]
  })
})

test('keeps mdast positions deterministic', () => {
  assert.deepEqual(parsePositions('a\n\nb'), {
    type: 'root', children: [
      {type: 'paragraph', children: [{type: 'text', value: 'a', position: {start: {line: 1, column: 1, offset: 0}, end: {line: 1, column: 2, offset: 1}}}], position: {start: {line: 1, column: 1, offset: 0}, end: {line: 1, column: 2, offset: 1}}},
      {type: 'paragraph', children: [{type: 'text', value: 'b', position: {start: {line: 3, column: 1, offset: 3}, end: {line: 3, column: 2, offset: 4}}}], position: {start: {line: 3, column: 1, offset: 3}, end: {line: 3, column: 2, offset: 4}}}
    ], position: {start: {line: 1, column: 1, offset: 0}, end: {line: 3, column: 2, offset: 4}}
  })
})

test('parses Unicode without data loss', () => {
  assert.deepEqual(parse('# café 世界\n\nnaïve'), {
    type: 'root', children: [
      {type: 'heading', depth: 1, children: [{type: 'text', value: 'café 世界'}]},
      {type: 'paragraph', children: [{type: 'text', value: 'naïve'}]}
    ]
  })
})

test('preserves CRLF line endings in text values', () => {
  assert.deepEqual(parse('first\r\nsecond'), {
    type: 'root', children: [{type: 'paragraph', children: [{type: 'text', value: 'first\r\nsecond'}]}]
  })
})

test('keeps nested list structure and loose item separation', () => {
  assert.deepEqual(parse('- outer\n  - inner\n\n- next'), {
    type: 'root', children: [{type: 'list', ordered: false, start: null, spread: true, children: [
      {type: 'listItem', spread: false, checked: null, children: [
        {type: 'paragraph', children: [{type: 'text', value: 'outer'}]},
        {type: 'list', ordered: false, start: null, spread: false, children: [
          {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'inner'}]}]}
        ]}
      ]},
      {type: 'listItem', spread: false, checked: null, children: [{type: 'paragraph', children: [{type: 'text', value: 'next'}]}]}
    ]}]
  })
})

test('is deterministic across repeated calls', () => {
  const input = '# title\n\n- a\n- b\n\n[ref](url)'
  assert.deepEqual(parse(input), parse(input))
  assert.deepEqual(call('parse', input).value, call('parse', input).value)
})

test('does not expose unexpected callable root exports', () => {
  const response = call('inventory')
  assert.equal(response.ok, true)
  assert.deepEqual(response.value.exportNames, ['fromMarkdown'])
})
