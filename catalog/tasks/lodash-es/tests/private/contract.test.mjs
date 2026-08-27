import test from "node:test";
import assert from "node:assert/strict";
import { call, callWithArgs } from "./test_client.mjs";

test("chunk-default-and-sized", async () => {
  assert.deepEqual(await call("chunk", [1, 2, 3]), [[1], [2], [3]]);
  assert.deepEqual(await call("chunk", [1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepEqual(await call("chunk", [1, 2, 3], 0), []);
});
test("compact-falsey-values", async () => assert.deepEqual(await call("compact", [0, 1, false, 2, "", 3, null]), [1, 2, 3]));
test("concat-flattens-one-level", async () => assert.deepEqual(await call("concat", [1], 2, [3, 4], [[5]]), [1, 2, 3, 4, [5]]));
test("difference-preserves-order", async () => assert.deepEqual(await call("difference", [2, 1, 2, 3], [2, 4]), [1, 3]));
test("drop-left", async () => {
  assert.deepEqual(await call("drop", [1, 2, 3]), [2, 3]);
  assert.deepEqual(await call("drop", [1, 2, 3], 2), [3]);
});
test("drop-right", async () => {
  assert.deepEqual(await call("dropRight", [1, 2, 3]), [1, 2]);
  assert.deepEqual(await call("dropRight", [1, 2, 3], 2), [1]);
});
test("flatten-one-level", async () => assert.deepEqual(await call("flatten", [1, [2, [3]], 4]), [1, 2, [3], 4]));
test("flatten-deep", async () => assert.deepEqual(await call("flattenDeep", [1, [2, [3, [4]]]]), [1, 2, 3, 4]));
test("head-and-last", async () => {
  assert.equal(await call("head", ["a", "b"]), "a");
  assert.equal(await call("last", ["a", "b"]), "b");
});
test("map-property-shorthand", async () => {
  assert.deepEqual(await call("map", [{ name: "Ada" }, { name: "Lin" }], "name"), ["Ada", "Lin"]);
  assert.deepEqual(await call("map", [{ active: true }, { active: false }], ["active", true]), [true, false]);
});
test("filter-object-match", async () => assert.deepEqual(await call("filter", [{ active: true, id: 1 }, { active: false, id: 2 }], { active: true }), [{ active: true, id: 1 }]));
test("find-object-match", async () => {
  assert.deepEqual(await call("find", [{ id: 1 }, { id: 2, active: true }], { active: true }), { id: 2, active: true });
  assert.equal(await call("find", [{ id: 1 }], { active: true }), undefined);
});
test("group-by-length", async () => assert.deepEqual(await call("groupBy", ["one", "two", "three"], "length"), { "3": ["one", "two"], "5": ["three"] }));
test("key-by-id", async () => assert.deepEqual(await call("keyBy", [{ id: "a", v: 1 }, { id: "b", v: 2 }], "id"), { a: { id: "a", v: 1 }, b: { id: "b", v: 2 } }));
test("get-dotted-path", async () => {
  assert.equal(await call("get", { a: { b: { c: 7 } } }, "a.b.c", 0), 7);
  assert.equal(await call("get", { a: {} }, "a.b.c", 9), 9);
});
test("has-array-path", async () => {
  assert.equal(await call("has", { a: [{ b: 1 }] }, ["a", 0, "b"]), true);
  assert.equal(await call("has", { a: [{}] }, ["a", 0, "b"]), false);
});
test("is-equal-order-independent", async () => assert.equal(await call("isEqual", { a: 1, b: [2, 3] }, { b: [2, 3], a: 1 }), true));
test("clone-deep-isolated-json", async () => assert.deepEqual(await call("cloneDeep", { a: [{ b: 1 }] }), { a: [{ b: 1 }] }));
test("sum-by-property", async () => assert.equal(await call("sumBy", [{ n: 2 }, { n: 5 }], "n"), 7));
test("max-by-property", async () => {
  assert.deepEqual(await call("maxBy", [{ n: 2, id: "a" }, { n: 5, id: "b" }], "n"), { n: 5, id: "b" });
  assert.equal(await call("maxBy", [], "n"), undefined);
});
test("order-by-descending", async () => assert.deepEqual(await call("orderBy", [{ n: 1 }, { n: 3 }, { n: 2 }], ["n"], ["desc"]), [{ n: 3 }, { n: 2 }, { n: 1 }]));
test("uniq-primitives", async () => assert.deepEqual(await call("uniq", [2, 1, 2, 3, 1]), [2, 1, 3]));
test("zip-arrays", async () => assert.deepEqual(await call("zip", ["a", "b"], [1], [true, false, true]), [["a", 1, true], ["b", null, false], [null, null, true]]));
test("camel-case", async () => assert.equal(await call("camelCase", "Foo Bar"), "fooBar"));
test("kebab-case", async () => assert.equal(await call("kebabCase", "Foo Bar"), "foo-bar"));
test("start-case", async () => assert.equal(await call("startCase", "fooBar"), "Foo Bar"));
test("root-export-aliases-and-conversions", async () => {
  assert.deepEqual(await call("default.chunk", [1, 2], 1), [[1], [2]]);
  assert.equal(await call("toString", 42), "42");
  assert.equal(await call("toNumber", "3.5"), 3.5);
});
test("empty-collection-boundaries", async () => {
  assert.deepEqual(await call("chunk", [], 2), []);
  assert.deepEqual(await call("flattenDeep", []), []);
});
test("unicode-word-boundaries", async () => assert.equal(await call("kebabCase", "Déjà Vu"), "deja-vu"));
test("repeatable-pure-results", async () => {
  const input = [{ score: 4 }, { score: 1 }, { score: 4 }];
  const response = await callWithArgs("orderBy", input, ["score"], ["asc"]);
  assert.deepEqual(response.value, [{ score: 1 }, { score: 4 }, { score: 4 }]);
  assert.deepEqual(response.args, [input, ["score"], ["asc"]]);
  assert.deepEqual(await call("orderBy", input, ["score"], ["asc"]), response.value);
  const cloneResponse = await callWithArgs("cloneDeep", { a: [{ b: 1 }] });
  assert.deepEqual(cloneResponse.args, [{ a: [{ b: 1 }] }]);
});
