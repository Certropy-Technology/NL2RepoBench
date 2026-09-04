# `vfile-message` Traceability

| Public specification | Private leaves | Frozen authority |
| --- | --- | --- |
| exact ESM package surface | named class, no default, Error inheritance, callable constructor | `index.js`, `package.json`, upstream API test |
| basic reason and fields | empty/nonempty reason, name, file, fatal, stack, `toString` | `lib/index.js`, upstream API test |
| points and positions | line/column, point/position place, formatted names | `lib/index.js`, `unist-util-stringify-position` |
| node overload | node position, ancestors, missing position, no mutation | `lib/index.js`, upstream API test |
| origins | rule-only, source/rule split, legacy third argument, explicit option precedence | `lib/index.js`, upstream API test |
| causes | Error message, cause identity summary, preserved first stack line, cause plus origin | `lib/index.js`, upstream API test |
| options and metadata | source/rule/place/ancestors and well-known undefined fields | `lib/index.js`, README API |
| deterministic boundaries | repeated construction, empty reason formatting | class state contract |
