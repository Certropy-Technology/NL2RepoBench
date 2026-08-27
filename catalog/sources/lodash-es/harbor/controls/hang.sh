#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace
cat > /workspace/package.json <<'JSON'
{"name":"lodash-es","version":"4.18.1","type":"module","exports":{".":"./index.js"}}
JSON
cat > /workspace/package-lock.json <<'JSON'
{"name":"lodash-es","version":"4.18.1","lockfileVersion":3,"requires":true,"packages":{"":{"name":"lodash-es","version":"4.18.1","type":"module"}}}
JSON
cat > /workspace/index.js <<'JS'
const hang = () => { while (true) {} };
export const chunk = hang;
export const compact = hang;
export const concat = hang;
export const difference = hang;
export const drop = hang;
export const dropRight = hang;
export const flatten = hang;
export const flattenDeep = hang;
export const head = hang;
export const last = hang;
export const map = hang;
export const filter = hang;
export const find = hang;
export const groupBy = hang;
export const keyBy = hang;
export const get = hang;
export const has = hang;
export const isEqual = hang;
export const cloneDeep = hang;
export const sumBy = hang;
export const maxBy = hang;
export const orderBy = hang;
export const uniq = hang;
export const zip = hang;
export const camelCase = hang;
export const kebabCase = hang;
export const startCase = hang;
export const toString = hang;
export const toNumber = hang;
export default {chunk: hang};
JS
