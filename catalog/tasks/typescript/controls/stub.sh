#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/lib /workspace/dist/ast
cat > /workspace/package.json <<'JSON'
{
  "name": "@typescript/typescript",
  "version": "0.0.0",
  "license": "Apache-2.0",
  "type": "module",
  "exports": {
    "./package.json": "./package.json",
    ".": "./lib/version.cjs",
    "./unstable/ast": "./dist/ast/index.js",
    "./unstable/ast/scanner": "./dist/ast/scanner.js"
  }
}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"@typescript/typescript","version":"0.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"@typescript/typescript","version":"0.0.0","license":"Apache-2.0"}}}
JSON
cat > /workspace/lib/version.cjs <<'JS'
exports.version = "0.0.0";
exports.versionMajorMinor = "7.1";
JS
cat > /workspace/dist/ast/index.js <<'JS'
function numericEnum(names) {
  const value = {};
  names.forEach((name, index) => { value[name] = index; value[index] = name; });
  return value;
}
export const LanguageVariant = numericEnum(["Standard", "JSX"]);
export const ScriptTarget = numericEnum(["Latest"]);
export const SyntaxKind = numericEnum(["Unknown", "EndOfFile", "Identifier"]);
export const SpanMapKind = numericEnum(["Verbatim", "Atom", "Alias"]);
export const SpanMapFeature = numericEnum(["None", "All", "Hover", "Definition"]);
export const SpanMapFidelity = numericEnum(["None", "Exact", "Atom", "Approximate"]);
export class SpanMap {
  constructor(segments) { this.segments = segments; }
  static isExact() { return false; }
  static isSingleSegment() { return false; }
  static isNone() { return false; }
  virtualToOriginalPosition() { return { position: 0, fidelity: SpanMapFidelity.None }; }
  virtualToOriginalSpan() { return { range: { pos: 0, end: 0 }, fidelity: SpanMapFidelity.None }; }
  virtualToOriginalPositionForFeature(position) { return this.virtualToOriginalPosition(position); }
  virtualToOriginalSpanForFeature(range) { return this.virtualToOriginalSpan(range); }
  originalToVirtualPositions() { return []; }
  originalToVirtualSpans() { return []; }
}
JS
cat > /workspace/dist/ast/scanner.js <<'JS'
export function createScanner() {
  return {
    scan: () => 1,
    getTokenValue: () => undefined,
    getTokenText: () => "",
    getTokenFullStart: () => 0,
    getTokenStart: () => 0,
    getTokenEnd: () => 0,
    hasPrecedingLineBreak: () => false,
    hasUnicodeEscape: () => false,
    isUnterminated: () => false
  };
}
export const tokenToString = () => undefined;
export const stringToToken = () => undefined;
export const computeLineStarts = () => [0];
export const skipTrivia = (_text, position = 0) => position;
export const getShebang = () => undefined;
export const isIdentifierText = () => false;
export const getLeadingCommentRanges = () => undefined;
export const getTrailingCommentRanges = () => undefined;
JS
