#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "is-string",
  "version": "1.1.1",
  "description": "Determine whether a value is a string",
  "main": "index.js",
  "types": "index.d.ts",
  "license": "MIT",
  "engines": {"node": ">=0.4"}
}
JSON

cat > package-lock.json <<'JSON'
{
  "name": "is-string",
  "version": "1.1.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "is-string",
      "version": "1.1.1",
      "license": "MIT",
      "engines": {"node": ">=0.4"}
    }
  }
}
JSON

cat > index.js <<'JS'
'use strict';

var $valueOf = String.prototype.valueOf;
var $toString = Object.prototype.toString;
var strClass = '[object String]';
var hasToStringTag = typeof Symbol === 'function' && Symbol.toStringTag;

module.exports = function isString(value) {
  if (typeof value === 'string') {
    return true;
  }
  if (!value || typeof value !== 'object') {
    return false;
  }
  if (hasToStringTag) {
    try {
      $valueOf.call(value);
      return true;
    } catch (e) {
      return false;
    }
  }
  return $toString.call(value) === strClass;
};
JS

cat > index.d.ts <<'TS'
declare function isString(value: unknown): value is string | String;

export = isString;
TS

cat > LICENSE <<'TXT'
The MIT License (MIT)

Copyright (c) 2015 Jordan Harband

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
TXT

npm ci --offline --ignore-scripts --no-audit --no-fund
