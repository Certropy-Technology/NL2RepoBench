# Build `zod`

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

## Project Description

Create an installable npm package named `zod`, version `4.4.3`, from an empty
workspace. It is an ESM-first schema construction and validation library. The
scored contract is a deterministic, JSON-compatible subset of the Zod v4
classic API: primitive schemas, string and number checks, arrays, objects,
unions, optional/nullable/default wrappers, `safeParse`, and stable issue
records.

This is a bounded rescope of the package, not a claim of complete upstream API
or test parity. Implement the behavior described below with your own source.
Do not copy a reference implementation or upstream tests into the repository.

## Natural Language Instruction

Create the ESM package from an empty `workspace/`. Implement the bounded Zod
classic namespace: primitive schemas, checks, collections, objects, unions,
wrappers, safe parsing, and stable issue records.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use name `zod`, version `4.4.3`, and `"type": "module"`.
  Its safe in-package root export must be importable as ESM.
- The root module must expose a named object export `z` and the default export
  must be the same object. The constructors listed in this specification are
  methods on that object.
- Declare no runtime dependencies, development dependencies, workspaces, or
  npm scripts. Include every runtime and declaration file selected by the root
  export plus a committed npm v3 lockfile consistent with `package.json`.
- A clean verifier must be able to run:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- Do not use lifecycle hooks, native addons, custom loaders, registry
  configuration, network access, browser globals, current time, or random
  state.

The package may expose more Zod-compatible API surface, but only the contract
below is scored.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── index.js
```

The root exports named `z` and the identical default namespace.

## JSON Boundary

The verifier owns a fixed adapter; it is not a CLI or export that your package
must implement. The adapter imports the package root in an unprivileged child,
constructs schemas only through the documented `z` methods, calls
`schema.safeParse(value)`, and returns JSON. Candidate code is never imported
into the trusted `node:test` process.

Each child receives one request and returns one response. Requests are at most
64 KiB, responses at most 256 KiB, schema depth at most 8, object shapes at
most 32 keys, arrays at most 128 items, enums at most 32 strings, and unions at
most 16 options. Inputs and successful outputs are recursively limited to JSON
null, booleans, finite numbers, strings, arrays, and plain objects.

The validation response is:

```js
// success
{ id: "request-id", success: true, data: parsedValue }

// failure
{
  id: "request-id",
  success: false,
  issues: [{ code: "issue_code", path: ["key", 0], message: "English message" }]
}
```

Issue order is schema traversal order. Paths contain only property-name strings
and array-index integers. The adapter projects exactly `code`, `path`, and
`message`; other internal issue fields and error object identity are outside
the boundary. The default English locale is used.

## API Usage Guide

### Root namespace and `safeParse`

**Import path and shape:**

```js
import zDefault, { z } from "zod";

zDefault === z; // true
const result = z.string().safeParse("value");
```

Every constructor returns a schema object with
`safeParse(input): {success: true, data} | {success: false, error}`. Parsing
must not mutate the input. On failure, `error.issues` is an ordered array whose
entries expose `code`, `path`, and `message` as described above.

### String schemas

```js
z.string()
z.string().min(count)
z.string().max(count)
z.string().length(count)
z.string().email()
z.string().trim()
z.string().toLowerCase()
```

`z.string()` accepts only strings. Counts are non-negative integers and count
Unicode code points. `min`, `max`, and `length` are inclusive constraints.
Checks and transformations run in chain order; for example,
`z.string().trim().toLowerCase()` maps `"  AbC  "` to `"abc"`. `email()`
accepts ordinary address forms such as `a@example.com` and rejects malformed
text.

### Number and boolean schemas

```js
z.number()
z.number().int()
z.number().min(value)
z.number().max(value)
z.number().positive()
z.number().nonnegative()
z.boolean()
```

`z.number()` accepts finite JavaScript numbers and does not coerce strings.
`min` and `max` are inclusive. `int()` rejects fractions, `positive()` requires
`> 0`, and `nonnegative()` requires `>= 0`. `z.boolean()` accepts only the two
boolean values and performs no string coercion.

### Literal and enum schemas

```js
z.literal(jsonScalar)
z.enum(["red", "green", "blue"])
```

A literal is JSON null, a boolean, a finite number, or a string and compares by
JavaScript scalar identity. An enum is a non-empty array of unique strings and
accepts exactly one listed value.

### Array schemas

```js
z.array(itemSchema)
z.array(itemSchema).min(count)
z.array(itemSchema).max(count)
z.array(itemSchema).length(count)
```

Arrays validate every element in index order and return the parsed element
array. Item failures include the numeric index in `path`. Length constraints
are inclusive; an exact-length failure reports that the array was expected to
have exactly that number of items.

### Object schemas

```js
z.object({ name: z.string() })
z.strictObject({ name: z.string() })
z.looseObject({ name: z.string() })
```

All three validate own enumerable properties from a fixed shape and return a
new plain object in shape-key order.

- `z.object` strips unrecognized keys.
- `z.strictObject` rejects unrecognized keys with `unrecognized_keys`.
- `z.looseObject` preserves unrecognized JSON values.

Nested failures prepend every containing property and array index to the issue
path. A required missing property is validated as JavaScript `undefined`, even
though `undefined` is not itself transported as a JSON value.

### Union and wrappers

```js
z.union([schemaA, schemaB])
schema.optional()
schema.nullable()
schema.default(jsonValue)
```

A union has at least two options, tries them in declaration order, and returns
the first successful parsed value. If no option succeeds, the projected root
issue has code `invalid_union`, an empty path, and message `Invalid input`.

`optional()` accepts `undefined`; in an object shape it permits an absent key
and leaves that key absent in the output. `nullable()` accepts `null` in
addition to the inner schema but does not make an object property optional.
`default(value)` substitutes the provided JSON value only when the input is
`undefined`, then returns the inner schema's parsed result.

### Scored issue messages

The default English messages below are part of the scored contract. Replace
the shown values with the actual expected type, received type, count, or key.

| Condition | Code | Message form |
| --- | --- | --- |
| Wrong primitive type | `invalid_type` | `Invalid input: expected string, received number` |
| Integer receives a fraction | `invalid_type` | `Invalid input: expected int, received number` |
| String below minimum | `too_small` | `Too small: expected string to have >=3 characters` |
| String above maximum | `too_big` | `Too big: expected string to have <=3 characters` |
| Invalid email | `invalid_format` | `Invalid email address` |
| Invalid enum member | `invalid_value` | `Invalid option: expected one of "red"|"green"|"blue"` |
| Array exact length is short | `too_small` | `Too small: expected array to have exactly 2 items` |
| Strict object extra key | `unrecognized_keys` | `Unrecognized key: "extra"` |
| Required nullable key absent | `invalid_type` | `Invalid input: expected string, received undefined` |
| No union option succeeds | `invalid_union` | `Invalid input` |

## Descriptor Mapping

For clarity, the verifier's allowlisted JSON descriptors map directly to the
public calls above:

```text
{type:"string", minLength?, maxLength?, length?, email?, trim?, toLowerCase?}
{type:"number", int?, min?, max?, positive?, nonnegative?}
{type:"boolean"}
{type:"literal", value}
{type:"enum", values:[...]}
{type:"array", item, minLength?, maxLength?, length?}
{type:"object", properties:{...}, unknownKeys?:"strip"|"strict"|"passthrough"}
{type:"union", options:[...]}
{type:"optional", inner}
{type:"nullable", inner}
{type:"default", inner, value}
```

String checks are chained in this order when their descriptor fields are
present: `min`, `max`, `length`, `email`, `trim`, `toLowerCase`. Number checks
use `int`, `min`, `max`, `positive`, `nonnegative`. Array checks use `min`,
`max`, `length`. The descriptor is only a deterministic verifier transport;
the package itself implements the ordinary Zod API calls.

## Examples

```js
import {z} from 'zod';
const User = z.object({name: z.string().min(1), age: z.number().int()});
User.safeParse({name: 'Ada', age: 37});
z.union([z.string(), z.number()]).safeParse(true);
```

Compose schemas with arrays, objects, literals, enums, unions, and wrappers.

## Error Handling and Boundary Conditions

Wrong primitive types, failed checks, invalid enum members, missing keys,
unknown-key policies, nested paths, union failures, `null`, and `undefined`
wrappers produce stable result shapes and issue paths.

## Implementation Notes

The frozen verifier contains 24 `node:test` leaves derived from the pinned v4
classic primitive, string, number, array, object, union, literal, enum,
optional, nullable, default, and error behavior. It does not run the upstream
Vitest development toolchain or score callbacks, asynchronous schemas,
promises, maps, sets, dates, BigInts, symbols, functions, cyclic values,
custom error maps, registries, codecs, JSON Schema conversion, locales other
than English, TypeScript inference, or package subpath exports. Those omissions
define the task boundary and are not claims about unscored behavior.
