import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadRollup } from './test_client.mjs';

test('writes a requested output file', async () => {
  const root = mkdtempSync(join(tmpdir(), 'rollup-write-'));
  const input = join(root, 'main.js');
  const output = join(root, 'dist', 'bundle.js');
  writeFileSync(input, 'export default 7;\n');
  const api = loadRollup();
  const bundle = await api.rollup({ input });
  await bundle.write({ file: output, format: 'es' });
  assert.match(readFileSync(output, 'utf8'), /default/);
  await bundle.close();
});
