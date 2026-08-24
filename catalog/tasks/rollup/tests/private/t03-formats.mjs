import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('generates valid CommonJS and IIFE formats', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-formats-'));
  writeFileSync(join(root, 'main.js'), 'export const answer = 42;\n');
  const api = loadRollup();
  const bundle = await api.rollup({ input: join(root, 'main.js') });
  const cjs = await bundle.generate({ format: 'cjs' });
  const iife = await bundle.generate({ format: 'iife', name: 'Demo' });
  assert.match(cjs.output[0].code, /exports\.answer/);
  assert.match(iife.output[0].code, /Demo/);
  await bundle.close();
});
