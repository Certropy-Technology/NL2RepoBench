import assert from 'node:assert/strict';
import test from 'node:test';
import { call, callError } from './test_client.mjs';

test('transforms TypeScript with the ts loader', () => {
  const result = call('transformSync', ['const answer: number = 1 + 2', { loader: 'ts' }]);
  assert.equal(result.code, 'const answer = 1 + 2;\n');
  assert.deepEqual(result.warnings, []);
});

test('minifies syntax without changing the expression result', () => {
  const result = call('transformSync', ['const answer = 1 + 2', { minifySyntax: true }]);
  assert.equal(result.code, 'const answer = 3;\n');
});

test('supports JSX through the jsx loader', () => {
  const result = call('transformSync', ['export default <Button enabled={true} />', { loader: 'jsx', format: 'cjs' }]);
  assert.match(result.code, /Button/);
  assert.match(result.code, /module\.exports/);
});

test('returns a source map when requested', () => {
  const result = call('transformSync', ['let value = 1', { sourcemap: 'inline', sourcefile: 'input.ts', loader: 'ts' }]);
  assert.match(result.code, /sourceMappingURL=data:application\/json;base64,/);
  assert.equal(typeof result.map, 'string');
});

test('builds stdin into outputFiles without writing to disk', () => {
  const result = call('buildSync', [{
    stdin: { contents: 'export const value = 1 + 2', sourcefile: 'input.js', loader: 'js' },
    write: false,
    format: 'cjs',
    platform: 'neutral',
  }]);
  assert.equal(result.errors.length, 0);
  assert.equal(result.outputFiles.length, 1);
  assert.match(result.outputFiles[0].text, /module\.exports/);
  assert.match(result.outputFiles[0].text, /value/);
});

test('bundles an entry point and emits a metafile', () => {
  const result = call('buildSync', [{
    stdin: { contents: 'export const value = 7', sourcefile: 'entry.js' },
    write: false,
    bundle: true,
    format: 'esm',
    metafile: true,
    platform: 'neutral',
  }]);
  assert.equal(result.errors.length, 0);
  assert.equal(result.outputFiles.length, 1);
  assert.match(result.outputFiles[0].text, /value/);
  const metafile = typeof result.metafile === 'string' ? JSON.parse(result.metafile) : result.metafile;
  assert.ok(metafile.inputs['entry.js']);
});

test('rejects invalid JavaScript with a structured error', () => {
  const result = callError('transformSync', ['const =', { loader: 'js' }]);
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, 'Error');
  assert.match(result.message, /Expected/);
});

test('formats an error message deterministically', () => {
  const messages = [{ text: 'unexpected token', location: { file: 'input.js', line: 2, column: 3, length: 1 } }];
  const result = call('formatMessagesSync', [messages, { kind: 'error', color: false }]);
  assert.equal(result.length, 1);
  assert.match(result[0], /\[ERROR\] unexpected token/);
  assert.match(result[0], /input\.js:2:3/);
});

test('analyzes a JSON metafile', () => {
  const metafile = JSON.stringify({
    inputs: { 'entry.js': { bytes: 18, imports: [] } },
    outputs: { 'out.js': { imports: [], exports: ['value'], entryPoint: 'entry.js', inputs: { 'entry.js': { bytesInOutput: 18 } }, bytes: 18 } },
  });
  const result = call('analyzeMetafileSync', [metafile, { color: false }]);
  assert.match(result, /entry\.js/);
  assert.match(result, /out\.js/);
});

test('returns a stable version from the synchronous API surface', () => {
  const result = call('transformSync', ['export const version = "0.28.2"', { format: 'esm' }]);
  assert.match(result.code, /version/);
});

test('returns empty warnings and errors for a valid transform', () => {
  const result = call('transformSync', ['/* comment */\nconst x = 1', { loader: 'js' }]);
  assert.deepEqual(result.errors ?? [], []);
  assert.deepEqual(result.warnings ?? [], []);
});
