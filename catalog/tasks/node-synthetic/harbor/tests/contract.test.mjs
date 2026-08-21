import assert from "node:assert/strict";
import test from "node:test";
const { callCandidate } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/runtime/node/test_client.mjs"
);

test("normalize accepts objects", () => {
  assert.deepEqual(callCandidate("normalize", [JSON.stringify({ b: 1, a: 2 })]), { a: 2, b: 1 });
});
test("normalize preserves arrays", () => {
  assert.deepEqual(callCandidate("normalize", [JSON.stringify([{ b: 1, a: 2 }])]), [{ a: 2, b: 1 }]);
});
test("normalize rejects invalid JSON", () => {
  assert.throws(() => callCandidate("normalize", ["{"]), /candidate-call-failed/);
});
test("stable stringify is compact", () => {
  assert.equal(callCandidate("stableStringify", [{ b: 1, a: 2 }]), '{"a":2,"b":1}');
});
test("stable stringify recurses", () => {
  assert.equal(callCandidate("stableStringify", [{ z: { b: 1, a: 2 } }]), '{"z":{"a":2,"b":1}}');
});
test("summarize counts values", () => {
  assert.deepEqual(callCandidate("summarize", [[1, 2, 3]]), { count: 3, first: 1, last: 3 });
});
test("summarize returns boundaries", () => {
  assert.deepEqual(callCandidate("summarize", [[1, 2, 3]]), { count: 3, first: 1, last: 3 });
});
test("empty summarize boundaries are null", () => {
  assert.deepEqual(callCandidate("summarize", [[]]), { count: 0, first: null, last: null });
});
