import assert from "node:assert/strict";
import { test } from "node:test";
import { call, packageJson, packageLock, value } from "./test_client.mjs";

test("package-name-version", () => {
  const manifest = packageJson();
  assert.equal(manifest.name, "js-yaml");
  assert.equal(manifest.version, "5.4.0");
});

test("esm-root-entry", () => {
  const manifest = packageJson();
  assert.equal(manifest.type, "module");
  assert.equal(manifest.exports["."]["import"], "./index.mjs");
});

test("lockfile-contract", () => {
  const manifest = packageJson();
  const lock = packageLock();
  assert.equal(manifest.dependencies, undefined);
  assert.equal(manifest.exports["./package.json"], "./package.json");
  assert.equal(lock.lockfileVersion, 3);
  assert.equal(typeof lock.packages[""], "object");
  assert.equal(lock.packages["node_modules/js-yaml"].version, "5.4.0");
});

test("load-basic-scalars", () => {
  assert.deepEqual(value("load", "name: John\nage: 30\nactive: true\nnone: null\n"), {
    name: "John", age: 30, active: true, none: null,
  });
});

test("load-quoted-scalars", () => {
  assert.deepEqual(value("load", "single: 'it''s'\ndouble: \"line\\nnext\"\nyes: yes\n"), {
    single: "it's", double: "line\nnext", yes: "yes",
  });
});

test("load-flow-collections", () => {
  assert.deepEqual(value("load", "obj: {a: 1, b: [true, null, \"x\"]}\n"), {
    obj: { a: 1, b: [true, null, "x"] },
  });
});

test("load-nested-blocks", () => {
  assert.deepEqual(value("load", "service:\n  name: api\n  ports:\n    - 8080\n    - 8081\n"), {
    service: { name: "api", ports: [8080, 8081] },
  });
});

test("load-comments-and-multiline", () => {
  assert.deepEqual(value("load", "# heading\nmessage: hello # inline\ntext: >\n  first\n  second\n"), {
    message: "hello", text: "first second\n",
  });
});

test("load-block-scalars", () => {
  assert.deepEqual(value("load", "literal: |\n  hello\n  world\nfolded: >\n  hello\n  world\n"), {
    literal: "hello\nworld\n", folded: "hello world\n",
  });
});

test("load-alias", () => {
  assert.deepEqual(value("load", "base: &x\n  value: 7\ncopy: *x\n"), {
    base: { value: 7 }, copy: { value: 7 },
  });
});

test("load-explicit-core-tags", () => {
  assert.deepEqual({
    string: value("load", "!!str 42"),
    integer: value("load", "!!int \"42\""),
    boolean: value("load", "!!bool \"true\""),
  }, { string: "42", integer: 42, boolean: true });
});

test("load-prototype-key", () => {
  const result = value("load", "__proto__: bad\nconstructor: ok\n");
  assert.equal(result["__proto__"], "bad");
  assert.equal(result.constructor, "ok");
  assert.equal({}.bad, undefined);
});

test("load-document-marker", () => {
  assert.deepEqual(value("load", "---\na: 1\n...\n"), { a: 1 });
});

test("loadall-empty", () => {
  assert.deepEqual(value("loadAll", ""), []);
});

test("loadall-multiple", () => {
  assert.deepEqual(value("loadAll", "---\na: 1\n---\nb: 2\n"), [{ a: 1 }, { b: 2 }]);
});

test("loadall-markers", () => {
  assert.deepEqual(value("loadAll", "---\nname: api\n...\n---\nname: worker\n...\n"), [
    { name: "api" }, { name: "worker" },
  ]);
});

test("loadall-options", () => {
  assert.deepEqual(value("loadAll", "a: 1\na: 2\n", { json: true }), [{ a: 2 }]);
});

test("load-empty-error", () => {
  const response = call("load", "");
  assert.equal(response.ok, false);
  assert.equal(response.exception_type, "YAMLException");
});

test("load-multi-error", () => {
  const response = call("load", "---\na: 1\n---\nb: 2\n");
  assert.equal(response.ok, false);
  assert.equal(response.exception_type, "YAMLException");
  assert.match(response.message, /single document/);
});

test("load-malformed-error", () => {
  const response = call("load", "a: [1,", { filename: "config.yml" });
  assert.equal(response.ok, false);
  assert.equal(response.exception_type, "YAMLException");
  assert.match(response.message, /config\.yml/);
  assert.match(response.message, /1:7/);
});

test("load-duplicate-error", () => {
  const response = call("load", "a: 1\na: 2\n");
  assert.equal(response.ok, false);
  assert.equal(response.exception_type, "YAMLException");
  assert.match(response.message, /duplicated mapping key/);
});

test("load-unknown-tag-error", () => {
  const response = call("load", "!!js/function test");
  assert.equal(response.ok, false);
  assert.equal(response.exception_type, "YAMLException");
  assert.match(response.message, /unknown scalar tag/);
});

test("dump-scalars", () => {
  assert.equal(value("dump", null), "null\n");
  assert.equal(value("dump", true), "true\n");
  assert.equal(value("dump", 42), "42\n");
});

test("dump-nested", () => {
  assert.equal(value("dump", { service: { name: "api" } }), "service:\n  name: api\n");
});

test("dump-array", () => {
  assert.equal(value("dump", { items: ["one", "two"] }), "items:\n  - one\n  - two\n");
});

test("dump-strings", () => {
  assert.equal(value("dump", { plain: "hello", needsQuotes: "a: b" }), "plain: hello\nneedsQuotes: 'a: b'\n");
});

test("dump-key-order", () => {
  assert.equal(value("dump", { z: 1, a: 2 }), "z: 1\na: 2\n");
});

test("dump-repeatable", () => {
  const input = { nested: { values: [1, true, null, "x"] } };
  assert.equal(value("dump", input), value("dump", input));
});

test("dump-sort", () => {
  assert.equal(value("dump", { z: 1, a: 2 }, { sortKeys: true }), "a: 2\nz: 1\n");
});

test("dump-flow", () => {
  assert.equal(value("dump", { a: [1, 2], b: { c: "x" } }, { flowLevel: 0 }), "{a: [1, 2], b: {c: x}}\n");
});

test("dump-indent", () => {
  assert.equal(value("dump", { a: { b: { c: 1 } }, list: [1, 2] }, { indent: 4 }), "a:\n    b:\n        c: 1\nlist:\n    - 1\n    - 2\n");
});

test("dump-no-array-indent", () => {
  assert.equal(value("dump", { a: [1, 2], b: "x" }, { seqNoIndent: true }), "a:\n- 1\n- 2\nb: x\n");
});

test("dump-flow-padding", () => {
  assert.equal(value("dump", { a: [1, 2], b: { c: 3 } }, { flowLevel: 0, flowBracketPadding: true }), "{ a: [ 1, 2 ], b: { c: 3 } }\n");
});

test("dump-quote-options", () => {
  assert.equal(value("dump", { a: "hello world", b: "yes" }, { forceQuotes: true, quoteStyle: "double" }), "a: \"hello world\"\nb: \"yes\"\n");
});

test("dump-line-width", () => {
  assert.equal(value("dump", { text: "This is a long line that should wrap across multiple lines when a small width is selected." }, { lineWidth: 30 }), "text: >-\n  This is a long line that\n  should wrap across multiple\n  lines when a small width is\n  selected.\n");
});

test("dump-deterministic", () => {
  const input = { z: [1, 2], a: { enabled: true, text: "stable" } };
  const first = value("dump", input, { flowLevel: 1, sortKeys: true });
  const second = value("dump", input, { flowLevel: 1, sortKeys: true });
  assert.equal(first, second);
});
