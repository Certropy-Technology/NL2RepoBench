import assert from "node:assert/strict";
import test from "node:test";

const { call, metadata } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/private/test_client.mjs"
);

test("package metadata is scripts-free CommonJS lodash 4.18.1", () => {
  assert.deepEqual(metadata(), {
    name: "lodash",
    version: "4.18.1",
    main: "lodash.js",
    type: null,
    scripts: null,
    dependencies: [],
    devDependencies: [],
    versionConstant: "4.18.1",
  });
});

test("chunk divides an array and preserves a final remainder", () => {
  assert.deepEqual(call("chunk", [1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
});

test("compact removes all falsey JSON values", () => {
  assert.deepEqual(call("compact", [0, 1, false, 2, "", 3, null]), [1, 2, 3]);
});

test("difference removes values using SameValueZero membership", () => {
  assert.deepEqual(call("difference", [2, 1, 2, 3, null], [2, 4, null]), [1, 3]);
});

test("drop removes a count from the start", () => {
  assert.deepEqual(call("drop", [1, 2, 3, 4], 2), [3, 4]);
  assert.deepEqual(call("drop", [1, 2, 3]), [2, 3]);
});

test("dropRight removes a count from the end", () => {
  assert.deepEqual(call("dropRight", [1, 2, 3, 4], 2), [1, 2]);
});

test("flatten removes exactly one array nesting level", () => {
  assert.deepEqual(call("flatten", [1, [2, [3]], 4]), [1, 2, [3], 4]);
});

test("flattenDeep recursively removes all array nesting", () => {
  assert.deepEqual(call("flattenDeep", [1, [2, [3, [4]]]]), [1, 2, 3, 4]);
});

test("head and last select array endpoints", () => {
  assert.equal(call("head", [10, 20, 30]), 10);
  assert.equal(call("last", [10, 20, 30]), 30);
});

test("nth supports negative offsets from the end", () => {
  assert.equal(call("nth", [10, 20, 30, 40], -2), 30);
});

test("take and takeRight select bounded endpoint slices", () => {
  assert.deepEqual(call("take", [1, 2, 3, 4], 3), [1, 2, 3]);
  assert.deepEqual(call("takeRight", [1, 2, 3, 4], 2), [3, 4]);
});

test("uniq keeps the first occurrence in input order", () => {
  assert.deepEqual(call("uniq", [2, 1, 2, null, null, "1", 1]), [2, 1, null, "1"]);
});

test("zip groups values at matching indexes", () => {
  assert.deepEqual(call("zip", ["a", "b"], [1, 2], [true, false]), [
    ["a", 1, true], ["b", 2, false],
  ]);
});

test("concat appends scalars and flattens array arguments once", () => {
  assert.deepEqual(call("concat", [1], 2, [3, [4]]), [1, 2, 3, [4]]);
});

test("initial returns all but the final element", () => {
  assert.deepEqual(call("initial", [1, 2, 3]), [1, 2]);
});

test("get resolves dot and bracket property paths", () => {
  assert.equal(call("get", { a: [{ b: { c: 7 } }] }, "a[0].b.c"), 7);
});

test("get returns the provided default for a missing path", () => {
  assert.equal(call("get", { a: 1 }, ["missing", "value"], "fallback"), "fallback");
});

test("has checks an own nested property path", () => {
  assert.equal(call("has", { a: { b: null } }, "a.b"), true);
  assert.equal(call("has", { a: {} }, "a.b"), false);
});

test("at selects multiple property paths in request order", () => {
  assert.deepEqual(call("at", { a: { b: 1 }, c: [2, 3] }, ["c[1]", "a.b"]), [3, 1]);
});

test("assign applies source properties from left to right", () => {
  assert.deepEqual(call("assign", { a: 1 }, { b: 2 }, { a: 3 }), { a: 3, b: 2 });
});

test("defaults fills only undefined or absent destination properties", () => {
  assert.deepEqual(call("defaults", { a: 1 }, { a: 3, b: 2 }), { a: 1, b: 2 });
});

test("merge recursively combines plain object properties", () => {
  assert.deepEqual(
    call("merge", { a: { x: 1 }, list: [1] }, { a: { y: 2 }, list: [2, 3] }),
    { a: { x: 1, y: 2 }, list: [2, 3] },
  );
});

test("pick creates a result containing selected deep paths", () => {
  assert.deepEqual(call("pick", { a: { b: 1, c: 2 }, d: 3 }, ["a.b", "d"]), {
    a: { b: 1 }, d: 3,
  });
});

test("omit creates a result without selected deep paths", () => {
  assert.deepEqual(call("omit", { a: { b: 1, c: 2 }, d: 3 }, ["a.b", "d"]), {
    a: { c: 2 },
  });
});

test("keys preserves own enumerable key order", () => {
  assert.deepEqual(call("keys", { beta: 2, alpha: 1 }), ["beta", "alpha"]);
});

test("values follows own enumerable key order", () => {
  assert.deepEqual(call("values", { beta: 2, alpha: 1 }), [2, 1]);
});

test("toPairs returns own key value pairs", () => {
  assert.deepEqual(call("toPairs", { a: 1, b: 2 }), [["a", 1], ["b", 2]]);
});

test("invert swaps string keys and values", () => {
  assert.deepEqual(call("invert", { a: "x", b: "y" }), { x: "a", y: "b" });
});

test("map supports property-name iteratee shorthand", () => {
  assert.deepEqual(call("map", [{ user: "fred" }, { user: "barney" }], "user"), ["fred", "barney"]);
});

test("filter supports partial-object match shorthand", () => {
  const users = [{ user: "barney", active: true }, { user: "fred", active: false }, { user: "pebbles", active: true }];
  assert.deepEqual(call("filter", users, { active: true }), [users[0], users[2]]);
});

test("find returns the first partial-object shorthand match", () => {
  const users = [{ user: "barney", age: 36 }, { user: "fred", age: 40 }];
  assert.deepEqual(call("find", users, { age: 40 }), users[1]);
});

test("groupBy supports property-name iteratee shorthand", () => {
  assert.deepEqual(call("groupBy", ["one", "two", "three"], "length"), {
    "3": ["one", "two"], "5": ["three"],
  });
});

test("keyBy indexes values using property-name shorthand", () => {
  const values = [{ dir: "left", code: 97 }, { dir: "right", code: 100 }];
  assert.deepEqual(call("keyBy", values, "dir"), { left: values[0], right: values[1] });
});

test("orderBy applies named paths and explicit directions", () => {
  const users = [
    { user: "fred", age: 48 }, { user: "barney", age: 34 },
    { user: "fred", age: 40 }, { user: "barney", age: 36 },
  ];
  assert.deepEqual(call("orderBy", users, ["user", "age"], ["asc", "desc"]), [
    users[3], users[1], users[0], users[2],
  ]);
});

test("sortBy performs stable ascending multi-key ordering", () => {
  const users = [
    { user: "fred", age: 48 }, { user: "barney", age: 34 },
    { user: "fred", age: 40 }, { user: "barney", age: 36 },
  ];
  assert.deepEqual(call("sortBy", users, ["user", "age"]), [users[1], users[3], users[2], users[0]]);
});

test("includes finds an array value from a starting index", () => {
  assert.equal(call("includes", [1, 2, 3, 2], 2, 2), true);
  assert.equal(call("includes", [1, 2, 3], 1, 1), false);
});

test("includes performs substring search for strings", () => {
  assert.equal(call("includes", "pebbles", "ebb"), true);
});

test("size counts arrays strings and own object keys", () => {
  assert.equal(call("size", [1, 2, 3]), 3);
  assert.equal(call("size", "pebbles"), 7);
  assert.equal(call("size", { a: 1, b: 2 }), 2);
});

test("camelCase normalizes words to lower camel case", () => {
  assert.equal(call("camelCase", "Foo Bar--BAZ"), "fooBarBaz");
});

test("kebabCase and snakeCase normalize word separators", () => {
  assert.equal(call("kebabCase", "__Foo Bar__"), "foo-bar");
  assert.equal(call("snakeCase", "Foo BAR"), "foo_bar");
});

test("startCase emits title-cased space-separated words", () => {
  assert.equal(call("startCase", "__foo_bar__"), "Foo Bar");
});

test("capitalize upperFirst and lowerFirst apply documented casing", () => {
  assert.equal(call("capitalize", "FRED"), "Fred");
  assert.equal(call("upperFirst", "fred"), "Fred");
  assert.equal(call("lowerFirst", "FRED"), "fRED");
});

test("pad centers text to the requested length", () => {
  assert.equal(call("pad", "abc", 8, "_-"), "_-abc_-_");
});

test("padStart and padEnd repeat and truncate fill strings", () => {
  assert.equal(call("padStart", "abc", 7, "01"), "0101abc");
  assert.equal(call("padEnd", "abc", 7, "01"), "abc0101");
});

test("repeat duplicates a string a fixed number of times", () => {
  assert.equal(call("repeat", "ab", 3), "ababab");
});

test("escape replaces HTML-sensitive characters", () => {
  assert.equal(call("escape", '<div class="x">Tom & Jerry</div>'), "&lt;div class=&quot;x&quot;&gt;Tom &amp; Jerry&lt;/div&gt;");
});

test("unescape reverses the supported HTML entities", () => {
  assert.equal(call("unescape", "fred, barney, &amp; pebbles"), "fred, barney, & pebbles");
});

test("truncate respects length and a string separator", () => {
  assert.equal(
    call("truncate", "hi-diddly-ho there, neighborino", { length: 24, separator: " " }),
    "hi-diddly-ho there,...",
  );
});

test("truncate supports a custom omission string", () => {
  assert.equal(
    call("truncate", "hi-diddly-ho there, neighborino", { length: 24, omission: " [...]" }),
    "hi-diddly-ho there [...]",
  );
});

test("clamp limits numbers to inclusive bounds", () => {
  assert.equal(call("clamp", -10, -5, 5), -5);
  assert.equal(call("clamp", 10, -5, 5), 5);
});

test("inRange uses an inclusive start and exclusive end", () => {
  assert.equal(call("inRange", 3, 2, 4), true);
  assert.equal(call("inRange", 4, 2, 4), false);
  assert.equal(call("inRange", 3, 4, 2), true);
});

test("add sums two finite numbers", () => {
  assert.equal(call("add", 6, 4), 10);
});

test("ceil rounds upward at decimal precision", () => {
  assert.equal(call("ceil", 4.006, 2), 4.01);
});

test("floor rounds downward at decimal precision", () => {
  assert.equal(call("floor", 0.046, 2), 0.04);
});

test("round rounds to nearest at decimal precision", () => {
  assert.equal(call("round", 4.006, 2), 4.01);
});

test("max and min select finite numeric extrema", () => {
  assert.equal(call("max", [4, 2, 8, 6]), 8);
  assert.equal(call("min", [4, 2, 8, 6]), 2);
});

test("sum and mean aggregate finite numbers", () => {
  assert.equal(call("sum", [4, 2, 8, 6]), 20);
  assert.equal(call("mean", [4, 2, 8, 6]), 5);
});

test("maxBy and minBy support property-name shorthand", () => {
  const values = [{ n: 1 }, { n: 3 }, { n: 2 }];
  assert.deepEqual(call("maxBy", values, "n"), values[1]);
  assert.deepEqual(call("minBy", values, "n"), values[0]);
});

test("sumBy and meanBy support property-name shorthand", () => {
  const values = [{ n: 4 }, { n: 2 }, { n: 8 }, { n: 6 }];
  assert.equal(call("sumBy", values, "n"), 20);
  assert.equal(call("meanBy", values, "n"), 5);
});

test("isEqual recursively compares JSON arrays and objects", () => {
  assert.equal(call("isEqual", { a: [1, { b: 2 }] }, { a: [1, { b: 2 }] }), true);
  assert.equal(call("isEqual", { a: 1 }, { a: 2 }), false);
});

test("isEmpty recognizes empty JSON collections and non-empty values", () => {
  assert.equal(call("isEmpty", []), true);
  assert.equal(call("isEmpty", {}), true);
  assert.equal(call("isEmpty", [1]), false);
});

test("isPlainObject accepts JSON objects but rejects arrays and null", () => {
  assert.equal(call("isPlainObject", { a: 1 }), true);
  assert.equal(call("isPlainObject", [1]), false);
  assert.equal(call("isPlainObject", null), false);
});

test("JSON type predicates distinguish arrays numbers and strings", () => {
  assert.equal(call("isArray", []), true);
  assert.equal(call("isArray", {}), false);
  assert.equal(call("isNumber", 3), true);
  assert.equal(call("isNumber", "3"), false);
  assert.equal(call("isString", "3"), true);
  assert.equal(call("isString", 3), false);
});
