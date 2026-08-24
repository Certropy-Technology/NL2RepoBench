import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('bundles a local dependency and keeps the used export', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-basic-'));
  writeFileSync(join(root, 'dep.js'), 'export const value = 40 + 2; export const unused = 99;\n');
  writeFileSync(join(root, 'main.js'), "import { value } from './dep.js'; export { value };\n");
  const api = loadRollup();
  const bundle = await api.rollup({ input: join(root, 'main.js') });
  const result = await bundle.generate({ format: 'es' });
  const code = result.output[0].code;
  assert.match(code, /value/);
  assert.doesNotMatch(code, /unused/);
  assert.equal(result.output[0].type, 'chunk');
  await bundle.close();
});
