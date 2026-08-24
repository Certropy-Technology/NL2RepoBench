import test from "node:test";
import assert from "node:assert/strict";
import { callScenario } from "./test_client.mjs";

const expected = {
  basic: { rows: [{ id: 1, name: "Ada" }, { id: 2, name: "Grace" }], count: 2, open: true },
  bindings: { positional: { value: "positional", number: 7 }, named: { value: "positional", number: 7 }, changes: 1 },
  iteration: { values: [1, 2, 3] },
  transactions: { committed: [1, 2], rolledBack: [1, 2], nested: [1, 2, 3, 4] },
  functions: { scalar: 7, aggregate: 9 },
  pragma: { foreignKeys: 1, cacheSizeType: "number" },
  serialization: { before: "persisted", after: "persisted" },
  errors: { constraintCode: "SQLITE_CONSTRAINT_UNIQUE", closedError: true },
  statementModes: { pluck: 7, raw: [7, 8], safeIntegerType: "bigint" },
  columns: { names: ["first", "second"], count: 2 },
  readonly: { readonly: true, writeCode: "SQLITE_READONLY" },
  apiShape: { hasDatabase: true, hasSqliteError: true, methods: ["exec", "prepare", "transaction", "pragma", "function", "aggregate", "serialize", "deserialize", "close"] },
};

for (const [name, value] of Object.entries(expected)) {
  test(`better-sqlite3 scenario: ${name}`, () => assert.deepEqual(callScenario(name), value));
}
