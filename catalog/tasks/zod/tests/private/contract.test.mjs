import assert from "node:assert/strict";
import test from "node:test";
import {readFileSync} from "node:fs";
import {join} from "node:path";
import {callCandidate} from "./test_client.mjs";

let sequence = 0;
const validate = (schema, value) => callCandidate({
  id: `case-${++sequence}`,
  operation: "validate",
  schema,
  value,
});

test("package metadata and root constructors", () => {
  const site = process.env.NODE_CANDIDATE_SITE;
  const manifest = JSON.parse(readFileSync(join(site, "node_modules/zod/package.json"), "utf8"));
  assert.equal(manifest.name, "zod");
  assert.equal(manifest.version, "4.4.3");
  assert.equal(manifest.type, "module");
  const response = callCandidate({id: "inventory", operation: "inventory"});
  assert.equal(response.success, true);
  assert.equal(response.data.hasNamedZ, true);
  assert.equal(response.data.hasDefaultZAlias, true);
  assert.deepEqual(response.data.constructors, ["string", "number", "boolean", "literal", "enum", "array", "object", "strictObject", "looseObject", "union"]);
});

test("string accepts a string", () => {
  assert.deepEqual(validate({type: "string"}, "alpha"), {id: "case-1", success: true, data: "alpha"});
});

test("string rejects a number", () => {
  const result = validate({type: "string"}, 7);
  assert.equal(result.success, false);
  assert.deepEqual(result.issues, [{code: "invalid_type", path: [], message: "Invalid input: expected string, received number"}]);
});

test("string minimum length reports too_small", () => {
  const result = validate({type: "string", minLength: 3}, "ab");
  assert.deepEqual(result.issues, [{code: "too_small", path: [], message: "Too small: expected string to have >=3 characters"}]);
});

test("string maximum length reports too_big", () => {
  const result = validate({type: "string", maxLength: 3}, "abcd");
  assert.deepEqual(result.issues, [{code: "too_big", path: [], message: "Too big: expected string to have <=3 characters"}]);
});

test("string trim and lowercase transformations are ordered", () => {
  assert.equal(validate({type: "string", trim: true, toLowerCase: true}, "  AbC  ").data, "abc");
});

test("email validation accepts a conventional address", () => {
  assert.equal(validate({type: "string", email: true}, "a@example.com").success, true);
});

test("email validation rejects malformed text", () => {
  const result = validate({type: "string", email: true}, "not-an-email");
  assert.deepEqual(result.issues, [{code: "invalid_format", path: [], message: "Invalid email address"}]);
});

test("number minimum and maximum are inclusive", () => {
  assert.equal(validate({type: "number", min: 1, max: 3}, 1).success, true);
  assert.equal(validate({type: "number", min: 1, max: 3}, 3).success, true);
});

test("integer validation rejects fractions", () => {
  const result = validate({type: "number", int: true}, 1.5);
  assert.deepEqual(result.issues, [{code: "invalid_type", path: [], message: "Invalid input: expected int, received number"}]);
});

test("positive and nonnegative checks distinguish zero", () => {
  assert.equal(validate({type: "number", positive: true}, 0).success, false);
  assert.equal(validate({type: "number", nonnegative: true}, 0).success, true);
});

test("boolean rejects strings", () => {
  const result = validate({type: "boolean"}, "true");
  assert.deepEqual(result.issues, [{code: "invalid_type", path: [], message: "Invalid input: expected boolean, received string"}]);
});

test("literal compares JSON scalar identity", () => {
  assert.equal(validate({type: "literal", value: "ready"}, "ready").success, true);
  assert.equal(validate({type: "literal", value: "ready"}, "READY").success, false);
});

test("enum accepts only listed strings", () => {
  assert.equal(validate({type: "enum", values: ["red", "green", "blue"]}, "green").success, true);
  const result = validate({type: "enum", values: ["red", "green", "blue"]}, "amber");
  assert.deepEqual(result.issues, [{code: "invalid_value", path: [], message: "Invalid option: expected one of \"red\"|\"green\"|\"blue\""}]);
});

test("array validates and returns each element", () => {
  assert.deepEqual(validate({type: "array", item: {type: "number", int: true}}, [1, 2, 3]).data, [1, 2, 3]);
});

test("array item errors preserve numeric paths", () => {
  const result = validate({type: "array", item: {type: "string"}}, ["ok", 2]);
  assert.deepEqual(result.issues, [{code: "invalid_type", path: [1], message: "Invalid input: expected string, received number"}]);
});

test("array exact length is enforced", () => {
  const result = validate({type: "array", item: {type: "boolean"}, length: 2}, [true]);
  assert.deepEqual(result.issues, [{code: "too_small", path: [], message: "Too small: expected array to have exactly 2 items"}]);
});

test("object strips unknown keys by default", () => {
  const schema = {type: "object", properties: {name: {type: "string"}}};
  assert.deepEqual(validate(schema, {name: "Ada", ignored: 1}).data, {name: "Ada"});
});

test("strict object rejects unknown keys", () => {
  const schema = {type: "object", unknownKeys: "strict", properties: {name: {type: "string"}}};
  const result = validate(schema, {name: "Ada", extra: true});
  assert.deepEqual(result.issues, [{code: "unrecognized_keys", path: [], message: "Unrecognized key: \"extra\""}]);
});

test("passthrough object preserves unknown keys", () => {
  const schema = {type: "object", unknownKeys: "passthrough", properties: {name: {type: "string"}}};
  assert.deepEqual(validate(schema, {name: "Ada", extra: true}).data, {name: "Ada", extra: true});
});

test("nested object errors preserve full paths", () => {
  const schema = {type: "object", properties: {user: {type: "object", properties: {age: {type: "number", int: true}}}}};
  const result = validate(schema, {user: {age: "old"}});
  assert.deepEqual(result.issues, [{code: "invalid_type", path: ["user", "age"], message: "Invalid input: expected number, received string"}]);
});

test("optional and default wrappers handle missing object properties", () => {
  const schema = {type: "object", properties: {
    note: {type: "optional", inner: {type: "string"}},
    count: {type: "default", inner: {type: "number", int: true}, value: 1},
  }};
  assert.deepEqual(validate(schema, {}).data, {count: 1});
});

test("nullable accepts null but not missing required properties", () => {
  const schema = {type: "object", properties: {value: {type: "nullable", inner: {type: "string"}}}};
  assert.deepEqual(validate(schema, {value: null}).data, {value: null});
  const result = validate(schema, {});
  assert.deepEqual(result.issues, [{code: "invalid_type", path: ["value"], message: "Invalid input: expected string, received undefined"}]);
});

test("union accepts either option and reports invalid_union", () => {
  const schema = {type: "union", options: [{type: "string"}, {type: "number", int: true}]};
  assert.equal(validate(schema, "ok").success, true);
  assert.equal(validate(schema, 4).success, true);
  const result = validate(schema, false);
  assert.deepEqual(result.issues, [{code: "invalid_union", path: [], message: "Invalid input"}]);
});
