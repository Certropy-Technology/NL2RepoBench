import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

function value(request) { const result=call(request); assert.equal(result.ok,true,result.message); return result.value; }
function failure(request) { const result=call(request); assert.equal(result.ok,false); return result; }

test('exports the core package shape', () => {
  const result=value({operation:'shape'});
  for (const name of ['parse','generate','tokenize','walk','find','findLast','findAll','toPlainObject','fromPlainObject','clone']) assert.equal(result.types[name],'function');
  for (const name of ['lexer','definitionSyntax','ident','string','url']) assert.equal(result.types[name],'object');
  assert.equal(result.version,'3.2.1');
});
test('exports token tables and namespaces', () => {
  const result=value({operation:'shape'});
  assert.equal(result.types.tokenNames,'object'); assert.equal(result.types.tokenTypes,'object');
  for (const name of ['List','Lexer','TokenStream','OffsetToLocation']) assert.equal(result.types[name],'function');
});

test('parses and generates a stylesheet', () => {
  const result=value({operation:'parse-generate',payload:{source:'a{color:red;margin:0 1px}',roundTrip:true}});
  assert.equal(result.ast.type,'StyleSheet'); assert.equal(result.generated,'a{color:red;margin:0 1px}'); assert.equal(result.roundTrip,result.generated);
});
test('parses nested at-rules deterministically', () => {
  const result=value({operation:'parse-generate',payload:{source:'@media screen and (min-width: 10px){.x{display:block}}'}});
  assert.equal(result.ast.children[0].type,'Atrule'); assert.equal(result.generated,'@media screen and (min-width:10px){.x{display:block}}');
});
test('parses CSS values', () => {
  const result=value({operation:'parse-generate',payload:{source:'1px solid rgb(1, 2, 3)',options:{context:'value'},roundTrip:true}});
  assert.deepEqual(result.ast.children.map(node=>node.type),['Dimension','Identifier','Function']); assert.equal(result.generated,'1px solid rgb(1,2,3)'); assert.equal(result.roundTrip,result.generated);
});
test('parses selectors', () => {
  const result=value({operation:'parse-generate',payload:{source:'div.foo > a:hover',options:{context:'selector'}}});
  assert.equal(result.ast.type,'Selector'); assert.deepEqual(result.ast.children.map(node=>node.type),['TypeSelector','ClassSelector','Combinator','TypeSelector','PseudoClassSelector']); assert.equal(result.generated,'div.foo>a:hover');
});
test('parses declarations with important', () => {
  const result=value({operation:'parse-generate',payload:{source:'color: red !important',options:{context:'declaration'}}});
  assert.equal(result.ast.type,'Declaration'); assert.equal(result.ast.property,'color'); assert.equal(result.ast.important,true); assert.equal(result.generated,'color:red!important');
});
test('preserves comments and quoted strings', () => {
  const result=value({operation:'parse-generate',payload:{source:'a{content:"x\\\"y";/*c*/color:var(--x)}'}});
  assert.equal(result.generated,'a{content:"x\\\"y";color:var(--x)}');
});
test('rejects invalid CSS context input', () => {
  const result=failure({operation:'parse-generate',payload:{source:'1px solid red',options:{context:'selector'}}}); assert.match(result.message,/expected|Unexpected|Selector/i);
});
test('rejects malformed stylesheet', () => {
  const result=failure({operation:'parse-generate',payload:{source:'color:;',options:{context:'declaration'}}}); assert.match(result.message,/Unexpected|expected|value/i);
});

test('tokenizes identifiers and punctuation', () => {
  const tokens=value({operation:'tokens',payload:{source:'a{color:red;}'}}); assert.deepEqual(tokens.map(t=>t.name),['ident-token','{-token','ident-token','colon-token','ident-token','semicolon-token','}-token']); assert.equal(tokens[0].raw,'a');
});
test('tokenizes numbers, dimensions, and percentages', () => {
  const tokens=value({operation:'tokens',payload:{source:'-1.5em 10%'}}); assert.deepEqual(tokens.map(t=>t.name),['dimension-token','whitespace-token','percentage-token']); assert.deepEqual(tokens.map(t=>t.raw),['-1.5em',' ','10%']);
});
test('tokenizes strings and URLs', () => {
  const tokens=value({operation:'tokens',payload:{source:'"x" url(foo.png)'}}); assert.deepEqual(tokens.map(t=>t.name),['string-token','whitespace-token','url-token']); assert.equal(tokens[2].raw,'url(foo.png)');
});
test('tokenizes comments as one token', () => {
  const tokens=value({operation:'tokens',payload:{source:'/* hi */#id'}}); assert.deepEqual(tokens.map(t=>t.name),['comment-token','hash-token']); assert.equal(tokens[0].raw,'/* hi */');
});

test('walks nodes in document order', () => {
  const nodes=value({operation:'walk',payload:{source:'a{color:red;margin:0}'}}); assert.equal(nodes[0].type,'StyleSheet'); assert.deepEqual(nodes.filter(n=>n.type==='Declaration').map(n=>n.property),['color','margin']);
});
test('restricts walk with visit', () => {
  const nodes=value({operation:'walk',payload:{source:'a{color:red;margin:0}',visit:'Declaration'}}); assert.ok(nodes.length>0); assert.ok(nodes.every(n=>n.type==='Declaration'));
});
test('supports reverse traversal', () => {
  const nodes=value({operation:'walk',payload:{source:'a{color:red;margin:0}',visit:'Declaration',reverse:true}}); assert.deepEqual(nodes.map(n=>n.property),['margin','color']);
});
test('finds the first and last node', () => {
  const result=value({operation:'find',payload:{source:'a{color:red;margin:0}',nodeType:'Declaration'}}); assert.equal(result.first.property,'color'); assert.equal(result.last.property,'margin');
});
test('findAll returns every matching node', () => {
  const result=value({operation:'find',payload:{source:'a{color:red;margin:0}',nodeType:'Identifier'}}); assert.deepEqual(result.all.map(n=>n.name),['red']);
});
test('plain ASTs remain stable through conversion', () => {
  const result=value({operation:'parse-generate',payload:{source:'.x{padding:2px}',roundTrip:true}}); assert.deepEqual(result.ast,result.ast); assert.equal(result.roundTrip,'.x{padding:2px}');
});

test('parses a definition-syntax keyword alternative', () => {
  const result=value({operation:'definition',payload:{source:'<length> | auto'}}); assert.equal(result.ast.type,'Group'); assert.equal(result.generated,'<length> | auto');
});
test('parses a definition-syntax multiplier', () => {
  const result=value({operation:'definition',payload:{source:'[ <length> | auto ]#'}}); assert.equal(result.ast.terms[0].type,'Multiplier'); assert.equal(result.generated,'[ <length> | auto ]#');
});
test('walks definition-syntax nodes', () => {
  const result=value({operation:'definition',payload:{source:'<color> && <length>',walk:true}}); assert.ok(result.nodes.some(node=>node.type==='Type'&&node.name==='color')); assert.ok(result.nodes.some(node=>node.type==='Type'&&node.name==='length'));
});
test('rejects malformed definition syntax', () => {
  const result=failure({operation:'definition',payload:{source:'<length'}}); assert.match(result.message,/Expect|syntax/i);
});

test('lexer matches a valid color property', () => {
  const result=value({operation:'lexer',payload:{property:'color',value:'red'}}); assert.equal(result.error,null); assert.ok(result.matched); assert.ok(result.iterations>0);
});
test('lexer matches a valid dimension property', () => {
  const result=value({operation:'lexer',payload:{property:'margin',value:'1px 2px'}}); assert.equal(result.error,null); assert.ok(result.matched);
});
test('lexer reports invalid property values', () => {
  const result=value({operation:'lexer',payload:{property:'color',value:'not-a-color'}}); assert.equal(result.matched,null); assert.ok(result.error); assert.ok(result.iterations>0);
});

test('encodes and decodes CSS strings', () => {
  assert.equal(value({operation:'utils',payload:{namespace:'string',method:'encode',value:'a "b"'}}),'"a \\"b\\""'); assert.equal(value({operation:'utils',payload:{namespace:'string',method:'decode',value:'a\\20 b'}}),'a b');
});
test('encodes CSS identifiers', () => {
  assert.equal(value({operation:'utils',payload:{namespace:'ident',method:'encode',value:'a b'}}),'a\\ b'); assert.equal(value({operation:'utils',payload:{namespace:'ident',method:'decode',value:'a\\ b'}}),'a b');
});
test('encodes CSS URLs', () => {
  assert.equal(value({operation:'utils',payload:{namespace:'url',method:'encode',value:'a b#c'}}),'url(a\\ b#c)'); assert.equal(value({operation:'utils',payload:{namespace:'url',method:'decode',value:'url(a\\ b#c)'}}),'a b#c');
});
test('escapes leading identifier digits', () => {
  const encoded=value({operation:'utils',payload:{namespace:'ident',method:'encode',value:'1abc'}}); assert.match(encoded,/^\\31 /); assert.equal(value({operation:'utils',payload:{namespace:'ident',method:'decode',value:encoded}}),'1abc');
});
test('utility encoding is deterministic', () => {
  const request={operation:'utils',payload:{namespace:'string',method:'encode',value:'line\nnext',apostrophe:true}}; assert.equal(value(request),value(request));
});
