import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadRollup } from './test_client.mjs';

test('runs resolveId, load, and transform plugin hooks', async () => {
  const api = loadRollup();
  const bundle = await api.rollup({
    input: 'virtual:entry',
    plugins: [{
      name: 'fixture',
      resolveId(id) { return id === 'virtual:entry' ? id : null; },
      load(id) { return id === 'virtual:entry' ? 'export const result = "raw";' : null; },
      transform(code) { return code.replace('raw', 'transformed'); }
    }]
  });
  const result = await bundle.generate({ format: 'es' });
  assert.match(result.output[0].code, /transformed/);
  await bundle.close();
});
