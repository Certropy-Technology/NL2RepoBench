#!/usr/bin/env bash
set -euo pipefail

rm -rf /workspace/* /workspace/.[!.]* /workspace/..?*
mkdir -p /workspace/dev
cat > /workspace/package.json <<'JSON'
{"name":"micromark-util-character","version":"2.1.1","type":"module","sideEffects":false,"types":"./index.d.ts","exports":{"development":"./dev/index.js","default":"./index.js"},"dependencies":{"micromark-util-symbol":"2.0.1","micromark-util-types":"2.0.2"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"micromark-util-character","version":"2.1.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"micromark-util-character","version":"2.1.1","dependencies":{"micromark-util-symbol":"2.0.1","micromark-util-types":"2.0.2"}},"node_modules/micromark-util-symbol":{"version":"2.0.1","resolved":"https://registry.npmjs.org/micromark-util-symbol/-/micromark-util-symbol-2.0.1.tgz","integrity":"sha512-vs5t8Apaud9N28kgCrRUdEed4UJ+wWNvicHLPxCa9ENlYuAY31M0ETy5y1vA33YoNPDFTghEbnh6efaE8h4x0Q=="},"node_modules/micromark-util-types":{"version":"2.0.2","resolved":"https://registry.npmjs.org/micromark-util-types/-/micromark-util-types-2.0.2.tgz","integrity":"sha512-Yw0ECSpJoViF1qTU4DC6NwtC4aWGt1EkzaQB8KPPyCRR8z9TWeV0HbEFGTO+ZY1wB22zmxnJqhPyTpOVCpeHTA=="}}}
JSON
cat > /workspace/index.js <<'JS'
const hang = () => { while (true) {} }
const stub = () => { throw new Error('stub') }
export const asciiAlpha = hang
export const asciiAlphanumeric = stub
export const asciiAtext = stub
export const asciiControl = stub
export const asciiDigit = stub
export const asciiHexDigit = stub
export const asciiPunctuation = stub
export const markdownLineEnding = stub
export const markdownLineEndingOrSpace = stub
export const markdownSpace = stub
export const unicodePunctuation = stub
export const unicodeWhitespace = stub
JS
cp /workspace/index.js /workspace/dev/index.js
cat > /workspace/index.d.ts <<'TS'
export type Code = number | null
export declare const asciiAlpha: (code: Code) => boolean
export declare const asciiAlphanumeric: (code: Code) => boolean
export declare const asciiAtext: (code: Code) => boolean
export declare const asciiControl: (code: Code) => boolean
export declare const asciiDigit: (code: Code) => boolean
export declare const asciiHexDigit: (code: Code) => boolean
export declare const asciiPunctuation: (code: Code) => boolean
export declare const markdownLineEnding: (code: Code) => boolean
export declare const markdownLineEndingOrSpace: (code: Code) => boolean
export declare const markdownSpace: (code: Code) => boolean
export declare const unicodePunctuation: (code: Code) => boolean
export declare const unicodeWhitespace: (code: Code) => boolean
TS
