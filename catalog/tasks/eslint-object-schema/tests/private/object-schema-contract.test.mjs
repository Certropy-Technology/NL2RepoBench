import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { test } from "node:test";

const site = resolve(process.env.NODE_CANDIDATE_SITE ?? process.cwd());
const require = createRequire(`${site}/package.json`);
const packageRoot = resolve(site, "node_modules/@eslint/object-schema");
const cjs = require("@eslint/object-schema");

test("CommonJS root exposes the three public classes", () => {
  assert.deepEqual(Object.keys(cjs).sort(), ["MergeStrategy", "ObjectSchema", "ValidationStrategy"]);
  for (const name of ["MergeStrategy", "ObjectSchema", "ValidationStrategy"]) {
    assert.equal(typeof cjs[name], "function", name);
  }
});

test("ESM root exposes the same public classes and metadata", async () => {
  const esm = await import(pathToFileURL(resolve(packageRoot, "dist/esm/index.js")));
  assert.deepEqual(Object.keys(esm).sort(), ["MergeStrategy", "ObjectSchema", "ValidationStrategy"]);
  assert.equal(JSON.parse(readFileSync(resolve(packageRoot, "package.json"))).version, "3.0.5");
});

test("built-in merge strategies implement overwrite, replace, and assign", () => {
  const { MergeStrategy } = cjs;
  assert.equal(MergeStrategy.overwrite("first", undefined), undefined);
  assert.equal(MergeStrategy.replace("first", undefined), "first");
  assert.equal(MergeStrategy.replace("first", null), null);
  const first = { a: 1 };
  const second = { b: 2, a: 3 };
  const result = MergeStrategy.assign(first, second);
  assert.deepEqual(result, { a: 3, b: 2 });
  assert.notEqual(result, first);
  assert.notEqual(result, second);
});

test("built-in validation strategies accept their documented values", () => {
  const { ValidationStrategy } = cjs;
  ValidationStrategy.array([]);
  ValidationStrategy.boolean(false);
  ValidationStrategy.number(0);
  ValidationStrategy.object([]);
  ValidationStrategy.object(new Date());
  ValidationStrategy["object?"](null);
  ValidationStrategy.string("");
  ValidationStrategy["string!"]("value");
});

test("built-in validation strategies reject invalid values with TypeError", () => {
  const { ValidationStrategy } = cjs;
  for (const [name, value, message] of [
    ["array", {}, "Expected an array."],
    ["boolean", 1, "Expected a boolean."],
    ["number", "1", "Expected a number."],
    ["object", null, "Expected an object."],
    ["object?", "value", "Expected an object or null."],
    ["string", 1, "Expected a string."],
    ["string!", "", "Expected a non-empty string."],
  ]) {
    assert.throws(() => ValidationStrategy[name](value), { name: "TypeError", message });
  }
});

test("constructor rejects missing definitions and incomplete strategies", () => {
  const { ObjectSchema } = cjs;
  assert.throws(() => new ObjectSchema(), { message: "Schema definitions missing." });
  assert.throws(() => new ObjectSchema({ value: {} }), /must have a merge property/);
  assert.throws(() => new ObjectSchema({ value: { merge: "unknown", validate() {} } }), /valid merge strategy/);
  assert.throws(() => new ObjectSchema({ value: { merge() {} } }), /must have a validate\(\) method/);
});

test("hasKey reports definitions without changing the input definition object", () => {
  const { ObjectSchema } = cjs;
  const definitions = { value: { merge: "replace", validate: "string" } };
  const before = JSON.stringify(definitions);
  const schema = new ObjectSchema(definitions);
  assert.equal(schema.hasKey("value"), true);
  assert.equal(schema.hasKey("missing"), false);
  assert.equal(JSON.stringify(definitions), before);
});

test("custom strategies validate and merge two objects", () => {
  const { ObjectSchema } = cjs;
  const calls = [];
  const schema = new ObjectSchema({
    count: {
      merge(first = 0, second = 0) { calls.push([first, second]); return first + second; },
      validate(value) { if (typeof value !== "number") throw new TypeError("count must be numeric"); },
    },
  });
  assert.deepEqual(schema.merge({ count: 2 }, { count: 3 }), { count: 5 });
  assert.deepEqual(calls, [[0, 2], [2, 3]]);
});

test("merge accepts more than two objects in input order", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ values: { merge: (a = [], b = []) => a.concat(b), validate: "array" } });
  assert.deepEqual(schema.merge({ values: [1] }, { values: [2] }, { values: [3] }), { values: [1, 2, 3] });
});

test("named merge strategies are resolved by ObjectSchema", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({
    replace: { merge: "replace", validate() {} },
    overwrite: { merge: "overwrite", validate() {} },
    assign: { merge: "assign", validate: "object" },
  });
  assert.deepEqual(schema.merge(
    { replace: "a", overwrite: "a", assign: { left: 1 } },
    { replace: undefined, overwrite: undefined, assign: { right: 2 } },
  ), { replace: "a", overwrite: "a", assign: { left: 1, right: 2 } });
});

test("a strategy returning undefined removes the key from the result", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ value: { merge: () => undefined, validate: "string" } });
  const result = schema.merge({ value: "first" }, { value: "second" });
  assert.equal(Object.hasOwn(result, "value"), false);
});

test("merge requires at least two non-null objects", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ value: { merge: "replace", validate() {} } });
  assert.throws(() => schema.merge({ value: 1 }), /at least two arguments/);
  assert.throws(() => schema.merge({}, null), /All arguments must be objects/);
  assert.throws(() => schema.merge({}, "value"), /All arguments must be objects/);
});

test("merge validates every input before applying strategies", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ value: { merge: "replace", validate: "string" } });
  assert.throws(() => schema.merge({ value: "ok" }, { value: 3 }), /Key "value": Expected a string/);
});

test("validate rejects unknown keys", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ known: { merge: "replace", validate() {} } });
  assert.throws(() => schema.validate({ unknown: true }), { message: 'Unexpected key "unknown" found.' });
});

test("validate enforces required keys", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ id: { required: true, merge: "replace", validate: "string!" } });
  assert.throws(() => schema.validate({}), { message: 'Missing required key "id".' });
  schema.validate({ id: "x" });
});

test("validate enforces dependent keys", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({
    date: { merge: "replace", validate: "string" },
    time: { requires: ["date"], merge: "replace", validate: "string" },
  });
  assert.throws(() => schema.validate({ time: "12:00" }), /Key "time" requires keys "date"/);
  schema.validate({ date: "2026-01-01", time: "12:00" });
});

test("nested schemas recursively validate and merge", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({
    config: { schema: {
      name: { merge: "replace", validate: "string!" },
      flags: { merge: "assign", validate: "object" },
    } },
  });
  assert.deepEqual(schema.merge(
    { config: { name: "one", flags: { a: true } } },
    { config: { name: "two", flags: { b: false } } },
  ), { config: { name: "two", flags: { a: true, b: false } } });
  assert.throws(() => schema.validate({ config: { name: "" } }), /Key "config": Key "name": Expected a non-empty string/);
});

test("nested merge returns fresh objects and does not mutate inputs", () => {
  const { ObjectSchema } = cjs;
  const schema = new ObjectSchema({ child: { schema: { value: { merge: "replace", validate: "number" } } } });
  const first = { child: { value: 1 } };
  const second = { child: { value: 2 } };
  const result = schema.merge(first, second);
  assert.deepEqual(first, { child: { value: 1 } });
  assert.deepEqual(second, { child: { value: 2 } });
  assert.notEqual(result.child, first.child);
});

test("validator errors are wrapped with their original cause", () => {
  const { ObjectSchema } = cjs;
  const source = new Error("bad value");
  const schema = new ObjectSchema({ value: { merge: "replace", validate() { throw source; } } });
  assert.throws(() => schema.validate({ value: 1 }), error => {
    assert.equal(error.message, 'Key "value": bad value');
    assert.equal(error.cause, source);
    return true;
  });
});

test("merge errors preserve custom source properties", () => {
  const { ObjectSchema } = cjs;
  const source = new Error("cannot combine");
  source.code = "E_COMBINE";
  const schema = new ObjectSchema({ value: { merge() { throw source; }, validate() {} } });
  assert.throws(() => schema.merge({ value: 1 }, { value: 2 }), error => {
    assert.equal(error.message, 'Key "value": cannot combine');
    assert.equal(error.code, "E_COMBINE");
    assert.equal(error.cause, source);
    return true;
  });
});

