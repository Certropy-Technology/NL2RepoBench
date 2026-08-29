import assert from 'node:assert/strict';
import {test} from 'node:test';
import {spawnSync} from 'node:child_process';

const client = process.env.NODE_TEST_CLIENT ?? new URL('./test_client.mjs', import.meta.url).pathname;
let id = 0;
function request(operation, payload = {}) {
  const result = spawnSync('/usr/bin/timeout', ['--signal=TERM', '--kill-after=5s', '30s', 'runuser', '-u', 'candidate', '--', '/usr/bin/prlimit', '--cpu=30', '--nproc=64', '--nofile=128', '--', '/usr/local/bin/node', '--no-addons', client], {
    cwd: process.env.NODE_CANDIDATE_SITE,
    input: JSON.stringify({id: `r-${++id}`, operation, payload}),
    encoding: 'utf8', maxBuffer: 512 * 1024, timeout: 35_000,
  });
  if (result.error || !result.stdout) throw new Error('candidate-call-failed');
  const response = JSON.parse(result.stdout);
  if (!response.ok) throw new Error(`${response.name}: ${response.message}`);
  return response.value;
}
function error(operation, payload) {
  const result = spawnSync('/usr/local/bin/node', ['--no-addons', client], {cwd: process.env.NODE_CANDIDATE_SITE, input: JSON.stringify({id: `r-${++id}`, operation, payload}), encoding: 'utf8', maxBuffer: 512 * 1024});
  const response = JSON.parse(result.stdout);
  assert.equal(response.ok, false);
  return response;
}
function magic(input, actions = [], options = {}, cloneActions) {
  return request('magic', {input, options, actions, cloneActions});
}
function bundle(payload) { return request('bundle', payload); }

test('exports expected ESM package shape', () => {
  assert.deepEqual(request('inventory'), {packageName: 'magic-string', packageVersion: '1.2.3', packageShape: true, exportNames: ['Bundle', 'MagicString', 'MagicStringError', 'SourceMap', 'default'], hasDefault: true});
});
test('append and prepend compose outside the body', () => assert.equal(magic('abc', [{method: 'append', args: ['!']}, {method: 'prepend', args: ['^']}]).final.string, '^abc!'));
test('indexed inserts preserve append and prepend order', () => assert.equal(magic('abcd', [{method: 'appendLeft', args: [1, 'L']}, {method: 'prependLeft', args: [1, 'P']}, {method: 'appendRight', args: [1, 'R']}, {method: 'prependRight', args: [1, 'Q']}]).final.string, 'aPLQRbcd'));
test('update uses original half-open indexes', () => assert.equal(magic('hello world', [{method: 'update', args: [0, 5, 'hi']}]).final.string, 'hi world'));
test('overwrite replaces a range', () => assert.equal(magic('hello world', [{method: 'overwrite', args: [0, 5, 'hi']}]).final.string, 'hi world'));
test('remove deletes original characters', () => assert.equal(magic('abcdef', [{method: 'remove', args: [1, 3]}]).final.string, 'adef'));
test('reset restores a removed range', () => assert.equal(magic('abcdef', [{method: 'remove', args: [1, 3]}, {method: 'reset', args: [1, 3]}]).final.string, 'abcdef'));
test('slice observes generated range content', () => assert.equal(magic('abcdef', [{method: 'appendLeft', args: [2, 'X']}, {method: 'slice', args: [1, 4]}]).results.at(-1), 'bXcd'));
test('move relocates original content', () => assert.equal(magic('abcdef', [{method: 'move', args: [1, 3, 6]}]).final.string, 'adefbc'));
test('replace changes the first original match', () => assert.equal(magic('foo foo', [{method: 'replace', args: ['foo', 'bar']}]).final.string, 'bar foo'));
test('replaceAll changes every string match', () => assert.equal(magic('foo foo', [{method: 'replaceAll', args: ['foo', 'bar']}]).final.string, 'bar bar'));
test('indent prefixes each non-empty line', () => assert.equal(magic('a\n  b\n  c', [{method: 'indent', args: ['> ']}]).final.string, '> a\n>   b\n>   c'));
test('indent can exclude an original range', () => assert.equal(magic('a\nb\nc', [{method: 'indent', args: ['> ', {exclude: [[2, 3]]}]}]).final.string, '> a\nb\n> c'));
test('indent infers the common indentation', () => assert.equal(magic('  a\n  b', [{method: 'indent', args: []}]).final.string, '    a\n    b'));
test('trim removes surrounding whitespace', () => assert.equal(magic('  x \n', [{method: 'trim', args: []}]).final.string, 'x'));
test('trimStart removes only leading whitespace', () => assert.equal(magic('  x \n', [{method: 'trimStart', args: []}]).final.string, 'x \n'));
test('trimEnd removes only trailing whitespace', () => assert.equal(magic('  x \n', [{method: 'trimEnd', args: []}]).final.string, '  x'));
test('trimLines removes boundary line breaks', () => assert.equal(magic('\n\n  x \n\n', [{method: 'trimLines', args: []}]).final.string, '  x '));
test('lastChar and lastLine observe generated output', () => { const value = magic('a\nb', [{method: 'append', args: ['\nc']}]).final; assert.equal(value.lastChar, 'c'); assert.equal(value.lastLine, 'c'); });
test('length excludes prepend and append content', () => assert.equal(magic('abc', [{method: 'prepend', args: ['>>']}, {method: 'append', args: ['<<']}, {method: 'appendLeft', args: [1, 'X']}]).final.length, 4));
test('isEmpty ignores whitespace', () => assert.equal(magic(' \n\t', []).final.isEmpty, true));
test('hasChanged distinguishes edits', () => assert.equal(magic('abc', [{method: 'update', args: [0, 1, 'x']}]).final.hasChanged, true));
test('getIndentString falls back to a tab', () => assert.equal(magic('a\nb', []).final.indentString, '\t'));
test('clone changes do not affect original', () => { const value = magic('abc', [], {}, [{method: 'append', args: ['!']}]); assert.equal(value.clone.final.string, 'abc!'); assert.equal(value.originalAfterClone.string, 'abc'); });
test('offset shifts indexed edits', () => assert.equal(magic('012345', [{method: 'appendLeft', args: [0, 'X']}], {offset: 2}).final.string, '01X2345'));
test('negative update indexes resolve from the original', () => assert.equal(magic('abcd', [{method: 'update', args: [-2, -1, 'X']}]).final.string, 'abXd'));
test('update with contentOnly retains interior inserts', () => assert.equal(magic('abcd', [{method: 'appendLeft', args: [1, 'I']}, {method: 'update', args: [0, 2, 'X', {overwrite: false}]}]).final.string, 'XIcd'));
test('overwrite removes interior inserts by default', () => assert.equal(magic('abcd', [{method: 'appendLeft', args: [1, 'I']}, {method: 'overwrite', args: [0, 2, 'X']}]).final.string, 'Xcd'));
test('invalid content raises MagicStringError', () => assert.equal(error('magic', {input: 'abc', actions: [{method: 'append', args: [3]}]}).name, 'MagicStringError'));
test('zero-length update raises MagicStringError', () => assert.equal(error('magic', {input: 'abc', actions: [{method: 'update', args: [1, 1, 'x']}]}).name, 'MagicStringError'));
test('reversed update raises MagicStringError', () => assert.equal(error('magic', {input: 'abc', actions: [{method: 'update', args: [2, 1, 'x']}]}).name, 'MagicStringError'));
test('move into itself raises MagicStringError', () => assert.equal(error('magic', {input: 'abc', actions: [{method: 'move', args: [0, 2, 1]}]}).name, 'MagicStringError'));
test('decoded map has source metadata', () => { const value = magic('abc', [{method: 'generateDecodedMap', args: [{source: 'in.js', file: 'out.js', includeContent: true}]}]).results[0]; assert.deepEqual(value.sources, ['in.js']); assert.deepEqual(value.sourcesContent, ['abc']); });
test('encoded map is version three', () => { const value = magic('abc', [{method: 'generateMap', args: [{source: 'in.js', file: 'out.js'}]}]).results[0]; assert.equal(value.version, 3); assert.equal(value.file, 'out.js'); assert.equal(typeof value.mappings, 'string'); });
test('ignoreList is emitted in source maps', () => { const value = magic('abc', [], {filename: 'in.js', ignoreList: true}); const map = magic('abc', [{method: 'generateMap', args: [{source: 'in.js'}]}], {filename: 'in.js', ignoreList: true}).results[0]; assert.deepEqual(map.x_google_ignoreList, [0]); void value; });
test('stored names are included after overwrite', () => { const value = magic('foo', [{method: 'overwrite', args: [0, 3, 'bar', {storeName: true}]}, {method: 'generateDecodedMap', args: [{source: 'in.js'}]}]).results[1]; assert.deepEqual(value.names, ['foo']); });
test('bundle joins sources with its separator', () => assert.equal(bundle({options: {separator: '|'}, sources: [{input: 'a'}, {input: 'b'}]}).final.string, 'a|b'));
test('bundle supports intro and prepend', () => assert.equal(bundle({options: {intro: 'I'}, sources: [{input: 'a'}], actions: [{method: 'prepend', args: ['^']}]}).final.string, '^Ia'));
test('bundle supports per-source separators', () => assert.equal(bundle({options: {separator: '|'}, sources: [{input: 'a'}, {input: 'b', separator: '/'}]}).final.string, 'a/b'));
test('bundle append defaults to no separator', () => assert.equal(bundle({options: {separator: '|'}, sources: [{input: 'a'}], actions: [{method: 'append', args: ['b']}]}).final.string, 'ab'));
test('bundle clone is independent', () => { const value = bundle({sources: [{input: 'a'}], cloneActions: [{method: 'append', args: ['!']} ]}); assert.equal(value.clone.string, 'a!'); assert.equal(value.originalAfterClone.string, 'a'); });
test('bundle length includes separators and intro', () => assert.equal(bundle({options: {intro: 'I', separator: '|'}, sources: [{input: 'a'}, {input: 'bb'}]}).final.length, 5));
test('bundle isEmpty handles whitespace sources', () => assert.equal(bundle({sources: [{input: ' '}, {input: '\n'}]}).final.isEmpty, true));
test('duplicate filename with different content raises MagicStringError', () => assert.equal(error('bundle', {sources: [{input: 'a', filename: 'same.js'}, {input: 'b', filename: 'same.js'}]}).name, 'MagicStringError'));
