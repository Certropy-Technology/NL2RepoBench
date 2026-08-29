import test from 'node:test';
import assert from 'node:assert/strict';
import {inspect, serialize, serializeResult} from './test_client.mjs';

const text = (value) => ({type: 'text', value});
const paragraph = (...children) => ({type: 'paragraph', children});
const root = (...children) => ({type: 'root', children});
const item = (children, spread = false) => ({type: 'listItem', spread, children});
const list = (ordered, children, extra = {}) => ({type: 'list', ordered, children, ...extra});

const exactDependencies = {
  '@types/mdast': '4.0.4',
  '@types/unist': '3.0.3',
  'longest-streak': '3.1.0',
  'mdast-util-phrasing': '4.1.0',
  'mdast-util-to-string': '4.0.0',
  'micromark-util-classify-character': '2.0.1',
  'micromark-util-decode-string': '2.0.1',
  'unist-util-visit': '5.1.0',
  zwitch: '2.0.4',
};

test('package metadata identifies an offline ESM mdast-util-to-markdown 2.1.2 package', () => {
  const value = inspect();
  assert.equal(value.name, 'mdast-util-to-markdown');
  assert.equal(value.version, '2.1.2');
  assert.equal(value.type, 'module');
  assert.equal(value.entry, './index.js');
  assert.equal(value.declarationExists, true);
});

test('package root exports toMarkdown and defaultHandlers only', () => {
  assert.deepEqual(inspect().exportKinds, {defaultHandlers: 'object', toMarkdown: 'function'});
});

test('package has no CLI, workspace, or lifecycle installation hooks', () => {
  const value = inspect();
  assert.equal(value.hasBin, false);
  assert.equal(value.hasWorkspaces, false);
  assert.deepEqual(value.lifecycleScripts, []);
});

test('package declares the exact frozen direct runtime dependency set', () => {
  assert.deepEqual(inspect().dependencies, exactDependencies);
});

const cases = [
  ['empty root serializes to an empty string', root(), {}, ''],
  ['plain paragraph receives a final line ending', root(paragraph(text('alpha'))), {}, 'alpha\n'],
  ['ATX heading uses its depth', root({type: 'heading', depth: 2, children: [text('Title')]}), {}, '## Title\n'],
  ['closeAtx repeats closing number signs', root({type: 'heading', depth: 2, children: [text('Title')]}), {closeAtx: true}, '## Title ##\n'],
  ['setext rank one uses equals markers', root({type: 'heading', depth: 1, children: [text('Title')]}), {setext: true}, 'Title\n=====\n'],
  ['setext rank two uses dash markers', root({type: 'heading', depth: 2, children: [text('Title')]}), {setext: true}, 'Title\n-----\n'],
  ['setext rank three remains ATX', root({type: 'heading', depth: 3, children: [text('Title')]}), {setext: true}, '### Title\n'],
  ['blockquote prefixes content and blank lines', root({type: 'blockquote', children: [paragraph(text('a')), paragraph(text('b'))]}), {}, '> a\n>\n> b\n'],
  ['HTML node values are emitted verbatim', root({type: 'html', value: '<x>\ny'}), {}, '<x>\ny\n'],
  ['thematic break uses three asterisks by default', root({type: 'thematicBreak'}), {}, '***\n'],
  ['thematic break honors marker repetition and spaces', root({type: 'thematicBreak'}), {rule: '-', ruleRepetition: 5, ruleSpaces: true}, '- - - - -\n'],
  ['code uses a fenced block by default', root({type: 'code', value: 'a\nb'}), {}, '```\na\nb\n```\n'],
  ['code includes language and meta after the fence', root({type: 'code', lang: 'js', meta: 'x', value: 'a'}), {}, '```js x\na\n```\n'],
  ['code honors a tilde fence', root({type: 'code', lang: 'js', value: 'a'}), {fence: '~'}, '~~~js\na\n~~~\n'],
  ['code can use indentation when fences are disabled', root({type: 'code', value: 'a\nb'}), {fences: false}, '    a\n    b\n'],
  ['blank-edged code remains fenced when fences are disabled', root({type: 'code', value: '\na\n'}), {fences: false}, '```\n\na\n\n```\n'],
  ['inline code uses one grave accent when possible', root(paragraph({type: 'inlineCode', value: 'a b'})), {}, '`a b`\n'],
  ['inline code grows its fence around an internal grave accent', root(paragraph({type: 'inlineCode', value: 'a`b'})), {}, '``a`b``\n'],
  ['emphasis uses asterisks by default', root(paragraph({type: 'emphasis', children: [text('a')]})), {}, '*a*\n'],
  ['emphasis honors underscore', root(paragraph({type: 'emphasis', children: [text('a')]})), {emphasis: '_'}, '_a_\n'],
  ['strong uses double asterisks by default', root(paragraph({type: 'strong', children: [text('a')]})), {}, '**a**\n'],
  ['strong honors double underscore', root(paragraph({type: 'strong', children: [text('a')]})), {strong: '_'}, '__a__\n'],
  ['break emits a hard break followed by a line ending', root(paragraph(text('a'), {type: 'break'}, text('b'))), {}, 'a\\\nb\n'],
  ['matching absolute links become autolinks', root(paragraph({type: 'link', url: 'https://example.com', children: [text('https://example.com')]})), {}, '<https://example.com>\n'],
  ['resourceLink disables autolink selection', root(paragraph({type: 'link', url: 'https://example.com', children: [text('https://example.com')]})), {resourceLink: true}, '[https://example.com](https://example.com)\n'],
  ['link destinations and titles are encoded safely', root(paragraph({type: 'link', url: 'a b', title: 'x " y', children: [text('z')]})), {}, '[z](<a b> "x \\" y")\n'],
  ['single quote option applies to titles', root(paragraph({type: 'link', url: 'u', title: "a'b", children: [text('x')]})), {quote: "'"}, "[x](u 'a\\'b')\n"],
  ['image serializes alt destination and title', root(paragraph({type: 'image', url: 'a b', title: 't', alt: 'A'})), {}, '![A](<a b> "t")\n'],
  ['image reference preserves identifier', root(paragraph({type: 'imageReference', identifier: 'a', referenceType: 'full', alt: 'x'})), {}, '![x][a]\n'],
  ['shortcut link reference omits the second label', root(paragraph({type: 'linkReference', identifier: 'a', referenceType: 'shortcut', children: [text('a')]})), {}, '[a]\n'],
  ['collapsed link reference emits normalized identifier', root(paragraph({type: 'linkReference', identifier: 'a', referenceType: 'collapsed', children: [text('x')]})), {}, '[x][a]\n'],
  ['full link reference prefers its label', root(paragraph({type: 'linkReference', identifier: 'a', label: 'A', referenceType: 'full', children: [text('x')]})), {}, '[x][A]\n'],
  ['definition includes URL and title', root({type: 'definition', identifier: 'a', url: 'u', title: 't'}), {}, '[a]: u "t"\n'],
  ['definitions are separated by a blank line by default', root({type: 'definition', identifier: 'a', url: 'u'}, {type: 'definition', identifier: 'b', url: 'v'}), {}, '[a]: u\n\n[b]: v\n'],
  ['tightDefinitions removes the blank line', root({type: 'definition', identifier: 'a', url: 'u'}, {type: 'definition', identifier: 'b', url: 'v'}), {tightDefinitions: true}, '[a]: u\n[b]: v\n'],
  ['unordered list uses asterisks and blank lines between items', root(list(false, [item([paragraph(text('a'))]), item([paragraph(text('b'))])])), {}, '* a\n\n* b\n'],
  ['unordered list honors plus marker', root(list(false, [item([paragraph(text('a'))])])), {bullet: '+'}, '+ a\n'],
  ['ordered list starts and increments from start', root(list(true, [item([paragraph(text('a'))]), item([paragraph(text('b'))])], {start: 3})), {}, '3. a\n\n4. b\n'],
  ['ordered list can keep a fixed marker', root(list(true, [item([paragraph(text('a'))]), item([paragraph(text('b'))])], {start: 3})), {incrementListMarker: false}, '3. a\n\n3. b\n'],
  ['nested list content is indented', root(list(false, [item([paragraph(text('a')), list(false, [item([paragraph(text('b'))])])])])), {}, '* a\n  * b\n'],
  ['one-space list indentation handles continuation lines', root(list(false, [item([paragraph(text('a\nb'))])])), {listItemIndent: 'one'}, '* a\n  b\n'],
  ['tab list indentation pads loose blocks to a tab stop', root(list(false, [item([paragraph(text('a')), paragraph(text('b'))])])), {listItemIndent: 'tab'}, '*   a\n\n    b\n'],
  ['mixed list indentation chooses tab layout for a loose item', root(list(false, [item([paragraph(text('a')), paragraph(text('b'))], true)], {spread: true})), {listItemIndent: 'mixed'}, '*   a\n\n    b\n'],
  ['empty list items remain distinct without forming a thematic break', root(list(false, [item([]), item([]), item([])])), {bullet: '*'}, '*\n\n*\n\n*\n'],
  ['adjacent unordered lists use different markers', root(list(false, [item([paragraph(text('a'))])]), list(false, [item([paragraph(text('b'))])])), {}, '* a\n\n- b\n'],
  ['text escapes block-looking constructs at line starts', root(paragraph(text('# a\n1. b\n***\n[x](y)'))), {}, '\\# a\n1\\. b\n\\*\\*\\*\n\\[x]\\(y)\n'],
  ['Unicode and astral characters are preserved', root(paragraph(text('caf\u00e9 \ud83d\ude00 \u4e2d\u6587'))), {}, 'caf\u00e9 \ud83d\ude00 \u4e2d\u6587\n'],
  ['character-reference-looking ampersands are escaped selectively', root(paragraph(text('a &copy; & b'))), {}, 'a \\&copy; & b\n'],
  ['adjacent paragraphs receive one blank line', root(paragraph(text('a')), paragraph(text('b'))), {}, 'a\n\nb\n'],
  ['custom unsafe patterns force escaping', root(paragraph(text('a~b'))), {unsafe: [{character: '~'}]}, 'a\\~b\n'],
  ['position metadata does not affect serialization', root({type: 'paragraph', position: {start: {line: 9, column: 4, offset: 10}, end: {line: 9, column: 5, offset: 11}}, children: [text('x')]}), {}, 'x\n'],
];

for (const [name, tree, options, expected] of cases) {
  test(name, () => {
    assert.equal(serialize(tree, options).output, expected);
  });
}

test('defaultHandlers exposes every core mdast handler', () => {
  assert.deepEqual(Object.keys(inspect().handlerKinds), [
    'blockquote', 'break', 'code', 'definition', 'emphasis', 'hardBreak',
    'heading', 'html', 'image', 'imageReference', 'inlineCode', 'link',
    'linkReference', 'list', 'listItem', 'paragraph', 'root', 'strong', 'text',
    'thematicBreak',
  ]);
});

test('all defaultHandlers entries are functions', () => {
  assert.ok(Object.values(inspect().handlerKinds).every((kind) => kind === 'function'));
});

test('repeated calls in one candidate process are deterministic', () => {
  const value = serialize(root(paragraph(text('repeat'))), {}, 4);
  assert.deepEqual(value.repeat, ['repeat\n', 'repeat\n', 'repeat\n', 'repeat\n']);
});

test('serialization does not mutate the supplied JSON tree', () => {
  assert.equal(serialize(root(paragraph(text('stable')))).mutated, false);
});

test('handlers option can serialize a custom node', () => {
  const tree = root(paragraph(text('a'), {type: 'mention', value: 'bob'}, text('b')));
  assert.equal(serialize(tree, {extensionCase: 'handler'}).output, 'a@bobb\n');
});

test('extensions option can install a custom handler', () => {
  const tree = root(paragraph(text('a'), {type: 'mention', value: 'bob'}, text('b')));
  assert.equal(serialize(tree, {extensionCase: 'extension'}).output, 'a<bob>b\n');
});

test('join callback can tighten adjacent flow nodes', () => {
  const tree = root(paragraph(text('a')), paragraph(text('b')));
  assert.equal(serialize(tree, {extensionCase: 'join'}).output, 'a\nb\n');
});

const errors = [
  ['null input is rejected as a non-node', null, {}, /expected node/],
  ['unknown root node type is rejected', {type: 'unknown'}, {}, /unknown node `unknown`/],
  ['invalid bullet is rejected when serializing a list', root(list(false, [item([paragraph(text('a'))])])), {bullet: 'x'}, /options\.bullet/],
  ['equal primary and alternate bullets are rejected', root(list(false, [item([paragraph(text('a'))])]), list(false, [item([paragraph(text('b'))])])), {bullet: '*', bulletOther: '*'}, /to be different/],
  ['invalid fence is rejected when serializing code', root({type: 'code', value: 'a'}), {fence: '!'}, /options\.fence/],
  ['too-short rule repetition is rejected', root({type: 'thematicBreak'}), {ruleRepetition: 2}, /options\.ruleRepetition/],
  ['invalid list indentation is rejected', root(list(false, [item([paragraph(text('a'))])])), {listItemIndent: 'x'}, /options\.listItemIndent/],
  ['invalid title quote is rejected', root(paragraph({type: 'link', url: 'u', title: 't', children: [text('x')]})), {quote: '`'}, /options\.quote/],
  ['invalid emphasis marker is rejected', root(paragraph({type: 'emphasis', children: [text('x')]})), {emphasis: '!'}, /options\.emphasis/],
  ['invalid strong marker is rejected', root(paragraph({type: 'strong', children: [text('x')]})), {strong: '!'}, /options\.strong/],
];

for (const [name, tree, options, message] of errors) {
  test(name, () => {
    const result = serializeResult(tree, options);
    assert.equal(result.ok, false);
    assert.equal(result.exceptionType, 'Error');
    assert.match(result.message, message);
  });
}
