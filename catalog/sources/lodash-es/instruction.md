# Project Description

Build an installable npm package named `lodash-es`, version `4.18.1`, from an
empty workspace. It is an ESM utility library implementing a deterministic,
JSON-safe slice of Lodash collection, object, string, comparison, and numeric
helpers. Browser builds, FP modules, and the complete upstream distribution
are outside scope.

# Natural Language Instruction

Create the `lodash-es` project from an empty `workspace/`. Expose every named
function listed below from the ESM root and also expose a default object with
the same functions. Implement the bounded JSON behavior, property-name/path
and partial-object shorthands, stable ordering, string conversion, and
non-mutating results described in this specification.

Do not copy private tests or a reference implementation. Do not add CommonJS
loaders, bundlers, native addons, lifecycle scripts, runtime dependencies,
CLI behavior, or registry access.

# Supports

- Use Node.js `24.19.0` with npm `11.17.0` on Linux x86-64.
- `package.json` must declare `name: "lodash-es"`, `version: "4.18.1"`,
  `type: "module"`, and root entry `index.js`.
- Commit an npm v3 `package-lock.json`; declare no runtime or development
  dependencies. Offline installation must support
  `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Agent, candidate, verifier, Oracle, and controls run with NoNetwork. Runtime
  behavior must not depend on time, random state, environment variables,
  external files, or network services.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

`package.json` declares the ESM root and package identity. `index.js` contains
the named exports and the default object containing the same named functions.
The lockfile describes the empty dependency closure. No tests, browser build,
FP build, loader, or private verifier file is part of the agent-owned project.

# API Usage Guide

Arguments and ordinary results are JSON-compatible values. A documented
`undefined` result is represented as an absent value at the caller boundary.
Functions must be deterministic and must not mutate supplied inputs.

## Array and collection helpers

- `chunk(array, size = 1) => any[][]` splits consecutive chunks; a non-positive
  size returns `[]`. `compact(array) => any[]` removes falsey values.
- `concat(value, ...values) => any[]` flattens array arguments one level.
  `difference(array, ...values) => any[]` removes values in later arrays while
  preserving first-array order. `drop`, `dropRight`, `flatten`, `flattenDeep`,
  `head`, `last`, `uniq`, and `zip` have their standard documented one-level,
  recursive, endpoint, duplicate, and index-row behavior.
- `map(collection, iteratee) => any[]` supports property-name and pair
  shorthands such as `"name"` and `["active", true]`. `filter(collection,
  predicate)` and `find(collection, predicate)` support partial object
  matching. `groupBy` and `keyBy` support property paths and Lodash key
  coercion; `keyBy` lets later entries replace earlier entries.
- `get(object, path, defaultValue)`, `has(object, path)`, `isEqual(left,
  right)`, and `cloneDeep(value)` support dotted/array JSON paths, own-path
  checks, recursive key-order-independent comparison, and isolated JSON copies.
- `sumBy(collection, iteratee)` and `maxBy(collection, iteratee)` support
  property-name iteratees. `orderBy(collection, iteratees, orders)` supports
  property-name iteratees and stable `"asc"`/`"desc"` orders.

## String, conversion, and predicates

`camelCase(string)`, `kebabCase(string)`, and `startCase(string)` normalize
ordinary ASCII and Unicode-letter word boundaries. `toString(value)` uses
Lodash coercion for JSON-compatible values; finite numbers retain ordinary
decimal spelling. `toNumber(value)` converts JSON-compatible numbers and
numeric strings. The default object aliases all named functions exactly.

# Implementation Notes

- Keep the ESM root self-contained and deterministic. Only the root named
  exports and their default aliases are scored; extra files are unnecessary.
- Preserve input order for collection operations and do not mutate arrays or
  objects. Use null for missing JSON values in `zip` within this bounded
  contract.
- General callbacks, executable values, non-JSON values, symbols, wrapper
  chains, templates, browser/UMD builds, FP helpers, CLI behavior, and
  per-method module paths are excluded.
- Do not depend on CommonJS loaders, TypeScript, native addons, lifecycle
  scripts, registry settings, network, time, randomness, or outside files.

# Examples

```js
import _, {chunk, map} from 'lodash-es';

chunk([1, 2, 3], 2); // [[1, 2], [3]]
map([{name: 'Ada'}], 'name'); // ['Ada']
_.camelCase('Hello world'); // 'helloWorld'
```

```js
import {get, orderBy, cloneDeep} from 'lodash-es';

get({user: {id: 3}}, 'user.id'); // 3
orderBy([{n: 2}, {n: 1}], ['n'], ['asc']); // [{n: 1}, {n: 2}]
const copy = cloneDeep({items: [1]});
```

# Error Handling and Boundary Conditions

- Empty collections return empty arrays or `undefined` as documented. Missing
  paths return the supplied default for `get` and false for `has`.
- `zip` uses bounded nulls for missing positions. `orderBy` remains stable for
  equal keys, and `uniq` retains the first occurrence.
- Unicode-letter strings must retain deterministic word boundaries; finite
  numeric conversions must not depend on locale.
- Unsupported callbacks, symbols, non-JSON values, browser globals, files,
  services, current time, randomness, environment, and network are outside the
  contract and must not affect scored results.
