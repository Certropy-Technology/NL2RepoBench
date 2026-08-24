import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('preserves an external import', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-external-'));
  writeFileSync(join(root, 'main.js'), "import answer from 'external-lib'; export { answer };\n");
  const api = loadRollup();
  const bundle = await api.rollup({ input: join(root, 'main.js'), external: ['external-lib'] });
  const result = await bundle.generate({ format: 'es' });
  assert.match(result.output[0].code, /external-lib/);
  await bundle.close();
});
