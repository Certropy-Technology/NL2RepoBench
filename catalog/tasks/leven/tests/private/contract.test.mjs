import assert from "node:assert/strict";
import test from "node:test";
import {callCandidate, closest, distance} from "./test_client.mjs";

test("package metadata identifies an ESM leven package", () => {
  const result = callCandidate({operation: "metadata"});
  assert.deepEqual(result.data, {name: "leven", version: "4.1.0", type: "module", hasDefault: true, hasClosestMatch: true});
});

test("default export is callable from the package root", () => assert.equal(distance("a", "b"), 1));
test("named closestMatch export is callable from the package root", () => assert.equal(closest("cat", ["cut"]), "cut"));
test("package exposes both exports without an internal import", () => {
  const result = callCandidate({operation: "metadata"});
  assert.equal(result.data.hasDefault && result.data.hasClosestMatch, true);
});

test("empty strings have their length as distance", () => {
  assert.equal(distance("", ""), 0);
  assert.equal(distance("", "abc"), 3);
  assert.equal(distance("abc", ""), 3);
});
test("identical strings have zero distance", () => assert.equal(distance("same text", "same text"), 0));
test("one substitution costs one edit", () => assert.equal(distance("ab", "ac"), 1));
test("one insertion costs one edit", () => assert.equal(distance("cat", "cart"), 1));
test("one deletion costs one edit", () => assert.equal(distance("cart", "cat"), 1));
test("distance is symmetric", () => assert.equal(distance("sturgeon", "urgently"), distance("urgently", "sturgeon")));
test("classic kitten example returns three", () => assert.equal(distance("kitten", "sitting"), 3));
test("common examples preserve exact integer results", () => {
  assert.equal(distance("xabxcdxxefxgx", "1ab2cd34ef5g6"), 6);
  assert.equal(distance("distance", "difference"), 5);
});
test("repeated characters are handled correctly", () => assert.equal(distance("aaaaab", "baaaaa"), 2));
test("non-ASCII strings use JavaScript string semantics", () => assert.equal(distance("因為我是中國人所以我會說中文", "因為我是英國人所以我會說英文"), 2));
test("surrogate-pair strings are measured by UTF-16 code units", () => assert.equal(distance("😀", "😃"), 1));
test("long common prefix and suffix remain exact", () => assert.equal(distance("prefix-123456789-suffix", "prefix-123456780-suffix"), 1));

test("maxDistance keeps an exact result below the cutoff", () => assert.equal(distance("cat", "cut", {maxDistance: 5}), 1));
test("maxDistance caps a result above the cutoff", () => assert.equal(distance("kitten", "sitting", {maxDistance: 2}), 2));
test("zero maxDistance returns zero for a different string", () => assert.equal(distance("abc", "abd", {maxDistance: 0}), 0));
test("large length differences are capped", () => assert.equal(distance("a", "abcdefgh", {maxDistance: 3}), 3));
test("cutoff behavior is symmetric", () => assert.equal(distance("abcdefgh", "a", {maxDistance: 3}), 3));
test("empty input obeys a smaller cutoff", () => assert.equal(distance("", "abc", {maxDistance: 2}), 2));
test("empty input returns its exact distance with a generous cutoff", () => assert.equal(distance("", "abc", {maxDistance: 10}), 3));
test("omitted, undefined, and null options preserve the exact result", () => {
  assert.equal(distance("foo", "bar"), 3);
  assert.equal(distance("foo", "bar", undefined), 3);
  assert.equal(distance("foo", "bar", null), 3);
});

test("closestMatch selects the nearest candidate", () => assert.equal(closest("hello", ["jello", "yellow", "bellow"]), "jello"));
test("closestMatch prefers an exact candidate", () => assert.equal(closest("foo", ["bar", "foo", "baz"]), "foo"));
test("closestMatch handles a single candidate", () => assert.equal(closest("test", ["testing"]), "testing"));
test("closestMatch returns undefined for an empty list", () => assert.equal(closest("test", []), undefined));
test("closestMatch preserves the first equal-distance candidate", () => assert.equal(closest("a", ["b", "c", "d"]), "b"));
test("duplicate candidates do not change the answer", () => assert.equal(closest("abc", ["ab", "ab", "abcd"]), "ab"));
test("closestMatch accepts a candidate at the cutoff", () => assert.equal(closest("kitten", ["sitting", "kitchen"], {maxDistance: 2}), "kitchen"));
test("closestMatch returns undefined when all candidates exceed the cutoff", () => assert.equal(closest("kitten", ["sitting", "kitchen"], {maxDistance: 1}), undefined));
test("closestMatch handles an empty target", () => assert.equal(closest("", ["a", "ab", "abc"]), "a"));
test("closestMatch is case-sensitive", () => assert.equal(closest("Hello", ["hello", "HELLO", "hELLo"]), "hello"));
test("closestMatch uses the same UTF-16 distance for Unicode", () => assert.equal(closest("café", ["cafe", "caffè", "café"]), "café"));
test("closestMatch remains deterministic for a long candidate list", () => {
  const candidates = Array.from({length: 50}, (_, index) => `candidate-${index}`);
  candidates.push("test");
  assert.equal(closest("test", candidates), "test");
});

test("non-array candidates are rejected by the child boundary", () => {
  assert.throws(() => callCandidate({operation: "closestMatch", target: "test", candidates: null}), /candidate-call-failed/);
});
test("maxDistance zero only accepts an exact closest match", () => {
  assert.equal(closest("test", ["tests", "testing"], {maxDistance: 0}), undefined);
});
test("a shorter tied candidate keeps input order", () => assert.equal(closest("abc", ["ab", "bc", "ac"]), "ab"));
test("a closer candidate beats an earlier farther candidate", () => assert.equal(closest("test", ["testing", "tests"]), "tests"));

test("closestMatch does not mutate its candidate array", () => {
  const candidates = ["sitting", "kitchen", "mittens"];
  const before = [...candidates];
  closest("kitten", candidates);
  assert.deepEqual(candidates, before);
});
test("leven does not mutate the options object", () => {
  const options = {maxDistance: 2};
  assert.equal(distance("kitten", "sitting", options), 2);
  assert.deepEqual(options, {maxDistance: 2});
});
test("repeated calls return identical results", () => {
  const values = Array.from({length: 5}, () => closest("testing", ["test", "testing", "toast"]));
  assert.deepEqual(values, ["testing", "testing", "testing", "testing", "testing"]);
});
test("Unicode nearest matching is deterministic", () => assert.equal(closest("你好", ["您好", "你们好", "大家好"]), "您好"));
