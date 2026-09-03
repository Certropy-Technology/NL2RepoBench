# Minimist Traceability

| Public behavior | Frozen upstream evidence | Private leaf coverage |
| --- | --- | ---: |
| CommonJS root export and empty input | `package.json`, `test/parse.js` | 2 |
| Long flags, `=`, negation, positionals | `test/long.js`, `test/parse.js` | 4 |
| Short flags, grouped flags, attached values | `test/short.js`, `test/kv_short.js`, `test/num.js` | 4 |
| Numeric conversion and declared strings | `test/parse.js`, `test/num.js` | 2 |
| Booleans, defaults, and `boolean: true` | `test/bool.js`, `test/default_bool.js`, `test/all_bool.js` | 3 |
| Aliases and defaults | `test/parse.js`, `test/dotted.js` | 2 |
| Dotted paths and trailing arguments | `test/dotted.js`, `test/parse_modified.js`, `test/stop_early.js` | 2 |
| Repeated values and prototype safety | `test/parse.js`, `test/proto.js` | 1 |

All 20 private leaves call the candidate only through a JSON-safe child Node
process. The trusted `node:test` process never imports the candidate package.
The upstream callback-valued `unknown` option is not in the JSON boundary and
is outside the scored contract.
