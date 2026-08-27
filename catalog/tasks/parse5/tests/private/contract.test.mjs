import test from 'node:test';
import assert from 'node:assert/strict';
import {constants, inspect, parseDocument, parseFragment, serializeOuter} from './test_client.mjs';

const HTML = 'http://www.w3.org/1999/xhtml';
const SVG = 'http://www.w3.org/2000/svg';
const MATHML = 'http://www.w3.org/1998/Math/MathML';

function children(node) {
	return node?.childNodes ?? [];
}

function elements(node) {
	return children(node).filter(child => typeof child?.tagName === 'string');
}

function find(node, predicate) {
	if (!node) return undefined;
	if (predicate(node)) return node;
	for (const child of children(node)) {
		const match = find(child, predicate);
		if (match) return match;
	}
	if (node.content) return find(node.content, predicate);
	return undefined;
}

function text(node) {
	if (!node) return '';
	if (node.nodeName === '#text') return node.value;
	return children(node).map(text).join('') + (node.content ? text(node.content) : '');
}

test('package metadata exposes parse5 8.0.1 as ESM with declarations and no CLI', () => {
	const value = inspect();
	assert.equal(value.name, 'parse5');
	assert.equal(value.version, '8.0.1');
	assert.equal(value.type, 'module');
	assert.equal(value.declarationExists, true);
	assert.equal(value.hasBin, false);
});

test('root exports all required package functions', () => {
	const kinds = inspect().exportKinds;
	for (const name of ['parse', 'parseFragment', 'serialize', 'serializeOuter']) assert.equal(kinds[name], 'function');
});

test('root exposes compatibility classes and object namespaces', () => {
	const kinds = inspect().exportKinds;
	assert.equal(kinds.Parser, 'function');
	assert.equal(kinds.Tokenizer, 'function');
	for (const name of ['ErrorCodes', 'Token', 'TokenizerMode', 'defaultTreeAdapter', 'foreignContent', 'html']) {
		assert.equal(kinds[name], 'object');
	}
});

test('default tree adapter exposes construction traversal and location methods', () => {
	const methods = constants().adapterMethods;
	for (const name of ['appendChild', 'createDocument', 'createDocumentFragment', 'createElement', 'detachNode', 'getAttrList', 'getChildNodes', 'getDocumentMode', 'getFirstChild', 'getNamespaceURI', 'getNodeSourceCodeLocation', 'getParentNode', 'getTagName', 'insertBefore', 'isElementNode', 'setDocumentMode', 'setNodeSourceCodeLocation', 'setTemplateContent', 'updateNodeSourceCodeLocation']) {
		assert.ok(methods.includes(name), name);
	}
});

test('public namespace and selected parse error constants are stable', () => {
	const value = constants();
	assert.deepEqual({HTML: value.ns.HTML, SVG: value.ns.SVG, MATHML: value.ns.MATHML, XLINK: value.ns.XLINK, XML: value.ns.XML, XMLNS: value.ns.XMLNS}, {
		HTML,
		SVG,
		MATHML,
		XLINK: 'http://www.w3.org/1999/xlink',
		XML: 'http://www.w3.org/XML/1998/namespace',
		XMLNS: 'http://www.w3.org/2000/xmlns/',
	});
	assert.deepEqual(value.errorCodes, {missingDoctype: 'missing-doctype', duplicateAttribute: 'duplicate-attribute', unexpectedNullCharacter: 'unexpected-null-character'});
});

test('Parser static compatibility entry points remain callable', () => {
	assert.deepEqual(constants().parserStaticKinds, {parse: 'function', getFragmentParser: 'function'});
});

test('empty input creates an implied html head and body document', () => {
	const {tree} = parseDocument('');
	assert.equal(tree.nodeName, '#document');
	assert.equal(tree.mode, 'quirks');
	const html = find(tree, node => node.tagName === 'html');
	assert.deepEqual(elements(html).map(node => node.tagName), ['head', 'body']);
});

test('standards doctype selects no-quirks mode and is preserved', () => {
	const value = parseDocument('<!DOCTYPE html><p>x');
	assert.equal(value.tree.mode, 'no-quirks');
	assert.equal(children(value.tree)[0].nodeName, '#documentType');
	assert.equal(children(value.tree)[0].name, 'html');
	assert.match(value.html, /^<!DOCTYPE html>/);
});

test('title RCDATA decodes entities and body text is retained', () => {
	const {tree} = parseDocument('<title>A &amp; B</title><p>Hello');
	assert.equal(text(find(tree, node => node.tagName === 'title')), 'A & B');
	assert.equal(text(find(tree, node => node.tagName === 'p')), 'Hello');
});

test('comments are represented in source order', () => {
	const {tree} = parseDocument('<!--before--><p>x</p><!--after-->');
	const comments = [];
	(function collect(node) { if (node.nodeName === '#comment') comments.push(node.data); for (const child of children(node)) collect(child); })(tree);
	assert.deepEqual(comments, ['before', 'after']);
});

test('HTML names are lowercased and duplicate attributes keep the first value', () => {
	const {tree} = parseDocument('<DIV ID="first" id="second" DATA-X="Y"></DIV>');
	const div = find(tree, node => node.tagName === 'div');
	assert.deepEqual(div.attrs.map(attr => [attr.name, attr.value]), [['id', 'first'], ['data-x', 'Y']]);
});

test('opening a second paragraph implicitly closes the first', () => {
	const {tree} = parseDocument('<p>one<p>two');
	const body = find(tree, node => node.tagName === 'body');
	assert.deepEqual(elements(body).map(node => [node.tagName, text(node)]), [['p', 'one'], ['p', 'two']]);
});

test('table rows receive an implicit tbody', () => {
	const {tree} = parseDocument('<table><tr><td>x</table>');
	const table = find(tree, node => node.tagName === 'table');
	assert.equal(elements(table)[0].tagName, 'tbody');
	assert.equal(find(table, node => node.tagName === 'td').childNodes[0].value, 'x');
});

test('non-whitespace table text is foster-parented before the table', () => {
	const {tree} = parseDocument('<body><table>outside<tr><td>inside</td></tr></table></body>');
	const body = find(tree, node => node.tagName === 'body');
	assert.equal(children(body)[0].value, 'outside');
	assert.equal(children(body)[1].tagName, 'table');
});

test('misnested formatting elements are reconstructed', () => {
	const {tree} = parseDocument('<p><b><i>x</b>y</i>z');
	const p = find(tree, node => node.tagName === 'p');
	assert.equal(text(p), 'xyz');
	assert.equal(find(p, node => node.tagName === 'b').childNodes[0].tagName, 'i');
	assert.ok(elements(p).filter(node => node.tagName === 'i').length >= 1);
});

test('script content is parsed as raw text', () => {
	const {tree} = parseDocument('<script>if (a < b && c > d) x&copy;</script>');
	assert.equal(text(find(tree, node => node.tagName === 'script')), 'if (a < b && c > d) x&copy;');
});

test('style content is parsed as raw text', () => {
	const {tree} = parseDocument('<style>a>b{content:"&amp;"}</style>');
	assert.equal(text(find(tree, node => node.tagName === 'style')), 'a>b{content:"&amp;"}');
});

test('textarea uses RCDATA and ignores its initial newline', () => {
	const {tree} = parseDocument('<textarea>\n&lt;b&gt;&amp;<b>x</b></textarea>');
	assert.equal(text(find(tree, node => node.tagName === 'textarea')), '<b>&<b>x</b>');
});

test('scripting-enabled head noscript content remains text', () => {
	const {tree} = parseDocument('<head><noscript><link href=x></noscript></head>', {scriptingEnabled: true});
	const noscript = find(tree, node => node.tagName === 'noscript');
	assert.equal(text(noscript), '<link href=x>');
});

test('scripting-disabled head noscript content is parsed as markup', () => {
	const {tree} = parseDocument('<head><noscript><link href=x></noscript></head>', {scriptingEnabled: false});
	const noscript = find(tree, node => node.tagName === 'noscript');
	assert.equal(find(noscript, node => node.tagName === 'link').attrs[0].value, 'x');
});

test('SVG elements use the SVG namespace and adjusted tag case', () => {
	const {tree} = parseDocument('<svg><lineargradient id=x></lineargradient><foreignObject><p>x</p></foreignObject></svg>');
	const svg = find(tree, node => node.tagName === 'svg');
	assert.equal(svg.namespaceURI, SVG);
	assert.equal(find(svg, node => node.tagName === 'linearGradient').namespaceURI, SVG);
	assert.equal(find(svg, node => node.tagName === 'p').namespaceURI, HTML);
});

test('MathML elements use the MathML namespace', () => {
	const {tree} = parseDocument('<math><mi>x</mi><annotation-xml encoding="text/html"><p>y</p></annotation-xml></math>');
	assert.equal(find(tree, node => node.tagName === 'math').namespaceURI, MATHML);
	assert.equal(find(tree, node => node.tagName === 'mi').namespaceURI, MATHML);
	assert.equal(find(tree, node => node.tagName === 'p').namespaceURI, HTML);
});

test('foreign namespaced attributes retain namespace and prefix', () => {
	const {tree} = parseDocument('<svg><a xlink:href="#x" xml:lang="en"></a></svg>');
	const attrs = Object.fromEntries(find(tree, node => node.tagName === 'a').attrs.map(attr => [attr.name, attr]));
	assert.equal(attrs.href.prefix, 'xlink');
	assert.equal(attrs.href.namespace, 'http://www.w3.org/1999/xlink');
	assert.equal(attrs.lang.prefix, 'xml');
	assert.equal(attrs.lang.namespace, 'http://www.w3.org/XML/1998/namespace');
});

test('template children are stored in a separate content fragment', () => {
	const {tree} = parseDocument('<template><div>x</div></template>');
	const template = find(tree, node => node.tagName === 'template');
	assert.deepEqual(template.childNodes, []);
	assert.equal(template.content.nodeName, '#document-fragment');
	assert.equal(find(template.content, node => node.tagName === 'div').childNodes[0].value, 'x');
});

test('Unicode including astral emoji is preserved', () => {
	const input = 'café Ελληνικά 中文 😀 𐐷';
	const {tree} = parseDocument(`<p>${input}</p>`);
	assert.equal(text(find(tree, node => node.tagName === 'p')), input);
});

test('null input characters in ordinary text are omitted', () => {
	const {tree} = parseDocument('<p>a\u0000b</p>');
	assert.equal(text(find(tree, node => node.tagName === 'p')), 'ab');
});

test('source locations expose one-based positions and zero-based offsets', () => {
	const {tree} = parseDocument('<p id="x">hi</p>', {locations: true});
	const p = find(tree, node => node.tagName === 'p');
	assert.deepEqual({startLine: p.sourceCodeLocation.startLine, startCol: p.sourceCodeLocation.startCol, startOffset: p.sourceCodeLocation.startOffset, endOffset: p.sourceCodeLocation.endOffset}, {startLine: 1, startCol: 1, startOffset: 0, endOffset: 16});
	assert.equal(p.sourceCodeLocation.attrs.id.startOffset, 3);
	assert.equal(p.sourceCodeLocation.startTag.endOffset, 10);
	assert.equal(p.sourceCodeLocation.endTag.startOffset, 12);
});

test('implicit document elements have no source locations', () => {
	const {tree} = parseDocument('<p>x', {locations: true});
	for (const tag of ['html', 'head', 'body']) assert.equal(find(tree, node => node.tagName === tag).sourceCodeLocation, null);
	assert.equal(find(tree, node => node.tagName === 'p').sourceCodeLocation.startOffset, 0);
});

test('parse error callback reports ordered stable codes and positions', () => {
	const {errors} = parseDocument('<div a=1 a=2>\u0000</span>', {errors: true});
	assert.ok(errors.length >= 3);
	assert.equal(errors[0].code, 'duplicate-attribute');
	assert.ok(errors.some(error => error.code === 'missing-doctype'));
	assert.ok(errors.some(error => error.code === 'duplicate-attribute'));
	assert.ok(errors.some(error => error.code === 'unexpected-null-character'));
	for (const error of errors) {
		assert.equal(Number.isInteger(error.startOffset), true);
		assert.equal(Number.isInteger(error.startLine), true);
	}
});

test('simple fragment parsing returns only fragment children', () => {
	const {tree, html} = parseFragment('<div>A</div><span>B</span>');
	assert.equal(tree.nodeName, '#document-fragment');
	assert.deepEqual(elements(tree).map(node => node.tagName), ['div', 'span']);
	assert.equal(html, '<div>A</div><span>B</span>');
});

test('table context fragment inserts tbody around rows', () => {
	const {tree} = parseFragment('<tr><td>x</td></tr>', {contextTag: 'table'});
	assert.equal(elements(tree)[0].tagName, 'tbody');
	assert.equal(find(tree, node => node.tagName === 'td').childNodes[0].value, 'x');
});

test('select context fragment discards invalid elements but keeps option text', () => {
	const {tree} = parseFragment('<div>bad</div><option value=x>good</option>', {contextTag: 'select'});
	assert.equal(find(tree, node => node.tagName === 'div'), undefined);
	assert.equal(find(tree, node => node.tagName === 'option').childNodes[0].value, 'good');
});

test('textarea context fragment treats markup as RCDATA text', () => {
	const {tree} = parseFragment('&lt;b&gt;<b>x</b>', {contextTag: 'textarea'});
	assert.equal(text(tree), '<b><b>x</b>');
});

test('script context fragment treats markup and entities as raw text', () => {
	const {tree} = parseFragment('<b>&amp;</b>', {contextTag: 'script'});
	assert.equal(text(tree), '<b>&amp;</b>');
});

test('default fragment context parses table as an ordinary element', () => {
	const {tree} = parseFragment('<table><tr><td>x');
	assert.equal(elements(tree)[0].tagName, 'table');
	assert.equal(find(tree, node => node.tagName === 'tbody').tagName, 'tbody');
});

test('fragment parsing preserves comments and adjacent text nodes deterministically', () => {
	const {tree} = parseFragment('a<!--c-->b');
	assert.deepEqual(children(tree).map(node => [node.nodeName, node.value ?? node.data]), [['#text', 'a'], ['#comment', 'c'], ['#text', 'b']]);
});

test('SVG context fragment keeps foreign namespace and adjusted names', () => {
	const {tree} = parseFragment('<lineargradient></lineargradient>', {contextTag: 'svg', contextNamespace: SVG});
	const gradient = elements(tree)[0];
	assert.equal(gradient.tagName, 'linearGradient');
	assert.equal(gradient.namespaceURI, SVG);
});

test('fragment source locations are relative to fragment input', () => {
	const {tree} = parseFragment('<b>x</b>', {locations: true});
	const b = find(tree, node => node.tagName === 'b');
	assert.equal(b.sourceCodeLocation.startOffset, 0);
	assert.equal(b.sourceCodeLocation.endOffset, 8);
});

test('document serialization emits a canonical complete tree', () => {
	const {html} = parseDocument('<!doctype html><title>x</title><p>y');
	assert.equal(html, '<!DOCTYPE html><html><head><title>x</title></head><body><p>y</p></body></html>');
});

test('text serialization escapes ampersand and non-breaking space', () => {
	assert.equal(parseFragment('<p>&amp;&nbsp;&lt;</p>').html, '<p>&amp;&nbsp;&lt;</p>');
});

test('attribute serialization escapes ampersand quotes and non-breaking space', () => {
	const {html} = parseFragment('<div title="a&amp;&quot;&nbsp;b"></div>');
	assert.equal(html, '<div title="a&amp;&quot;&nbsp;b"></div>');
});

test('HTML void elements serialize without closing tags', () => {
	assert.equal(parseFragment('<br><img src=x><input disabled>').html, '<br><img src="x"><input disabled="">');
});

test('document type serialization uses canonical uppercase syntax', () => {
	assert.match(parseDocument('<!doctype html public "x"><p>y').html, /^<!DOCTYPE html>/);
});

test('comment serialization preserves comment data', () => {
	assert.equal(parseFragment('<!--alpha--><p>x</p>').html, '<!--alpha--><p>x</p>');
});

test('template serialization uses template content children', () => {
	assert.equal(parseFragment('<template><span>x</span></template>').html, '<template><span>x</span></template>');
});

test('serializeOuter includes an element and its descendants', () => {
	assert.equal(serializeOuter('<div class=x>Hello <b>world</b></div>'), '<div class="x">Hello <b>world</b></div>');
});

test('serializeOuter escapes a top-level text node', () => {
	assert.equal(serializeOuter('a &amp; b'), 'a &amp; b');
});

test('serializeOuter keeps HTML void elements void', () => {
	assert.equal(serializeOuter('<img src=x>'), '<img src="x">');
});

test('serialize on an element returns only its child markup', () => {
	const {html} = parseFragment('<div><span>x</span>tail</div>');
	assert.equal(html, '<div><span>x</span>tail</div>');
	assert.equal(serializeOuter('<div><span>x</span>tail</div>'), '<div><span>x</span>tail</div>');
});

test('character references round-trip through decoded tree content', () => {
	const {tree, html} = parseFragment('<p>&copy; &#x1F600; &notin;</p>');
	assert.equal(text(find(tree, node => node.tagName === 'p')), '© 😀 ∉');
	assert.equal(html, '<p>© 😀 ∉</p>');
});

test('unknown named references remain literal text', () => {
	const {tree} = parseFragment('<p>&definitelyUnknown;</p>');
	assert.equal(text(find(tree, node => node.tagName === 'p')), '&definitelyUnknown;');
});

test('raw-text serialization preserves unescaped script content', () => {
	assert.equal(parseFragment('<script>if (a < b && c > d) x&copy;</script>').html, '<script>if (a < b && c > d) x&copy;</script>');
});

test('attribute order is preserved by serialization', () => {
	assert.equal(serializeOuter('<div z="1" a="2" m="3"></div>'), '<div z="1" a="2" m="3"></div>');
});

test('source offsets count UTF-16 code units', () => {
	const {tree} = parseFragment('😀<b>x</b>', {locations: true});
	const b = find(tree, node => node.tagName === 'b');
	assert.equal(b.sourceCodeLocation.startOffset, 2);
	assert.equal(b.sourceCodeLocation.endOffset, 10);
});
