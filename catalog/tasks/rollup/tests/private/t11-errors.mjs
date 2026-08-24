import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadRollup } from './test_client.mjs';

test('rejects an unresolved entry with a structured error code', async () => {
  const api = loadRollup();
  await assert.rejects(
    api.rollup({ input: '/definitely/missing/rollup-entry.js' }),
    error => error && error.code === 'UNRESOLVED_ENTRY'
  );
});
