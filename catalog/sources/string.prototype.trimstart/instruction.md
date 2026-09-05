# Project Description

The package root is a callable function named `trim`. It trims ECMAScript
whitespace from the beginning of a value after ordinary JavaScript object
coercion. The function is deterministic and must not read the filesystem, use
the network, inspect a terminal, or depend on time or randomness.

## Natural Language Instruction

Create `string.prototype.trimstart` from an empty workspace as a complete installable node project. Implement
the public operations, data or state behavior, input validation, deterministic ordering, and
error contracts documented below. Keep package metadata, root exports, module imports, and any
subpath entry points consistent across files. Implement the behavior rather than hard-coding the
examples, and do not retrieve or copy a reference implementation.

The finished repository must install from its root, expose every documented API family, preserve
the specified side effects and resource lifecycle, and remain usable in a fresh process.

## Supports

- Package/distribution name: `string.prototype.trimstart`. Primary import or package entry: `string.prototype.trimstart`.
- Node.js 24.19.0 and npm 11.17.0 on Linux amd64.
- Install from `workspace/` using `npm ci --offline --ignore-scripts --no-audit --no-fund`.
- Declared dependency closure: call-bind, define-properties, es-object-atoms. Standard-library modules are not dependencies.
- Build requirements are supplied before execution; do not add undeclared dependencies,
  registry overrides, download hooks, or source-fetch steps.
- Agent, candidate, verifier, Oracle, and controls use `network_mode=no-network`. Runtime access
  to GitHub, PyPI, npm, the Go proxy, DNS, and external services is forbidden.
- The declared test framework is `node:test`. A fixed collection
  contains `31` cases when that value is frozen in metadata;
  test implementation details are not part of the package surface.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── implementation.js
├── polyfill.js
└── shim.js
```

This is the required public project shape. Additional implementation modules are allowed only
when they support the documented API; evaluation, source-fetch, and private runtime files are
not agent-owned project files.

## API Usage Guide

### `trim(value) => string`

Import the root export with CommonJS:

```js
const trim = require('string.prototype.trimstart');
trim(' \t\nhello'); // 'hello'
```

`value` is any non-nullish JavaScript value. The function applies ordinary
JavaScript string coercion, then removes whitespace from the beginning only.
Trailing and internal whitespace remain. The ECMAScript whitespace set is
ASCII tabs/control whitespace, space, no-break space, U+1680, U+2000 through
U+200A, U+2028, U+2029, U+202F, U+205F, U+3000, and BOM U+FEFF. Zero-width
space U+200B, Mongolian vowel separator U+180E on Node 24, U+0085, and U+FFFE
remain in the result. The operation returns a string and does not mutate
caller-owned values.

### Helper properties

- `trim.implementation`: a callable implementation of the trimming behavior.
- `trim.getPolyfill()`: returns a callable native `trimStart`/`trimLeft` method
  when the host method is conforming, otherwise the package implementation.
- `trim.shim()`: installs the selected polyfill as `String.prototype.trimStart`
  when required and returns the selected callable.

The three helper properties are non-enumerable. The root callable has name
`trim` and a one-argument function length.

### Errors and boundary

Calling the root function with `null` or with no argument throws a `TypeError`
because the receiver must be object-coercible. Other JSON values such as
numbers, booleans, arrays, and plain objects follow ordinary JavaScript
ToString behavior. Do not add validation for those values.

## Implementation Notes

- Keep the package root importable without a build step after npm installation.
- The scored verifier uses a fresh bounded unprivileged Node child for each
  request and passes JSON values only.
- The frozen denominator is 31 deterministic `node:test` leaves covering
  package identity, helper shape, leading whitespace boundaries, Unicode
  exclusions, coercion, nullish errors, shim behavior, large inputs,
  non-mutation, and determinism.
- Upstream Tape/NYC/ESLint development tooling, browser compatibility, and
  audit/network post-test behavior are outside this production boundary.

Use the public language semantics described by each API family. Keep repeated calls deterministic
unless state mutation is explicitly part of the contract. Public re-exports and declarations must
match runtime behavior, and installation must not rely on a repository checkout or network access.

## Examples

The API-specific examples above are normative demonstrations of ordinary behavior. These four
local snippets also provide ordinary and boundary-oriented calls without external services:

```javascript
const trim = require('string.prototype.trimstart');
trim(' \t\nhello'); // 'hello'
```

```javascript
const api = require('string.prototype.trimstart');
console.log(typeof api);
```

```javascript
import api from 'string.prototype.trimstart';
console.log(typeof api);
```

```javascript
const api = require('string.prototype.trimstart');
console.log(typeof api);
```

## Error Handling and Boundary Conditions

Empty values, malformed values, unsupported types, exhausted inputs, invalid options, and missing
local resources must follow the API-specific contracts above. Preserve documented exception types
and messages where they are stated. Do not silently coerce an unsupported value merely to produce
a result, and do not mutate caller-owned data unless the relevant API explicitly promises it.

All filesystem, process, terminal, clock, randomness, and service interactions are forbidden unless
the API guide explicitly includes that local behavior. Even for an API that models remote or async
work, evaluation must remain bounded, deterministic, and disconnected from public networks.
