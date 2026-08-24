import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('supports deterministic code splitting for multiple inputs', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-split-'));
  writeFileSync(join(root, 'shared.js'), 'export const shared = 1;\n');
  writeFileSync(join(root, 'a.js'), "import { shared } from './shared.js'; export { shared };\n");
  writeFileSync(join(root, 'b.js'), "import { shared } from './shared.js'; export { shared };\n");
  const api = loadRollup();
  const bundle = await api.rollup({ input: { a: join(root, 'a.js'), b: join(root, 'b.js') } });
  const result = await bundle.generate({ dir: join(root, 'out'), format: 'es' });
  assert.ok(result.output.filter(item => item.type === 'chunk').length >= 2);
  assert.ok(result.output.every(item => typeof item.fileName === 'string'));
  await bundle.close();
});
