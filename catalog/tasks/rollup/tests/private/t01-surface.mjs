import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadRollup } from './test_client.mjs';

test('exposes the documented CommonJS surface', () => {
  const rollup = loadRollup();
  assert.equal(rollup.VERSION, '4.62.5');
  for (const name of ['rollup', 'watch', 'defineConfig']) assert.equal(typeof rollup[name], 'function');
});
