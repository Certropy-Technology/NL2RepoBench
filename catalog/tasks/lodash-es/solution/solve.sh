#!/usr/bin/env bash
set -euo pipefail

root=/workspace
mkdir -p "$root"
printf '%s  %s\n' \
  '9bd765def21a6704a6d7e54ecf76004811ba7df19b387b60e04740785794e376' \
  '/solution/lodash.cjs' | sha256sum --check --strict
cp /solution/lodash.cjs "$root/lodash.cjs"
cat > "$root/package.json" <<'JSON'
{"name":"lodash-es","version":"4.18.1","type":"module","exports":{".":"./index.js","./*.js":"./*.js"},"files":["index.js","*.js","*.cjs","package.json","package-lock.json"],"scripts":{}}
JSON
cat > "$root/package-lock.json" <<'JSON'
{"name":"lodash-es","version":"4.18.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"lodash-es","version":"4.18.1","license":"MIT","type":"module","dependencies":{},"devDependencies":{}}}}
JSON
cat > "$root/index.js" <<'JS'
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const lodash = require("./lodash.cjs");
const names = ["chunk", "compact", "concat", "difference", "drop", "dropRight", "flatten", "flattenDeep", "head", "last", "map", "filter", "find", "groupBy", "keyBy", "get", "has", "isEqual", "cloneDeep", "sumBy", "maxBy", "orderBy", "uniq", "zip", "camelCase", "kebabCase", "startCase", "toString", "toNumber"];
export const chunk = lodash.chunk;
export const compact = lodash.compact;
export const concat = lodash.concat;
export const difference = lodash.difference;
export const drop = lodash.drop;
export const dropRight = lodash.dropRight;
export const flatten = lodash.flatten;
export const flattenDeep = lodash.flattenDeep;
export const head = lodash.head;
export const last = lodash.last;
export const map = lodash.map;
export const filter = lodash.filter;
export const find = lodash.find;
export const groupBy = lodash.groupBy;
export const keyBy = lodash.keyBy;
export const get = lodash.get;
export const has = lodash.has;
export const isEqual = lodash.isEqual;
export const cloneDeep = lodash.cloneDeep;
export const sumBy = lodash.sumBy;
export const maxBy = lodash.maxBy;
export const orderBy = lodash.orderBy;
export const uniq = lodash.uniq;
export const zip = lodash.zip;
export const camelCase = lodash.camelCase;
export const kebabCase = lodash.kebabCase;
export const startCase = lodash.startCase;
export const toString = lodash.toString;
export const toNumber = lodash.toNumber;
export default Object.fromEntries(names.map((name) => [name, lodash[name]]));
JS
for name in chunk compact concat difference drop dropRight flatten flattenDeep head last map filter find groupBy keyBy get has isEqual cloneDeep sumBy maxBy orderBy uniq zip camelCase kebabCase startCase toString toNumber; do
  printf 'export { %s as default, %s } from "./index.js";\n' "$name" "$name" > "$root/$name.js"
done
