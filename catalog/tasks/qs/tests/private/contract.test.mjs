import assert from "node:assert/strict";
import test from "node:test";

const { callCandidate } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/runtime/node/test_client.mjs"
);

test("parse decodes simple pairs and plus spaces", () => {
  assert.deepEqual(callCandidate("parse", ["foo=bar+baz&n=15"]), { foo: "bar baz", n: "15" });
});

test("parse combines repeated keys in order", () => {
  assert.deepEqual(callCandidate("parse", ["foo=bar&foo=baz"]), { foo: ["bar", "baz"] });
});

test("parse handles nested brackets and arrays", () => {
  assert.deepEqual(callCandidate("parse", ["a[b][0]=x&a[b][1]=y"]), { a: { b: ["x", "y"] } });
});

test("parse applies the array limit", () => {
  assert.deepEqual(callCandidate("parse", ["a[1]=x", { arrayLimit: 1 }]), { a: { "1": "x" } });
});

test("parse honors strict null handling", () => {
  assert.deepEqual(callCandidate("parse", ["flag", { strictNullHandling: true }]), { flag: null });
});

test("parse supports comma arrays", () => {
  assert.deepEqual(callCandidate("parse", ["a=b,c", { comma: true }]), { a: ["b", "c"] });
});

test("parse supports dot notation", () => {
  assert.deepEqual(callCandidate("parse", ["a.b=c", { allowDots: true }]), { a: { b: "c" } });
});

test("parse can ignore a query prefix", () => {
  assert.deepEqual(callCandidate("parse", ["?a=b", { ignoreQueryPrefix: true }]), { a: "b" });
});

test("parse retains malformed percent escapes", () => {
  assert.deepEqual(callCandidate("parse", ["a=%ZZ"]), { a: "%ZZ" });
});

test("parse enforces prototype protection", () => {
  assert.deepEqual(callCandidate("parse", ["toString=foo&a=b"]), { a: "b" });
});

test("parse permits prototype keys without global mutation", () => {
  assert.deepEqual(callCandidate("parse", ["toString=foo", { allowPrototypes: true }]), { toString: "foo" });
});

test("stringify encodes nested arrays with RFC3986 defaults", () => {
  assert.equal(callCandidate("stringify", [{ a: { b: ["x", "y"] } }]), "a%5Bb%5D%5B0%5D=x&a%5Bb%5D%5B1%5D=y");
});

test("stringify preserves own-key order", () => {
  assert.equal(callCandidate("stringify", [{ b: 2, a: 1 }]), "b=2&a=1");
});

test("stringify supports bracket arrays", () => {
  assert.equal(callCandidate("stringify", [{ a: ["x", "y"] }, { arrayFormat: "brackets" }]), "a%5B%5D=x&a%5B%5D=y");
});

test("stringify supports repeated arrays", () => {
  assert.equal(callCandidate("stringify", [{ a: ["x", "y"] }, { arrayFormat: "repeat" }]), "a=x&a=y");
});

test("stringify supports comma arrays", () => {
  assert.equal(callCandidate("stringify", [{ a: ["x", "y"] }, { arrayFormat: "comma" }]), "a=x%2Cy");
});

test("stringify supports RFC1738 spaces", () => {
  assert.equal(callCandidate("stringify", [{ a: "hello world" }, { format: "RFC1738" }]), "a=hello+world");
});
