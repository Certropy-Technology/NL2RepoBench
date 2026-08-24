import assert from "node:assert/strict";
import test from "node:test";

const { callJsonc, callJsoncFailure } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/private/test_client.mjs"
);

const formatting = {
  insertSpaces: true,
  tabSize: 2,
  eol: "\n",
  keepLines: false,
};
const modifyOptions = { formattingOptions: formatting };

function errorNames(result) {
  return result.errors.map((error) => error.name);
}

test("package is a scripts-stripped zero-dependency ESM distribution", () => {
  assert.deepEqual(callJsonc("metadata", {}), {
    name: "jsonc-parser",
    version: "4.0.0-next.2",
    type: "module",
    exportImport: "./lib/esm/main.js",
    scripts: null,
    dependencies: [],
    devDependencies: [],
  });
});

test("parse accepts nested JSON with line and block comments", () => {
  const result = callJsonc("parse", {
    text: '{ // heading\n "name": "demo", "items": [1, /* gap */ true, null] }',
  });
  assert.deepEqual(result, {
    hasValue: true,
    value: { name: "demo", items: [1, true, null] },
    errors: [],
  });
});

test("parse handles root strings, escapes, and exponent numbers", () => {
  assert.deepEqual(callJsonc("parse", { text: '"\\u00DC-\\n"' }).value, "Ü-\n");
  assert.equal(callJsonc("parse", { text: "1.2E-3" }).value, 0.0012);
});

test("parse keeps the last value for duplicate object keys", () => {
  assert.deepEqual(callJsonc("parse", { text: '{ "x": 1, "x": 2 }' }), {
    hasValue: true,
    value: { x: 2 },
    errors: [],
  });
});

test("parse allows trailing commas when requested", () => {
  assert.deepEqual(callJsonc("parse", {
    text: '{ "hello": [], }',
    options: { allowTrailingComma: true },
  }), {
    hasValue: true,
    value: { hello: [] },
    errors: [],
  });
});

test("parse reports a trailing comma by default", () => {
  const result = callJsonc("parse", { text: '{ "hello": [], }' });
  assert.deepEqual(result.value, { hello: [] });
  assert.deepEqual(errorNames(result), ["PropertyNameExpected", "ValueExpected"]);
  assert.deepEqual(result.errors.map(({ offset, length }) => ({ offset, length })), [
    { offset: 15, length: 1 },
    { offset: 15, length: 1 },
  ]);
});

test("parse reports comments when disallowComments is true", () => {
  const result = callJsonc("parse", {
    text: '{ "foo": /*comment*/ true }',
    options: { disallowComments: true },
  });
  assert.deepEqual(result.value, { foo: true });
  assert.deepEqual(errorNames(result), ["InvalidCommentToken"]);
  assert.deepEqual(result.errors[0], {
    error: 10,
    offset: 9,
    length: 11,
    startLine: 0,
    startCharacter: 9,
    name: "InvalidCommentToken",
  });
});

test("parse recovers from a missing object comma", () => {
  const result = callJsonc("parse", { text: '{ "bar": 8 "xoo": "foo" }' });
  assert.deepEqual(result.value, { bar: 8, xoo: "foo" });
  assert.deepEqual(errorNames(result), ["CommaExpected"]);
  assert.equal(result.errors[0].offset, 11);
});

test("parse recovers from missing and trailing array values", () => {
  const result = callJsonc("parse", { text: "[ ,1, 2, 3, ]" });
  assert.deepEqual(result.value, [1, 2, 3]);
  assert.deepEqual(errorNames(result), ["ValueExpected", "ValueExpected"]);
  assert.deepEqual(result.errors.map((error) => error.offset), [2, 12]);
});

test("parse reports empty input and has no value", () => {
  assert.deepEqual(callJsonc("parse", { text: "" }), {
    hasValue: false,
    value: null,
    errors: [{
      error: 4,
      offset: 0,
      length: 0,
      startLine: 0,
      startCharacter: 0,
      name: "ValueExpected",
    }],
  });
});

test("parse accepts empty input when allowEmptyContent is true", () => {
  assert.deepEqual(callJsonc("parse", {
    text: "",
    options: { allowEmptyContent: true },
  }), { hasValue: false, value: null, errors: [] });
});

test("parse reports an invalid escape while returning a tolerant value", () => {
  const result = callJsonc("parse", { text: '"\\v"' });
  assert.equal(result.value, "");
  assert.deepEqual(errorNames(result), ["InvalidEscapeCharacter"]);
  assert.equal(result.errors[0].error, 15);
});

test("parse reports extra content after a root value", () => {
  const result = callJsonc("parse", { text: "1,1" });
  assert.equal(result.value, 1);
  assert.deepEqual(errorNames(result), ["EndOfFileExpected"]);
  assert.equal(result.errors[0].offset, 1);
});

test("modify replaces an existing property and returns valid edits", () => {
  assert.deepEqual(callJsonc("modify", {
    text: '{\n  "x": "y"\n}',
    path: ["x"],
    value: "bar",
    options: modifyOptions,
  }), {
    edits: [{ offset: 9, length: 3, content: '"bar"' }],
    text: '{\n  "x": "bar"\n}',
  });
});

test("modify replaces the root value", () => {
  assert.deepEqual(callJsonc("modify", {
    text: "true",
    path: [],
    value: "bar",
    options: modifyOptions,
  }), {
    edits: [{ offset: 0, length: 4, content: '"bar"' }],
    text: '"bar"',
  });
});

test("modify creates a nested object and array in an empty document", () => {
  assert.equal(callJsonc("modify", {
    text: "",
    path: ["foo", 0],
    value: "bar",
    options: modifyOptions,
  }).text, '{\n  "foo": [\n    "bar"\n  ]\n}');
});

test("modify appends a formatted object property", () => {
  assert.equal(callJsonc("modify", {
    text: '{\n  "x": "y"\n}',
    path: ["new"],
    value: { enabled: true },
    options: modifyOptions,
  }).text, '{\n  "x": "y",\n  "new": {\n    "enabled": true\n  }\n}');
});

test("modify removes the first object property", () => {
  assert.equal(callJsonc("modify", {
    text: '{\n  "x": "y", "a": []\n}',
    path: ["x"],
    delete: true,
    options: modifyOptions,
  }).text, '{\n  "a": []\n}');
});

test("modify removes the last object property", () => {
  assert.equal(callJsonc("modify", {
    text: '{\n  "x": "y", "a": []\n}',
    path: ["a"],
    delete: true,
    options: modifyOptions,
  }).text, '{\n  "x": "y"\n}');
});

test("modify replaces an array item", () => {
  assert.equal(callJsonc("modify", {
    text: '[\n  1,\n  2,\n  3\n]',
    path: [1],
    value: 5,
    options: modifyOptions,
  }).text, '[\n  1,\n  5,\n  3\n]');
});

test("modify inserts an array item when isArrayInsertion is true", () => {
  assert.equal(callJsonc("modify", {
    text: '[\n  1,\n  3\n]',
    path: [1],
    value: 2,
    options: { ...modifyOptions, isArrayInsertion: true },
  }).text, '[\n  1,\n  2,\n  3\n]');
});

test("modify appends an array item at path segment minus one", () => {
  assert.equal(callJsonc("modify", {
    text: '[\n  1,\n  2\n]',
    path: [-1],
    value: "bar",
    options: modifyOptions,
  }).text, '[\n  1,\n  2,\n  "bar"\n]');
});

test("modify removes an array item in the middle", () => {
  assert.equal(callJsonc("modify", {
    text: '[\n  1,\n  2,\n  3\n]',
    path: [1],
    delete: true,
    options: modifyOptions,
  }).text, '[\n  1,\n  3\n]');
});

test("modify leaves inserted JSON compact without formattingOptions", () => {
  assert.equal(callJsonc("modify", {
    text: '{"items":[1,2]}',
    path: ["items", 0],
    value: { a: 1, b: 2 },
    options: {},
  }).text, '{"items":[{"a":1,"b":2},2]}');
});

test("modify distinguishes null replacement from deletion", () => {
  assert.equal(callJsonc("modify", {
    text: '{ "x": 1 }',
    path: ["x"],
    value: null,
    options: modifyOptions,
  }).text, '{ "x": null }');
});

test("modify rejects traversal through a scalar parent", () => {
  const failure = callJsoncFailure("modify", {
    text: '{"x":1}',
    path: ["x", "y"],
    value: 2,
    options: {},
  });
  assert.equal(failure.exception_type, "Error");
  assert.equal(failure.message, "Can not add index to parent of type number");
});

test("format expands an object with two-space indentation", () => {
  assert.equal(callJsonc("format", {
    text: '{"x" : 1,  "y" : "foo"}',
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '{\n  "x": 1,\n  "y": "foo"\n}');
});

test("format expands nested arrays and objects", () => {
  assert.equal(callJsonc("format", {
    text: '[ [], [ [ {} ], "a" ] ]',
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '[\n  [],\n  [\n    [\n      {}\n    ],\n    "a"\n  ]\n]');
});

test("format preserves and indents line comments", () => {
  assert.equal(callJsonc("format", {
    text: '[ \n//comment\n"foo", "bar"\n] ',
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '[\n  //comment\n  "foo",\n  "bar"\n]');
});

test("format keeps inline block comments with one separating space", () => {
  assert.equal(callJsonc("format", {
    text: '{ "a": {}, /*comment*/ "b": {} }',
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '{\n  "a": {}, /*comment*/\n  "b": {}\n}');
});

test("format can indent with tabs", () => {
  assert.equal(callJsonc("format", {
    text: '{"a":true,"b":[1,2]}',
    options: { tabSize: 2, insertSpaces: false, eol: "\n" },
  }).text, '{\n\t"a": true,\n\t"b": [\n\t\t1,\n\t\t2\n\t]\n}');
});

test("format can insert a final newline", () => {
  assert.equal(callJsonc("format", {
    text: "{\n}",
    options: { tabSize: 2, insertSpaces: true, eol: "\n", insertFinalNewline: true },
  }).text, "{}\n");
});

test("format keepLines preserves an existing one-line array", () => {
  assert.equal(callJsonc("format", {
    text: '{ "array": [1,2,3]\n}',
    options: { tabSize: 2, insertSpaces: true, eol: "\n", keepLines: true },
  }).text, '{ "array": [ 1, 2, 3 ]\n}');
});

test("format limits changes to a requested range", () => {
  assert.equal(callJsonc("format", {
    text: '{ "a": {},\n"b": [null, null]\n} ',
    range: { offset: 11, length: 17 },
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '{ "a": {},\n"b": [\n  null,\n  null\n]\n} ');
});

test("format preserves malformed token order while adjusting safe whitespace", () => {
  assert.equal(callJsonc("format", {
    text: '[ null  1.2 "Hello" ]',
    options: { tabSize: 2, insertSpaces: true, eol: "\n" },
  }).text, '[\n  null  1.2 "Hello"\n]');
});

test("applyEdits sorts non-overlapping edits by offset", () => {
  assert.deepEqual(callJsonc("applyEdits", {
    text: "abcdef",
    edits: [
      { offset: 4, length: 2, content: "Y" },
      { offset: 1, length: 2, content: "X" },
    ],
  }), { text: "aXdY" });
});

test("applyEdits rejects overlapping ranges", () => {
  const failure = callJsoncFailure("applyEdits", {
    text: "abcdef",
    edits: [
      { offset: 1, length: 3, content: "X" },
      { offset: 2, length: 2, content: "Y" },
    ],
  });
  assert.equal(failure.exception_type, "Error");
  assert.equal(failure.message, "Overlapping edit");
});
