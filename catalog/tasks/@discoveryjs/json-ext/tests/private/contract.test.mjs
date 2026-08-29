import assert from "node:assert/strict";
import test from "node:test";

const { callJsonExt, callJsonExtFailure } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/private/test_client.mjs"
);

test("package is a scripts-stripped zero-dependency ESM distribution", () => {
  assert.deepEqual(callJsonExt("metadata"), {
    name: "@discoveryjs/json-ext",
    version: "1.1.0",
    type: "module",
    importEntry: "./src/index.js",
    declarationEntry: "./index.d.ts",
    scripts: null,
    dependencies: [],
    devDependencies: [],
    exportNames: [
      "createStringifyWebStream",
      "parseChunked",
      "parseFromWebStream",
      "stringifyChunked",
      "stringifyInfo",
    ],
  });
});

test("parseChunked parses a primitive root", () => {
  assert.deepEqual(callJsonExt("parse", { chunks: ["123"] }), {
    hasValue: true, value: 123, roots: [], progress: [],
  });
});

test("parseChunked reconstructs nested JSON across token boundaries", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["{\"name", "\":\"demo\",\"items\":[1,", "true,null]}"],
  }).value, { name: "demo", items: [1, true, null] });
});

test("parseChunked accepts a synchronous generator", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["[", "1", ",", "2", ",", "3", "]"],
    emitter: "sync-generator",
  }).value, [1, 2, 3]);
});

test("parseChunked accepts an asynchronous generator", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["{\"a\":", "1}"], emitter: "async-generator",
  }).value, { a: 1 });
});

test("parseChunked accepts a function returning an iterable", () => {
  assert.equal(callJsonExt("parse", {
    chunks: ["\"hel", "lo\""], emitter: "factory",
  }).value, "hello");
});

test("parseChunked joins UTF-8 sequences split across byte chunks", () => {
  const result = callJsonExt("parse", {
    chunks: [
      { bytes: [34, 240, 159] },
      { bytes: [164, 147, 230, 188] },
      { bytes: [162, 229, 173, 151, 34] },
    ],
  });
  assert.equal(result.value, "🤓漢字");
});

test("parseChunked supports mixed string and byte chunks", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["{\"ok\":", { bytes: [116, 114, 117, 101] }, "}"],
  }).value, { ok: true });
});

test("parseChunked jsonl mode returns all roots", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["{\"id\":1}\n", "{\"id\":2}\r\n", "3"], options: { mode: "jsonl" },
  }).value, [{ id: 1 }, { id: 2 }, 3]);
});

test("parseChunked jsonl mode accepts empty input", () => {
  assert.deepEqual(callJsonExt("parse", { chunks: [], options: { mode: "jsonl" } }).value, []);
});

test("parseChunked auto mode switches after a newline", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["1\n", "2\n", "3"], options: { mode: "auto" },
  }).value, [1, 2, 3]);
});

test("parseChunked auto mode preserves a single root value", () => {
  assert.deepEqual(callJsonExt("parse", {
    chunks: ["{\"only\":true}"], options: { mode: "auto" },
  }).value, { only: true });
});

test("parseChunked json mode rejects a second root", () => {
  const result = callJsonExtFailure("parse", { chunks: ["1\n2"] });
  assert.equal(result.exceptionType, "SyntaxError");
});

test("parseChunked rejects an invalid mode", () => {
  const result = callJsonExtFailure("parse", {
    chunks: ["1"], options: { mode: "invalid" },
  });
  assert.equal(result.exceptionType, "TypeError");
  assert.equal(result.message, "Invalid options: `mode` should be \"json\", \"jsonl\", or \"auto\"");
});

test("parseChunked reports malformed JSON with an adjusted position", () => {
  const result = callJsonExtFailure("parse", { chunks: ["{\"a\":1,", " nope}"] });
  assert.equal(result.exceptionType, "SyntaxError");
  assert.match(result.message, /position 8/);
});

test("parseChunked onRootValue captures roots and returns their count", () => {
  const result = callJsonExt("parse", {
    chunks: ["{\"id\":1}\n", "{\"id\":2}"],
    options: { mode: "jsonl", captureRoots: true },
  });
  assert.equal(result.value, 2);
  assert.deepEqual(result.roots.map((entry) => entry.value), [{ id: 1 }, { id: 2 }]);
  assert.deepEqual(result.roots.map((entry) => entry.state.rootValuesCount), [1, 2]);
  assert.deepEqual(result.roots.map((entry) => entry.state.mode), ["jsonl", "jsonl"]);
});

test("parseChunked onChunk reports pending and final progress", () => {
  const result = callJsonExt("parse", {
    chunks: ["{\"text\":\"hel", "lo\"}"], options: { captureChunks: true },
  });
  assert.deepEqual(result.value, { text: "hello" });
  assert.equal(result.progress.length, 3);
  assert.equal(result.progress[0].chunk, "{\"text\":\"hel");
  assert.equal(typeof result.progress[0].pending, "string");
  assert.deepEqual(result.progress.at(-1), {
    chunkParsed: 0,
    chunk: null,
    pending: null,
    state: {
      mode: "json",
      returnValue: { text: "hello" },
      currentRootValue: { text: "hello" },
      rootValuesCount: 1,
      consumed: 16,
      parsed: 16,
    },
  });
});

test("parseChunked accepts whitespace split around a root", () => {
  assert.deepEqual(callJsonExt("parse", { chunks: [" \n", " [1,2]", " \r\n"] }).value, [1, 2]);
});

test("stringifyChunked serializes JSON primitives", () => {
  for (const [value, expected] of [[null, "null"], [true, "true"], [false, "false"], [42.5, "42.5"], ["x", "\"x\""]]) {
    assert.equal(callJsonExt("stringify", { value }).text, expected);
  }
});

test("stringifyChunked serializes nested JSON in key order", () => {
  const value = { first: 1, nested: { ok: true }, items: [null, "x", 3] };
  assert.equal(callJsonExt("stringify", { value }).text, JSON.stringify(value));
});

test("stringifyChunked emits one chunk for a small default value", () => {
  assert.deepEqual(callJsonExt("stringify", { value: { a: 1, b: 2 } }).chunks, ["{\"a\":1,\"b\":2}"]);
});

test("stringifyChunked flushes deterministically at a small highWaterMark", () => {
  assert.deepEqual(callJsonExt("stringify", {
    value: [1, "hello world", 42], options: { highWaterMark: 1 },
  }).chunks, ["[1", ",\"hello world\"", ",42", "]"]);
});

test("stringifyChunked pretty prints with numeric indentation", () => {
  assert.equal(callJsonExt("stringify", {
    value: { a: 1, b: [true, false] }, options: { space: 2 },
  }).text, '{\n  "a": 1,\n  "b": [\n    true,\n    false\n  ]\n}');
});

test("stringifyChunked clamps numeric indentation to ten spaces", () => {
  assert.equal(callJsonExt("stringify", {
    value: { a: 1 }, options: { space: 20 },
  }).text, '{\n          "a": 1\n}');
});

test("stringifyChunked truncates string indentation to ten code units", () => {
  assert.equal(callJsonExt("stringify", {
    value: { a: 1 }, options: { space: "------------" },
  }).text, '{\n----------"a": 1\n}');
});

test("stringifyChunked array replacer is an ordered key allowlist", () => {
  assert.equal(callJsonExt("stringify", {
    value: { a: 1, b: 2, 1: "one" }, options: { replacer: ["b", 1] },
  }).text, '{"b":2,"1":"one"}');
});

test("stringifyChunked removes duplicate replacer keys", () => {
  assert.equal(callJsonExt("stringify", {
    value: { a: 1, b: 2 }, options: { replacer: ["a", "a", "b"] },
  }).text, '{"a":1,"b":2}');
});

test("stringifyChunked jsonl mode serializes array roots", () => {
  assert.equal(callJsonExt("stringify", {
    value: [{ id: 1 }, { id: 2 }, 3], options: { mode: "jsonl" },
  }).text, '{"id":1}\n{"id":2}\n3');
});

test("stringifyChunked jsonl mode emits no trailing newline", () => {
  const result = callJsonExt("stringify", { value: [1, 2], options: { mode: "jsonl" } });
  assert.equal(result.text, "1\n2");
  assert.equal(result.text.endsWith("\n"), false);
});

test("stringifyChunked jsonl mode emits no chunks for an empty array", () => {
  assert.deepEqual(callJsonExt("stringify", { value: [], options: { mode: "jsonl" } }), {
    chunks: [], text: "",
  });
});

test("stringifyChunked jsonl mode treats a non-array as one root", () => {
  assert.equal(callJsonExt("stringify", { value: { id: 1 }, options: { mode: "jsonl" } }).text, '{"id":1}');
});

test("stringifyChunked normalizes non-finite numbers to null", () => {
  assert.equal(callJsonExt("stringify", { special: "non-finite" }).text, '{"nan":null,"positive":null,"negative":null}');
});

test("stringifyChunked emits null for root undefined", () => {
  assert.equal(callJsonExt("stringify", { special: "undefined" }).text, "null");
});

test("stringifyChunked rejects circular structures", () => {
  const result = callJsonExtFailure("stringify", { special: "circular-one" });
  assert.equal(result.exceptionType, "TypeError");
  assert.equal(result.message, "Converting circular structure to JSON");
});

test("stringifyChunked rejects an invalid mode", () => {
  const result = callJsonExtFailure("stringify", { value: 1, options: { mode: "auto" } });
  assert.equal(result.exceptionType, "TypeError");
  assert.equal(result.message, "Invalid options: `mode` should be \"json\" or \"jsonl\"");
});

test("stringifyInfo reports compact UTF-8 byte size", () => {
  assert.deepEqual(callJsonExt("info", { value: { word: "漢字" } }), {
    bytes: Buffer.byteLength('{"word":"漢字"}'), spaceBytes: 0, circularCount: 0,
  });
});

test("stringifyInfo matches chunked output for an acyclic value", () => {
  const value = { a: 1, b: [true, "x"] };
  const output = callJsonExt("stringify", { value, options: { space: 2 } }).text;
  const info = callJsonExt("info", { value, options: { space: 2 } });
  assert.equal(info.bytes, Buffer.byteLength(output));
  assert.equal(info.circularCount, 0);
  assert.ok(info.spaceBytes > 0);
});

test("stringifyInfo counts pretty-print whitespace", () => {
  assert.deepEqual(callJsonExt("info", { value: { test: true }, options: { space: 4 } }), {
    bytes: 20, spaceBytes: 7, circularCount: 0,
  });
});

test("stringifyInfo applies an array replacer", () => {
  assert.deepEqual(callJsonExt("info", {
    value: { a: 1, b: 2 }, options: { replacer: ["b"] },
  }), { bytes: 7, spaceBytes: 0, circularCount: 0 });
});

test("stringifyInfo includes JSONL separators in total bytes", () => {
  assert.deepEqual(callJsonExt("info", { value: [1, 2, 3], options: { mode: "jsonl" } }), {
    bytes: 5, spaceBytes: 0, circularCount: 0,
  });
});

test("stringifyInfo reports the package-specific root undefined size", () => {
  assert.deepEqual(callJsonExt("info", { special: "undefined" }), {
    bytes: 9, spaceBytes: 0, circularCount: 0,
  });
});

test("stringifyInfo stops after the first circular object by default", () => {
  assert.deepEqual(callJsonExt("info", { special: "circular-two" }), {
    bytes: 31, spaceBytes: 0, circularCount: 1,
  });
});

test("stringifyInfo can continue and report multiple circular objects", () => {
  const result = callJsonExt("info", {
    special: "circular-two", options: { continueOnCircular: true },
  });
  assert.equal(result.circularCount, 2);
  assert.ok(result.bytes > 22);
});

test("stringifyInfo rejects an invalid mode", () => {
  const result = callJsonExtFailure("info", { value: 1, options: { mode: "auto" } });
  assert.equal(result.exceptionType, "TypeError");
  assert.equal(result.message, "Invalid options: `mode` should be \"json\" or \"jsonl\"");
});

test("parseFromWebStream parses string chunks", () => {
  assert.deepEqual(callJsonExt("parseWeb", { chunks: ["{\"foo", "\":123}"] }), { foo: 123 });
});

test("parseFromWebStream parses UTF-8 byte chunks", () => {
  assert.deepEqual(callJsonExt("parseWeb", {
    chunks: [{ bytes: [91, 34, 240, 159] }, { bytes: [164, 147, 34, 93] }],
  }), ["🤓"]);
});

test("parseFromWebStream falls back when async iteration is unavailable", () => {
  assert.deepEqual(callJsonExt("parseWeb", {
    chunks: ["{\"foo", "\":123}"], nonIterable: true,
  }), { foo: 123 });
});

test("createStringifyWebStream preserves default generator chunks", () => {
  assert.deepEqual(callJsonExt("stringifyWeb", { value: { foo: 123, bar: 456 } }), {
    chunks: ['{"foo":123,"bar":456}'], text: '{"foo":123,"bar":456}',
  });
});

test("createStringifyWebStream accepts chunking and formatting options", () => {
  assert.deepEqual(callJsonExt("stringifyWeb", {
    value: { foo: 123, bar: 456 }, options: { highWaterMark: 1, replacer: ["foo"], space: 4 },
  }).chunks, ['{\n    "foo": 123', '\n}']);
});

test("createStringifyWebStream supports cancellation", () => {
  assert.deepEqual(callJsonExt("stringifyWeb", {
    value: { foo: 123, bar: 456 }, options: { highWaterMark: 1 }, cancelAfterFirst: true,
  }), {
    first: { value: '{"foo":123', done: false },
    afterCancel: { value: null, done: true },
  });
});
