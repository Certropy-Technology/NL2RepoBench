import assert from "node:assert/strict";
import test from "node:test";
import { call } from "./test_client.mjs";

test("basic GET route returns JSON", () => {
  const out = call({ op: "basic" });
  assert.equal(out.statusCode, 200);
  assert.deepEqual(out.json, { hello: "world" });
});

test("params and query are exposed", () => {
  assert.deepEqual(call({ op: "params" }).json, { id: "42", query: { active: "true" } });
});

test("POST JSON payload is parsed", () => {
  assert.deepEqual(call({ op: "post" }).json, { body: { message: "héllo", count: 2 }, contentType: "application/json" });
});

test("generic and shorthand methods preserve status and method", () => {
  const out = call({ op: "methods" });
  assert.equal(out.put.statusCode, 202);
  assert.deepEqual(out.put.json, { id: "a", method: "PUT" });
  assert.equal(out.del.statusCode, 204);
});

test("static, parameter, and wildcard routes have deterministic precedence", () => {
  const out = call({ op: "precedence" });
  assert.equal(out.static.json.route, "static");
  assert.equal(out.param.json.route, "param");
  assert.equal(out.wildcard.json.route, "wildcard");
});

test("request hooks run in lifecycle order", () => {
  const out = call({ op: "hooks" });
  assert.deepEqual(out.events, ["onRequest", "preParsing", "preValidation", "preHandler", "handler", "onSend", "onResponse"]);
});

test("query schema accepts valid input and rejects invalid input", () => {
  const out = call({ op: "schema" });
  assert.equal(out.valid.statusCode, 200);
  assert.deepEqual(out.valid.json, { q: "fastify" });
  assert.equal(out.invalid.statusCode, 400);
});

test("response schema keeps declared response fields", () => {
  const out = call({ op: "response-schema" });
  assert.equal(out.statusCode, 200);
  assert.deepEqual(out.json, { ok: true });
});

test("custom error handler formats thrown errors", () => {
  const out = call({ op: "error" });
  assert.equal(out.statusCode, 418);
  assert.deepEqual(out.json, { handled: true, message: "boom" });
});

test("custom not-found handler receives the URL", () => {
  const out = call({ op: "not-found" });
  assert.equal(out.statusCode, 404);
  assert.deepEqual(out.json, { missing: "/missing" });
});

test("plugin prefix and encapsulated hook work", () => {
  const out = call({ op: "plugin" });
  assert.deepEqual(out.child.json, { scope: "child", pluginSeen: true });
  assert.deepEqual(out.root.json, { scope: "root" });
});

test("hasRoute and ready expose lifecycle state", () => {
  const out = call({ op: "lifecycle" });
  assert.equal(out.hasRoute, true);
  assert.deepEqual(out.response.json, { ready: true });
});
