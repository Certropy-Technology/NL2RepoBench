import assert from 'node:assert/strict';
import {test} from 'node:test';

const client = await import(process.env.NODE_TEST_CLIENT);

test('package metadata and declaration entry are exact', () => {
  const value = client.inventory();
  assert.deepEqual(
    {name: value.packageName, version: value.packageVersion, type: value.type, main: value.main, types: value.types, lock: value.lockfileVersion},
    {name: 'process-warning', version: '5.1.0', type: 'commonjs', main: 'index.js', types: 'types/index.d.ts', lock: 3},
  );
  assert.equal(value.declarationUsesExportEquals, true);
});

test('root export names are exact', () => {
  assert.deepEqual(client.inventory().exportNames, ['createDeprecation', 'createWarning', 'default', 'processWarning', 'spyWarning']);
});

test('default and processWarning aliases reference the root export', () => {
  const value = client.inventory();
  assert.equal(value.defaultSame, true);
  assert.equal(value.processWarningSame, true);
});
