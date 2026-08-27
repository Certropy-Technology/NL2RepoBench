import assert from "node:assert/strict";
import test from "node:test";
import { scenario } from "./test_client.mjs";

test("basic database creation, rows, and open state", () => {
  assert.deepEqual(scenario("basic"), { rows: [{ id: 1, name: "Ada" }, { id: 2, name: "Linus" }], count: 2, open: true });
});

test("positional and named parameter bindings", () => {
  assert.deepEqual(scenario("bindings"), { positional: 1, named: 1, changes: 2 });
});

test("ordered statement iteration", () => {
  assert.deepEqual(scenario("iteration"), { values: [1, 2, 3] });
});

test("commit rollback and nested transaction isolation", () => {
  assert.deepEqual(scenario("transactions"), { committed: "committed", rolledBack: 0, nested: ["committed", "outer"] });
});

test("registered scalar and aggregate functions", () => {
  assert.deepEqual(scenario("functions"), { scalar: 8, aggregate: 5 });
});

test("pragma results and simple mode", () => {
  assert.deepEqual(scenario("pragma"), { foreignKeys: 1, cacheSizeType: "number" });
});

test("in-memory serialization and deserialization", () => {
  assert.deepEqual(scenario("serialization"), { before: "saved", after: "saved" });
});

test("constraint and closed database errors", () => {
  const result = scenario("errors");
  assert.equal(result.constraintCode, "SQLITE_CONSTRAINT_UNIQUE");
  assert.equal(result.closedError, "SQLITE_MISUSE");
});

test("pluck raw and safe integer modes", () => {
  assert.deepEqual(scenario("statementModes"), { pluck: "x", raw: [42, "x"], safeIntegerType: "bigint" });
});

test("statement column metadata", () => {
  assert.deepEqual(scenario("columns"), { names: ["first", "second"], count: 2 });
});

test("readonly file database rejects writes", () => {
  const result = scenario("readonly");
  assert.equal(result.readonly, true);
  assert.match(result.writeCode, /^SQLITE_READONLY/);
});

test("CommonJS package root API shape", () => {
  assert.deepEqual(scenario("apiShape"), { hasDatabase: true, hasSqliteError: true, methods: ["prepare", "exec", "pragma", "transaction", "function", "aggregate", "serialize", "close"] });
});
