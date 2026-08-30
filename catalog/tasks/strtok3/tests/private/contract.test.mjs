import assert from "node:assert/strict";
import test from "node:test";
import { call, session } from "./test_client.mjs";

const bytes = [0x05, 0x70, 0x65, 0x74, 0x65, 0x72, 0xff, 0x10, 0x20];

test("package identity and ESM metadata", () => {
  const value = call({ op: "inventory" });
  assert.equal(value.name, "strtok3");
  assert.equal(value.version, "10.3.5");
  assert.equal(value.type, "module");
  assert.equal(value.types, "lib/index.d.ts");
});

test("root exports required factories", () => {
  const exports = call({ op: "inventory" }).exports;
  for (const name of ["fromBuffer", "fromBlob", "fromWebStream", "fromStream", "fromFile"]) {
    assert.ok(exports.includes(name), name);
  }
});

test("root exports classes and errors", () => {
  const exports = call({ op: "inventory" }).exports;
  for (const name of ["AbstractTokenizer", "FileTokenizer", "EndOfStreamError", "AbortError"]) {
    assert.ok(exports.includes(name), name);
  }
});

test("package has exact runtime dependency", () => {
  assert.deepEqual(call({ op: "inventory" }).dependencies, { "@tokenizer/token": "0.3.0" });
});

test("buffer starts at zero with size and random access", () => {
  const [r] = session("buffer", bytes, [{ op: "info" }]);
  assert.deepEqual(r.value, { position: 0, fileInfo: { size: 9 }, randomAccess: true });
});

test("buffer preserves caller file information and replaces size", () => {
  const [r] = session("buffer", bytes, [{ op: "info" }], { fileInfo: { mimeType: "audio/test", size: 99 } });
  assert.equal(r.value.fileInfo.mimeType, "audio/test");
  assert.equal(r.value.fileInfo.size, bytes.length);
});

test("readBuffer default length advances", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 4 }]);
  assert.deepEqual(r.value, { count: 4, bytes: bytes.slice(0, 4), position: 4 });
});

test("readBuffer explicit length leaves zero suffix", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 5, options: { length: 2 } }]);
  assert.deepEqual(r.value, { count: 2, bytes: [5, 112, 0, 0, 0], position: 2 });
});

test("readBuffer absolute position seeks and advances", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 3, options: { position: 3 } }]);
  assert.deepEqual(r.value, { count: 3, bytes: [116, 101, 114], position: 6 });
});

test("readBuffer mayBeLess returns remaining bytes", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 5, options: { position: 7, mayBeLess: true } }]);
  assert.deepEqual(r.value, { count: 2, bytes: [16, 32, 0, 0, 0], position: 9 });
});

test("readBuffer exact EOF succeeds", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 2, options: { position: 7 } }]);
  assert.equal(r.ok, true);
  assert.equal(r.value.position, 9);
});

test("readBuffer beyond EOF throws EndOfStreamError", () => {
  const [r] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 3, options: { position: 7 } }]);
  assert.equal(r.ok, false);
  assert.equal(r.exceptionType, "EndOfStreamError");
});

test("peekBuffer does not advance", () => {
  const [peek, info] = session("buffer", bytes, [{ op: "peekBuffer", targetSize: 3 }, { op: "info" }]);
  assert.deepEqual(peek.value.bytes, bytes.slice(0, 3));
  assert.equal(info.value.position, 0);
});

test("peekBuffer at absolute position does not advance", () => {
  const [peek, info] = session("buffer", bytes, [{ op: "peekBuffer", targetSize: 3, options: { position: 4 } }, { op: "info" }]);
  assert.deepEqual(peek.value.bytes, [101, 114, 255]);
  assert.equal(info.value.position, 0);
});

test("peekBuffer mayBeLess returns partial data", () => {
  const [peek] = session("buffer", bytes, [{ op: "peekBuffer", targetSize: 5, options: { position: 8, mayBeLess: true } }]);
  assert.equal(peek.value.count, 1);
  assert.deepEqual(peek.value.bytes, [32, 0, 0, 0, 0]);
});

test("sequential readBuffer calls preserve state", () => {
  const [a, b] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 2 }, { op: "readBuffer", targetSize: 3 }]);
  assert.deepEqual(a.value.bytes, [5, 112]);
  assert.deepEqual(b.value.bytes, [101, 116, 101]);
  assert.equal(b.value.position, 5);
});

test("ignore advances by requested length", () => {
  const [r] = session("buffer", bytes, [{ op: "ignore", length: 4 }]);
  assert.deepEqual(r.value, { count: 4, position: 4 });
});

test("ignore clamps to remaining buffer", () => {
  const [a, b] = session("buffer", bytes, [{ op: "ignore", length: 7 }, { op: "ignore", length: 99 }]);
  assert.equal(a.value.position, 7);
  assert.deepEqual(b.value, { count: 2, position: 9 });
});

test("negative ignore throws RangeError without moving", () => {
  const [r] = session("buffer", bytes, [{ op: "ignore", length: -1 }]);
  assert.equal(r.exceptionType, "RangeError");
  assert.equal(r.position, 0);
});

test("setPosition changes random access cursor", () => {
  const [set, read] = session("buffer", bytes, [{ op: "setPosition", position: 6 }, { op: "readBuffer", targetSize: 2 }]);
  assert.equal(set.value.position, 6);
  assert.deepEqual(read.value.bytes, [255, 16]);
});

test("readToken decodes uint8 and advances", () => {
  const [r] = session("buffer", bytes, [{ op: "readToken", token: { kind: "uint8", len: 1 } }]);
  assert.deepEqual(r.value, { value: 5, position: 1 });
});

test("readToken decodes UTF-8 custom token", () => {
  const [r] = session("buffer", bytes, [{ op: "readToken", token: { kind: "utf8", len: 5 }, position: 1 }]);
  assert.deepEqual(r.value, { value: "peter", position: 6 });
});

test("peekToken does not advance", () => {
  const [r] = session("buffer", bytes, [{ op: "peekToken", token: { kind: "uint16le", len: 2 }, position: 7 }]);
  assert.deepEqual(r.value, { value: 8208, position: 0 });
});

test("readNumber decodes signed big endian", () => {
  const [r] = session("buffer", [0xff, 0xfe], [{ op: "readNumber", token: { kind: "int16be", len: 2 } }]);
  assert.deepEqual(r.value, { value: -2, position: 2 });
});

test("peekNumber does not advance", () => {
  const [r] = session("buffer", [0x12, 0x34], [{ op: "peekNumber", token: { kind: "uint32be", len: 4 } }]);
  assert.equal(r.ok, false);
  assert.equal(r.exceptionType, "EndOfStreamError");
  assert.equal(r.position, 0);
});

test("readToken partial token throws EndOfStreamError", () => {
  const [r] = session("buffer", [1], [{ op: "readToken", token: { kind: "int16be", len: 2 } }]);
  assert.equal(r.exceptionType, "EndOfStreamError");
});

for (const source of ["blob", "web", "stream"]) {
  test(`${source} source reads and advances`, () => {
    const [r, info] = session(source, bytes, [{ op: "readBuffer", targetSize: 4 }, { op: "info" }]);
    assert.deepEqual(r.value.bytes, bytes.slice(0, 4));
    assert.equal(info.value.position, 4);
  });

  test(`${source} source peeks without advancing`, () => {
    const [r, info] = session(source, bytes, [{ op: "peekBuffer", targetSize: 3 }, { op: "info" }]);
    assert.deepEqual(r.value.bytes, bytes.slice(0, 3));
    assert.equal(info.value.position, 0);
  });
}

test("blob reports size and random access", () => {
  const [r] = session("blob", bytes, [{ op: "info" }]);
  assert.deepEqual(r.value, { position: 0, fileInfo: { size: bytes.length, mimeType: "" }, randomAccess: true });
});

test("web stream is sequential", () => {
  const [r] = session("web", bytes, [{ op: "info" }]);
  assert.equal(r.value.randomAccess, false);
});

test("node stream is sequential", () => {
  const [r] = session("stream", bytes, [{ op: "info" }]);
  assert.equal(r.value.randomAccess, false);
});

test("sequential stream rejects backward position", () => {
  const [a, b] = session("stream", bytes, [{ op: "readBuffer", targetSize: 3 }, { op: "peekBuffer", targetSize: 1, options: { position: 1 } }]);
  assert.equal(a.ok, true);
  assert.equal(b.ok, false);
  assert.match(b.message, /position/);
});

test("file source reports path size and random access", () => {
  const [r] = session("file", bytes, [{ op: "info" }]);
  assert.equal(r.value.fileInfo.size, bytes.length);
  assert.match(r.value.fileInfo.path, /strtok3-candidate\.bin$/);
  assert.equal(r.value.randomAccess, true);
});

test("file source supports random read", () => {
  const [r] = session("file", bytes, [{ op: "readBuffer", targetSize: 3, options: { position: 5 } }]);
  assert.deepEqual(r.value.bytes, [114, 255, 16]);
  assert.equal(r.value.position, 8);
});

test("file stream discovers path and size", () => {
  const [r] = session("file-stream", bytes, [{ op: "info" }]);
  assert.equal(r.value.fileInfo.size, bytes.length);
  assert.match(r.value.fileInfo.path, /strtok3-candidate-stream\.bin$/);
});

test("abort resolves and preserves position", () => {
  const [read, aborted] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 2 }, { op: "abort" }]);
  assert.equal(read.value.position, 2);
  assert.equal(aborted.value.position, 2);
});

test("close resolves and preserves position", () => {
  const [read, closed] = session("buffer", bytes, [{ op: "readBuffer", targetSize: 2 }, { op: "close" }]);
  assert.equal(read.value.position, 2);
  assert.equal(closed.value.position, 2);
});

test("empty buffer may return zero when mayBeLess", () => {
  const [r] = session("buffer", [], [{ op: "readBuffer", targetSize: 4, options: { mayBeLess: true } }]);
  assert.deepEqual(r.value, { count: 0, bytes: [0, 0, 0, 0], position: 0 });
});

test("empty buffer strict read throws", () => {
  const [r] = session("buffer", [], [{ op: "readBuffer", targetSize: 1 }]);
  assert.equal(r.exceptionType, "EndOfStreamError");
});

test("repeated independent sessions are deterministic", () => {
  const request = { op: "session", source: "buffer", bytes, steps: [{ op: "readBuffer", targetSize: 5 }] };
  assert.deepEqual(call(request), call(request));
});
