import assert from "node:assert/strict";
import test from "node:test";
const {callCandidate} = await import("./test_client.mjs");

test("root ESM and CommonJS exports expose the named class", () => {
  assert.deepEqual(callCandidate("inventory"), {
    cjsClass: "function",
    esmClass: "function",
    cjsDefaultAbsent: true,
    effectiveUid: 10001,
    effectiveGid: 10001,
  });
});
test("root package reports the expected class identity on repeated loading", () => {
  assert.deepEqual(callCandidate("inventory"), {
    cjsClass: "function",
    esmClass: "function",
    cjsDefaultAbsent: true,
    effectiveUid: 10001,
    effectiveGid: 10001,
  });
});

test("single line index zero", () => assert.deepEqual(callCandidate("location", ["abcd", 0]), {line: 0, column: 0}));
test("single line index middle", () => assert.deepEqual(callCandidate("location", ["abcd", 2]), {line: 0, column: 2}));
test("single line index end", () => assert.deepEqual(callCandidate("location", ["abcd", 4]), {line: 0, column: 4}));
test("LF index remains on preceding line", () => assert.deepEqual(callCandidate("location", ["ab\ncd", 2]), {line: 0, column: 2}));
test("LF index after newline starts line one", () => assert.deepEqual(callCandidate("location", ["ab\ncd", 3]), {line: 1, column: 0}));
test("LF line zero end maps to newline offset", () => assert.equal(callCandidate("index", ["ab\ncd", {line: 0, column: 2}]), 2));
test("LF line one start maps after newline", () => assert.equal(callCandidate("index", ["ab\ncd", {line: 1, column: 0}]), 3));
test("LF line one end maps to string length", () => assert.equal(callCandidate("index", ["ab\ncd", {line: 1, column: 2}]), 5));

test("CR index remains on preceding line", () => assert.deepEqual(callCandidate("location", ["a\rb", 1]), {line: 0, column: 1}));
test("CR index after newline starts next line", () => assert.deepEqual(callCandidate("location", ["a\rb", 2]), {line: 1, column: 0}));
test("CR location round trip", () => assert.equal(callCandidate("index", ["a\rb", {line: 1, column: 0}]), 2));
test("CRLF CR code unit is preceding line", () => assert.deepEqual(callCandidate("location", ["a\r\nb", 1]), {line: 0, column: 1}));
test("CRLF LF code unit is preceding line", () => assert.deepEqual(callCandidate("location", ["a\r\nb", 2]), {line: 0, column: 2}));
test("CRLF following text starts next line", () => assert.deepEqual(callCandidate("location", ["a\r\nb", 3]), {line: 1, column: 0}));
test("CRLF line zero accepts both newline columns", () => assert.equal(callCandidate("index", ["a\r\nb", {line: 0, column: 2}]), 2));
test("CRLF line one start maps after both units", () => assert.equal(callCandidate("index", ["a\r\nb", {line: 1, column: 0}]), 3));
test("mixed CR and LF create independent lines", () => assert.deepEqual(callCandidate("location", ["a\rb\nc", 4]), {line: 2, column: 0}));

test("empty string has one empty line", () => assert.deepEqual(callCandidate("location", ["", 0]), {line: 0, column: 0}));
test("empty string index location is zero", () => assert.equal(callCandidate("index", ["", {line: 0, column: 0}]), 0));
test("trailing LF creates an empty final line", () => assert.deepEqual(callCandidate("location", ["a\n", 2]), {line: 1, column: 0}));
test("trailing CR creates an empty final line", () => assert.deepEqual(callCandidate("location", ["a\r", 2]), {line: 1, column: 0}));
test("UTF-16 emoji occupies two columns", () => assert.deepEqual(callCandidate("location", ["😀x", 2]), {line: 0, column: 2}));
test("UTF-16 emoji line location maps back", () => assert.equal(callCandidate("index", ["😀x", {line: 0, column: 2}]), 2));

test("negative index returns null", () => assert.equal(callCandidate("location", ["a", -1]), null));
test("index beyond string returns null", () => assert.equal(callCandidate("location", ["a", 2]), null));
test("negative line returns null", () => assert.equal(callCandidate("index", ["a\nb", {line: -1, column: 0}]), null));
test("line beyond recorded lines returns null", () => assert.equal(callCandidate("index", ["a\nb", {line: 2, column: 0}]), null));
test("negative column returns null", () => assert.equal(callCandidate("index", ["a", {line: 0, column: -1}]), null));
test("column beyond line length returns null", () => assert.equal(callCandidate("index", ["a", {line: 0, column: 2}]), null));
test("column beyond a CRLF line span returns null", () => assert.equal(callCandidate("index", ["a\r\nb", {line: 0, column: 4}]), null));

test("valid location round trips to the same offset", () => {
  const location = callCandidate("location", ["first\nsecond", 8]);
  assert.equal(callCandidate("index", ["first\nsecond", location]), 8);
});
test("newline location round trips deterministically", () => {
  const location = callCandidate("location", ["x\r\ny", 2]);
  assert.deepEqual(location, {line: 0, column: 2});
  assert.equal(callCandidate("index", ["x\r\ny", location]), 2);
});
