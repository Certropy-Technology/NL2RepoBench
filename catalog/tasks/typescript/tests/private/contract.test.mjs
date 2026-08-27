import assert from "node:assert/strict";
import { test } from "node:test";
import { callCandidate } from "./test_client.mjs";

const kinds = (text, options = {}) => callCandidate({ op: "scan", text, skipTrivia: true, ...options }).map((token) => token.kind);
const utility = (name, payload = {}) => callCandidate({ op: "utility", name, ...payload });
const baseSegments = [
  { virtualStart: 2, virtualEnd: 6, originalStart: 10, originalEnd: 14, kind: "Verbatim" },
  { virtualStart: 8, virtualEnd: 11, originalStart: 20, originalEnd: 27, kind: "Atom" },
  { virtualStart: 14, virtualEnd: 18, originalStart: 30, originalEnd: 34, kind: "Verbatim" },
];
const map = (action, payload = {}, segments = baseSegments) => callCandidate({ op: "spanMap", action, segments, ...payload });

test("package metadata is the frozen native-preview identity", () => {
  const value = callCandidate({ op: "metadata" });
  assert.deepEqual({ name: value.name, version: value.version, type: value.type }, { name: "@typescript/typescript", version: "0.0.0", type: "module" });
  assert.equal(value.rootVersion, "0.0.0");
  assert.equal(value.versionMajorMinor, "7.1");
});

test("distribution has no runtime dependency or script surface", () => {
  const value = callCandidate({ op: "metadata" });
  assert.equal(value.scripts, null);
  assert.equal(value.dependencies, null);
  assert.equal(value.devDependencies, null);
});

test("distribution exports the bounded root and AST entrypoints", () => {
  const value = callCandidate({ op: "metadata" });
  assert.deepEqual(value.exports, [".", "./package.json", "./unstable/ast", "./unstable/ast/scanner"]);
});

test("scanner recognizes declarations and type punctuation", () => {
  assert.deepEqual(kinds("let value: number = 42;"), ["LetKeyword", "Identifier", "ColonToken", "NumberKeyword", "EqualsToken", "NumericLiteral", "SemicolonToken", "EndOfFile"]);
});

test("scanner exposes trivia when skipTrivia is false", () => {
  const tokens = callCandidate({ op: "scan", text: " \n// note\nvalue", skipTrivia: false });
  assert.deepEqual(tokens.map((token) => token.kind), ["WhitespaceTrivia", "NewLineTrivia", "SingleLineCommentTrivia", "NewLineTrivia", "Identifier", "EndOfFile"]);
  assert.equal(tokens[2].text, "// note");
});

test("scanner skips trivia and reports a preceding line break", () => {
  const tokens = callCandidate({ op: "scan", text: " \n/* note */\nvalue", skipTrivia: true });
  assert.deepEqual(tokens.map((token) => token.kind), ["Identifier", "EndOfFile"]);
  assert.equal(tokens[0].precedingLineBreak, true);
});

test("scanner recognizes numeric literal families", () => {
  assert.deepEqual(kinds("0 0x2a 0b101 0o77 1_000 1.5e2 10n"), ["NumericLiteral", "NumericLiteral", "NumericLiteral", "NumericLiteral", "NumericLiteral", "NumericLiteral", "BigIntLiteral", "EndOfFile"]);
});

test("scanner decodes string escapes and Unicode escapes", () => {
  const tokens = callCandidate({ op: "scan", text: "\"a\\n\" 'b\\u0063'", skipTrivia: true });
  assert.deepEqual(tokens.map((token) => token.kind), ["StringLiteral", "StringLiteral", "EndOfFile"]);
  assert.deepEqual(tokens.slice(0, 2).map((token) => token.value), ["a\n", "bc"]);
  assert.equal(tokens[1].unicodeEscape, true);
});

test("scanner accepts Unicode identifier text", () => {
  const tokens = callCandidate({ op: "scan", text: "π café", skipTrivia: true });
  assert.deepEqual(tokens.map((token) => token.kind), ["Identifier", "Identifier", "EndOfFile"]);
  assert.deepEqual(tokens.slice(0, 2).map((token) => token.value), ["π", "café"]);
});

test("scanner recognizes modern operators", () => {
  assert.deepEqual(kinds("?. ?? ??= => ** **="), ["QuestionDotToken", "QuestionQuestionToken", "QuestionQuestionEqualsToken", "EqualsGreaterThanToken", "AsteriskAsteriskToken", "AsteriskAsteriskEqualsToken", "EndOfFile"]);
});

test("scanner recognizes contextual and reserved keywords", () => {
  assert.deepEqual(kinds("class interface satisfies using await async from of"), ["ClassKeyword", "InterfaceKeyword", "SatisfiesKeyword", "UsingKeyword", "AwaitKeyword", "AsyncKeyword", "FromKeyword", "OfKeyword", "EndOfFile"]);
});

test("scanner recognizes no-substitution template literals", () => {
  const tokens = callCandidate({ op: "scan", text: "`hello\\nworld`", skipTrivia: true });
  assert.deepEqual(tokens.map((token) => token.kind), ["NoSubstitutionTemplateLiteral", "EndOfFile"]);
  assert.equal(tokens[0].value, "hello\nworld");
});

test("scanner marks unterminated string literals", () => {
  const tokens = callCandidate({ op: "scan", text: "'missing", skipTrivia: true });
  assert.equal(tokens[0].kind, "StringLiteral");
  assert.equal(tokens[0].unterminated, true);
  assert.equal(tokens[0].end, 8);
});

test("scanner honors explicit start and length bounds", () => {
  const tokens = callCandidate({ op: "scan", text: "before target after", skipTrivia: true, start: 7, length: 6 });
  assert.deepEqual(tokens.map((token) => token.kind), ["Identifier", "EndOfFile"]);
  assert.equal(tokens[0].text, "target");
  assert.deepEqual([tokens[0].start, tokens[0].end], [7, 13]);
});

test("token text maps in both directions", () => {
  assert.equal(utility("tokenToString", { kind: "EqualsGreaterThanToken" }), "=>");
  assert.equal(utility("stringToToken", { text: "satisfies" }), "SatisfiesKeyword");
  assert.equal(utility("stringToToken", { text: "not-a-token" }), null);
});

test("computeLineStarts handles LF CRLF and Unicode separators", () => {
  assert.deepEqual(utility("computeLineStarts", { text: "a\nb\r\nc\u2028d" }), [0, 2, 5, 7]);
});

test("skipTrivia supports comments and line breaks", () => {
  const text = " \t/*x*/\r\n//y\nvalue";
  assert.equal(utility("skipTrivia", { text, position: 0 }), 13);
  assert.equal(utility("skipTrivia", { text, position: 0, stopAfterLineBreak: true }), 9);
});

test("getShebang returns only a leading hashbang", () => {
  assert.equal(utility("getShebang", { text: "#!/usr/bin/env node\nlet x" }), "#!/usr/bin/env node");
  assert.equal(utility("getShebang", { text: " \n#!/bin/sh" }), null);
});

test("identifier validation follows target and language variant", () => {
  assert.equal(utility("isIdentifierText", { text: "hello_π" }), true);
  assert.equal(utility("isIdentifierText", { text: "hello-world" }), false);
  assert.equal(utility("isIdentifierText", { text: "class" }), true);
  assert.equal(utility("isIdentifierText", { text: "123x" }), false);
});

test("leading comment ranges preserve kind and line termination", () => {
  assert.deepEqual(utility("commentRanges", { side: "leading", text: "// a\n/* b */value", position: 0 }), [
    { kind: "SingleLineCommentTrivia", pos: 0, end: 4, hasTrailingNewLine: true },
    { kind: "MultiLineCommentTrivia", pos: 5, end: 12, hasTrailingNewLine: false },
  ]);
});

test("trailing comment ranges begin at a token boundary", () => {
  assert.deepEqual(utility("commentRanges", { side: "trailing", text: "value /* b */ // c\nnext", position: 5 }), [
    { kind: "MultiLineCommentTrivia", pos: 6, end: 13, hasTrailingNewLine: false },
    { kind: "SingleLineCommentTrivia", pos: 14, end: 18, hasTrailingNewLine: true },
  ]);
});

test("SpanMap maps exact virtual positions", () => {
  assert.deepEqual(map("virtualToOriginalPosition", { position: 4 }), { position: 12, fidelity: "Exact" });
  assert.deepEqual(map("virtualToOriginalPosition", { position: 18 }), { position: 34, fidelity: "Exact" });
});

test("SpanMap maps synthesized gaps to insertion points", () => {
  assert.deepEqual(map("virtualToOriginalPosition", { position: 0 }), { position: 0, fidelity: "None" });
  assert.deepEqual(map("virtualToOriginalSpan", { range: { pos: 6, end: 8 } }), { range: { pos: 14, end: 14 }, fidelity: "None" });
});

test("SpanMap maps atom segments as indivisible ranges", () => {
  assert.deepEqual(map("virtualToOriginalPosition", { position: 9 }), { position: 20, fidelity: "Atom" });
  assert.deepEqual(map("virtualToOriginalSpan", { range: { pos: 8, end: 10 } }), { range: { pos: 20, end: 27 }, fidelity: "Atom" });
});

test("SpanMap marks cross-segment mappings approximate", () => {
  assert.deepEqual(map("virtualToOriginalSpan", { range: { pos: 5, end: 15 } }), { range: { pos: 13, end: 31 }, fidelity: "Approximate" });
});

test("SpanMap maps original positions to every virtual projection", () => {
  const segments = [
    { virtualStart: 0, virtualEnd: 3, originalStart: 10, originalEnd: 13, kind: "Verbatim", features: "Hover" },
    { virtualStart: 10, virtualEnd: 13, originalStart: 10, originalEnd: 13, kind: "Verbatim", features: "Hover" },
  ];
  assert.deepEqual(map("originalToVirtualPositions", { position: 11, feature: "Hover" }, segments), [
    { position: 1, fidelity: "Exact" },
    { position: 11, fidelity: "Exact" },
  ]);
});

test("SpanMap filters mappings by feature", () => {
  const segments = [{ virtualStart: 0, virtualEnd: 3, originalStart: 10, originalEnd: 13, kind: "Verbatim", features: "Definition" }];
  assert.deepEqual(map("originalToVirtualPositions", { position: 11, feature: "Hover" }, segments), []);
  assert.deepEqual(map("originalToVirtualPositions", { position: 11, feature: "Definition" }, segments), [{ position: 1, fidelity: "Exact" }]);
});

test("SpanMap feature-aware virtual mappings reject disabled spans", () => {
  const segments = [{ virtualStart: 0, virtualEnd: 3, originalStart: 10, originalEnd: 13, kind: "Verbatim", features: "Definition" }];
  assert.deepEqual(map("virtualToOriginalPositionForFeature", { position: 1, feature: "Hover" }, segments), { position: 11, fidelity: "None" });
  assert.deepEqual(map("virtualToOriginalPositionForFeature", { position: 1, feature: "Definition" }, segments), { position: 11, fidelity: "Exact" });
});

test("SpanMap handles empty maps deterministically", () => {
  assert.deepEqual(map("virtualToOriginalPosition", { position: 5 }, []), { position: 0, fidelity: "None" });
  assert.deepEqual(map("originalToVirtualPositions", { position: 5, feature: "All" }, []), []);
});

test("SpanMap exposes fidelity predicates", () => {
  assert.deepEqual(map("predicates", { fidelity: "Exact" }), { exact: true, singleSegment: true, none: false });
  assert.deepEqual(map("predicates", { fidelity: "Atom" }), { exact: false, singleSegment: true, none: false });
  assert.deepEqual(map("predicates", { fidelity: "None" }), { exact: false, singleSegment: false, none: true });
});
