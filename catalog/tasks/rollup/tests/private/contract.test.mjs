import assert from 'node:assert/strict';
import {test} from 'node:test';
import {call} from './test_client.mjs';

function value(operation, payload = {}) {
  const response = call(operation, payload);
  assert.equal(response.ok, true, response.message);
  return response.value;
}

function onlyChunk(result) {
  assert.equal(result.output.length, 1);
  assert.equal(result.output[0].type, 'chunk');
  return result.output[0];
}

test('exports the installable self-contained Rollup surface', () => {
  const inventory = value('inventory');
  assert.equal(inventory.version, '4.62.5');
  assert.deepEqual(inventory.functions, [['rollup', 'function'], ['watch', 'function'], ['defineConfig', 'function']]);
  assert.deepEqual({main: inventory.main, types: inventory.types, bin: inventory.bin}, {
    main: 'dist/rollup.js', types: 'dist/rollup.d.ts', bin: 'dist/bin/rollup',
  });
  assert.ok(inventory.wasmBytes > 100_000);
  assert.deepEqual(inventory.nativeAddons, []);
  assert.deepEqual(inventory.lifecycleScripts, []);
});

test('defineConfig preserves object and array configuration values', () => {
  assert.deepEqual(value('defineConfig', {config: [{input: 'a.js'}, {input: 'b.js', treeshake: false}]}), [
    {input: 'a.js'}, {input: 'b.js', treeshake: false},
  ]);
});

test('bundles local modules as ES and tree-shakes unused exports', () => {
  const chunk = onlyChunk(value('bundle', {
    files: {
      'main.js': "import {used} from './dep.js'; export const answer = used + 1;",
      'dep.js': "export const used = 41; export const unused = 'REMOVE_ME';",
    },
    input: 'main.js',
    output: {format: 'es'},
  }));
  assert.equal(chunk.fileName, 'main.js');
  assert.deepEqual(chunk.exports, ['answer']);
  assert.match(chunk.code, /41/);
  assert.doesNotMatch(chunk.code, /REMOVE_ME/);
});

test('generates CommonJS output with named exports', () => {
  const chunk = onlyChunk(value('bundle', {
    files: {'main.js': 'export const answer = 42;'}, input: 'main.js', output: {format: 'cjs'},
  }));
  assert.deepEqual(chunk.exports, ['answer']);
  assert.match(chunk.code, /exports\.answer\s*=\s*answer/);
});

test('generates named IIFE output', () => {
  const chunk = onlyChunk(value('bundle', {
    files: {'main.js': 'export const answer = 42;'}, input: 'main.js', output: {format: 'iife', name: 'Demo'},
  }));
  assert.match(chunk.code, /var Demo\s*=\s*\(function/);
  assert.match(chunk.code, /exports\.answer/);
});

test('code-splits multiple entries deterministically', () => {
  const payload = {
    files: {
      'a.js': "import {shared} from './shared.js'; export const a = shared + 'a';",
      'b.js': "import {shared} from './shared.js'; export const b = shared + 'b';",
      'shared.js': "export const shared = 's';",
    },
    input: {alpha: 'a.js', beta: 'b.js'},
    output: {format: 'es', entryFileNames: '[name].js', chunkFileNames: 'chunks/[name].js'},
  };
  const first = value('bundle', payload).output.map(item => item.fileName);
  const second = value('bundle', payload).output.map(item => item.fileName);
  assert.deepEqual(first, second);
  assert.deepEqual(first.sort(), ['alpha.js', 'beta.js', 'chunks/shared.js']);
});

test('runs resolveId, load, and transform plugin hooks', () => {
  const chunk = onlyChunk(value('bundle', {
    files: {'main.js': "import {value} from 'virtual:data'; export const result = value;"},
    input: 'main.js',
    plugin: {
      virtual: {'virtual:data': "export const value = 'before';"},
      replace: {file: 'main.js', from: 'value;', to: "value + '-after';"},
    },
    output: {format: 'es'},
  }));
  assert.match(chunk.code, /'before'/);
  assert.match(chunk.code, /'-after'/);
});

test('preserves external modules in generated output', () => {
  const chunk = onlyChunk(value('bundle', {
    files: {'main.js': "import value from 'external-pkg'; export default value;"},
    input: 'main.js', external: ['external-pkg'], output: {format: 'es'},
  }));
  assert.deepEqual(chunk.imports, ['external-pkg']);
  assert.match(chunk.code, /from 'external-pkg'/);
});

test('writes generated output and closes the bundle', () => {
  const result = value('write', {
    files: {'main.js': 'export default 21 * 2;'}, input: 'main.js', file: 'out/bundle.js', output: {format: 'es'},
  });
  assert.equal(result.file, 'out/bundle.js');
  assert.match(result.code, /21 \* 2/);
});

test('rejects missing entry points with a stable error code', () => {
  const error = value('error', {files: {}, input: 'missing.js', output: {format: 'es'}});
  assert.equal(error.threw, true);
  assert.equal(error.name, 'RollupError');
  assert.equal(error.code, 'UNRESOLVED_ENTRY');
  assert.match(error.message, /Could not resolve entry module/);
});

test('CLI reports its version and bundles files and standard input', () => {
  const version = value('cli', {args: ['--version']});
  assert.equal(version.status, 0);
  assert.equal(version.stdout.trim(), 'rollup v4.62.5');

  const file = value('cli', {
    files: {'main.js': 'export const answer = 42;'},
    args: ['$ROOT/main.js', '--format', 'es', '--file', '$ROOT/bundle.js'],
    read: 'bundle.js',
  });
  assert.equal(file.status, 0, file.stderr);
  assert.match(file.output, /const answer = 42/);

  const stdin = value('cli', {args: ['-', '--format', 'es'], stdin: 'export default 7;'});
  assert.equal(stdin.status, 0, stdin.stderr);
  assert.match(stdin.stdout, /var \w+ = 7/);
  assert.match(stdin.stdout, /export \{ \w+ as default \}/);
});
