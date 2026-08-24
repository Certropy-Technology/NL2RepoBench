import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('emits an inline sourcemap when requested', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-map-'));
  writeFileSync(join(root, 'main.js'), 'export const mapped = true;\n');
  const api = loadRollup();
  const bundle = await api.rollup({ input: join(root, 'main.js') });
  const result = await bundle.generate({ format: 'es', sourcemap: 'inline' });
  assert.match(result.output[0].code, /sourceMappingURL=data:application\/json(?:;charset=utf-8)?;base64,/);
  await bundle.close();
});
