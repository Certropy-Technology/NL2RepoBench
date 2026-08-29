import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {join} from "node:path";
import test from "node:test";
import {callCandidate} from "./test_client.mjs";

const strings = (response) => response.keys.map((key) => key.value);
const call = (scenario) => callCandidate({operation: "call", scenario});

test("package metadata is pinned", () => {
  const site = process.env.NODE_CANDIDATE_SITE;
  const manifest = JSON.parse(readFileSync(join(site, "node_modules/own-keys/package.json"), "utf8"));
  assert.equal(manifest.name, "own-keys");
  assert.equal(manifest.version, "1.0.2");
  assert.equal(manifest.main, "index.js");
  assert.equal(manifest.type, undefined);
  assert.deepEqual(manifest.exports, {".": "./index.js", "./package.json": "./package.json"});
  assert.deepEqual(manifest.dependencies, {
    "call-bound": "1.0.4",
    "get-intrinsic": "1.3.0",
    "object-keys": "1.1.1",
    "safe-push-apply": "1.0.0",
  });
});

test("root export is a unary function", () => {
  assert.deepEqual(callCandidate({operation: "inventory"}), {ok: true, type: "function", length: 1});
});

test("empty object has no keys", () => assert.deepEqual(strings(call("empty")), []));
test("enumerable string insertion order is preserved", () => assert.deepEqual(strings(call("enumerable-order")), ["delta", "alpha", "charlie", "bravo"]));
test("non-enumerable names are included", () => assert.deepEqual(strings(call("non-enumerable")), ["visible", "hidden"]));
test("inherited names are excluded", () => assert.deepEqual(strings(call("inherited")), ["own"]));

test("enumerable and non-enumerable symbols are included", () => {
  const result = call("symbols");
  assert.equal(result.ok, true);
  assert.deepEqual(result.keys, [
    {type: "string", value: "text"},
    {type: "symbol", id: "first", description: "first", globalKey: null},
    {type: "symbol", id: "second", description: "second", globalKey: null},
  ]);
});

test("all strings precede symbols while each group preserves order", () => {
  assert.deepEqual(call("mixed-order").keys.map((key) => key.id ?? key.value), ["zeta", "alpha", "early", "late"]);
});

test("canonical integer-index ordering precedes other strings", () => assert.deepEqual(strings(call("integer-order")), ["2", "10", "beta", "alpha"]));
test("dense arrays include indexes and length", () => assert.deepEqual(strings(call("dense-array")), ["0", "1", "2", "length"]));
test("sparse arrays include the present index, length, and custom keys", () => assert.deepEqual(strings(call("sparse-array")), ["3", "length", "extra"]));
test("null-prototype objects are supported", () => assert.deepEqual(strings(call("null-prototype")), ["alpha", "hidden"]));
test("frozen objects retain their keys", () => assert.deepEqual(strings(call("frozen")), ["alpha", "beta"]));
test("sealed objects retain their keys", () => assert.deepEqual(strings(call("sealed")), ["alpha", "beta"]));

test("enumerable accessors are not invoked", () => {
  const result = call("accessor");
  assert.deepEqual(strings(result), ["computed"]);
  assert.equal(result.state.getterCalls, 0);
});

test("throwing non-enumerable accessors are not invoked", () => {
  const result = call("throwing-accessor");
  assert.deepEqual(strings(result), ["danger"]);
  assert.equal(result.state.getterCalls, 0);
});

test("deleting and re-adding a string moves it to the end", () => assert.deepEqual(strings(call("delete-readd")), ["alpha", "gamma", "beta"]));
test("redefining a property does not move it", () => assert.deepEqual(strings(call("redefine")), ["alpha", "beta"]));

test("distinct symbols with equal descriptions remain distinct", () => {
  const result = call("duplicate-symbol-descriptions");
  assert.deepEqual(result.keys.map((key) => key.id), ["one", "two"]);
  assert.deepEqual(result.keys.map((key) => key.description), ["same", "same"]);
});

test("global symbols are returned unchanged", () => {
  assert.deepEqual(call("global-symbol").keys, [{type: "symbol", id: "global", description: "shared-key", globalKey: "shared-key"}]);
});

test("well-known symbols are returned unchanged", () => {
  const [key] = call("well-known-symbol").keys;
  assert.equal(key.type, "symbol");
  assert.equal(key.id, "iterator");
});

test("proxy ownKeys order is observed", () => assert.deepEqual(strings(call("proxy-order")), ["beta", "alpha"]));
test("proxy ownKeys trap is called once", () => assert.equal(call("proxy-order").state.trapCalls, 1));
test("duplicate proxy keys produce TypeError", () => assert.equal(call("proxy-duplicate").errorType, "TypeError"));
test("omitting a non-configurable proxy key produces TypeError", () => assert.equal(call("proxy-missing-fixed").errorType, "TypeError"));

test("null input produces TypeError", () => assert.equal(call("null").errorType, "TypeError"));
test("undefined input produces TypeError", () => assert.equal(call("undefined").errorType, "TypeError"));
test("string primitive input produces TypeError", () => assert.equal(call("string").errorType, "TypeError"));
test("number primitive input produces TypeError", () => assert.equal(call("number").errorType, "TypeError"));
test("boolean primitive input produces TypeError", () => assert.equal(call("boolean").errorType, "TypeError"));
test("symbol primitive input produces TypeError", () => assert.equal(call("symbol-primitive").errorType, "TypeError"));
test("bigint primitive input produces TypeError", () => assert.equal(call("bigint").errorType, "TypeError"));

test("result entries distinguish strings from symbols", () => {
  assert.deepEqual(call("symbols").keys.map((key) => key.type), ["string", "symbol", "symbol"]);
});

test("the source object is not mutated", () => {
  const result = call("no-mutation");
  assert.equal(result.state.before, result.state.after);
});

test("each call returns a fresh result array", () => {
  const first = call("enumerable-order");
  first.keys.pop();
  assert.deepEqual(strings(call("enumerable-order")), ["delta", "alpha", "charlie", "bravo"]);
});

test("large but bounded ordinary key sets remain deterministic", () => {
  const expected = ["delta", "alpha", "charlie", "bravo"];
  assert.deepEqual(strings(call("enumerable-order")), expected);
  assert.deepEqual(strings(call("enumerable-order")), expected);
});
