#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{"name":"zod","version":"4.4.3","type":"module","exports":"./index.mjs"}
JSON
cat > package-lock.json <<'JSON'
{"name":"zod","version":"4.4.3","lockfileVersion":3,"requires":true,"packages":{"":{"name":"zod","version":"4.4.3","type":"module"}}}
JSON
cat > index.mjs <<'JS'
const schema = new Proxy({}, {
  get(_target, name) {
    if (name === "safeParse") return () => { while (true) {} };
    return () => schema;
  },
});
const constructor = () => schema;
export const z = Object.fromEntries([
  "string", "number", "boolean", "literal", "enum", "array",
  "object", "strictObject", "looseObject", "union",
].map((name) => [name, constructor]));
export default z;
JS
