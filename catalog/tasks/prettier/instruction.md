# prettier

## Project Description

Build an installable `prettier` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution/package identity: `prettier`; root module entry is the package entry documented below.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `format`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `check`: preserve the documented object or module behavior, including state and side effects.
3. `formatWithCursor`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Errors and JSON boundary`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- Node.js 24.19.0 with npm 11.17.0.
- Distribution/package identity: `prettier`; root module entry is the package entry documented below.
- Install from the workspace with `npm install --offline` using the declared lockfile.
- No third-party runtime package is declared by the local task metadata; standard-library support is sufficient unless the API section says otherwise.
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

All three functions are asynchronous and stateless. They accept JSON-safe
arguments and must not read files, environment configuration, clocks, random
state, or network services.

### `format`

**Import path:** named export from the package root.

**Signature:**

```ts
format(text: string, options: FormatOptions): Promise<string>
```

Every successful result ends with exactly one line feed. Preserve source
ordering and literal values; only normalize layout, spaces, quotes, punctuation,
and wrapping. Supported parser names are `babel`, `typescript`, `json`, `css`,
`markdown`, `yaml`, `html`, and `graphql`.

The supported options are:

```ts
interface FormatOptions {
  parser: "babel" | "typescript" | "json" | "css" |
          "markdown" | "yaml" | "html" | "graphql";
  printWidth?: number;                 // default 80
  semi?: boolean;                      // default true
  singleQuote?: boolean;               // default false
  arrowParens?: "always" | "avoid";   // default "always"
  useTabs?: boolean;                   // default false
  proseWrap?: "always" | "never" | "preserve"; // default "preserve"
  cursorOffset?: number;               // formatWithCursor only
}
```

Parser behavior for this production slice:

- `babel`: normalize spaces around `=`, `=>`, binary operators, object colons,
  and comma separators. Put spaces inside nonempty object braces, retain compact
  arrays when they fit, and add the configured semicolon. `singleQuote: true`
  rewrites simple double-quoted strings without escapes. `arrowParens: "avoid"`
  removes parentheses around one simple parameter. When a function call exceeds
  `printWidth`, put one argument on each two-space-indented line and keep a final
  comma.
- `typescript`: apply the same punctuation rules and normalize an object type
  such as `type User={name:string;age?:number};` to
  `type User = { name: string; age?: number };`.
- `json`: parse a JSON value without reordering object properties. Keep a short
  object on one line with spaces inside braces. When it exceeds `printWidth`,
  print one property/item per line with two spaces, or tabs when `useTabs` is
  true, and never add trailing commas.
- `css`: put declaration blocks and nested at-rules on separate lines with
  two-space indentation, one declaration per line, a space after each colon,
  a semicolon after each declaration, collapsed internal value whitespace, and
  a space between an at-rule name and its parenthesized condition.
- `markdown`: collapse repeated spaces in prose, normalize list markers to
  `- `, and retain blank lines between blocks. With `proseWrap: "always"`, wrap
  prose greedily without exceeding `printWidth` when words themselves fit.
- `yaml`: normalize sequence markers to two-space indentation and add spaces
  inside a flow mapping and after its commas and colons.
- `html`: preserve inline phrasing content on one line when it fits and append
  the final line feed.
- `graphql`: add spaces after argument/type colons and expand operation and
  selection-set braces with two-space nesting, one selected field per line.

Representative exact results:

```js
await format("const x={a:1,b:[2,3]}", { parser: "babel" });
// "const x = { a: 1, b: [2, 3] };\n"

await format('{"b":2,"a":[1,2]}', { parser: "json" });
// '{ "b": 2, "a": [1, 2] }\n'

await format("type User={name:string;age?:number};", {
  parser: "typescript"
});
// "type User = { name: string; age?: number };\n"

await format("query User($id:ID!){user(id:$id){id name email}}", {
  parser: "graphql"
});
// "query User($id: ID!) {\n  user(id: $id) {\n    id\n    name\n    email\n  }\n}\n"
```

Calling `format` again on a successful result with the same options must return
the same string.

### `check`

**Signature:**

```ts
check(text: string, options: FormatOptions): Promise<boolean>
```

Return whether `text` is byte-for-byte equal to `await format(text, options)`.
For example, `check("const x = 1;\n", {parser: "babel"})` is `true`, while the
same call with `"const x=1"` is `false`.

### `formatWithCursor`

**Signature:**

```ts
formatWithCursor(
  text: string,
  options: FormatOptions & {cursorOffset: number}
): Promise<{formatted: string; cursorOffset: number; comments: []}>
```

Return the same text as `format` in `formatted`. Translate `cursorOffset` by
the formatting edits before the cursor, preserving the cursor's logical source
position. The bounded slice does not expose parsed comments, so `comments` is
an empty array. Exact example:

```js
await formatWithCursor("const value={alpha:1,beta:2}", {
  parser: "babel",
  cursorOffset: 15
});
// {
//   formatted: "const value = { alpha: 1, beta: 2 };\n",
//   cursorOffset: 18,
//   comments: []
// }
```

### Errors and JSON boundary

- If `format` is called without `options.parser`, reject with an error whose
  class name is `UndefinedParserError` and whose message is exactly
  `No parser and no file path given, couldn't infer a parser.`
- For an unsupported parser name, reject with class name `ConfigError` and the
  exact message `Couldn't resolve parser "<name>".`
- The verifier sends strings and plain JSON option objects. Functions, symbols,
  BigInts, cyclic values, custom prototypes, file handles, and executable text
  are outside the boundary.
- The verifier-owned adapter invokes only the installed package root in a
  bounded subprocess. It is not a candidate CLI requirement.


- Keep parser dispatch deterministic and isolate parser-specific formatting
  rules. A small tokenizer/state machine is preferable to substitutions that
  alter quoted strings or nested delimiters.
- Handle LF output explicitly. Inputs in the scored slice are finite UTF-8
  strings and use no external plugins.
- Public declarations should describe the signatures above. No CLI behavior,
  config-file lookup, plugin loading, filesystem traversal, or browser bundle is
  scored or required.
- The fixed private denominator is 20 `node:test` leaves: package/API shape,
  the eight parser families, formatting options and wrapping, idempotence,
  `check`, cursor translation, and both parser error contracts.

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
{
    "exports": {
      ".": {
        "types": "./index.d.ts",
        "default": "./index.mjs"
      }
    }
  }
```

### Example 2: ordinary usage
```text
format(text: string, options: FormatOptions): Promise<string>
```

### Example 3: boundary or error behavior
```text
interface FormatOptions {
  parser: "babel" | "typescript" | "json" | "css" |
          "markdown" | "yaml" | "html" | "graphql";
  printWidth?: number;                 // default 80
  semi?: boolean;                      // default true
  singleQuote?: boolean;               // default false
  arrowParens?: "always" | "avoid";   // default "always"
  useTabs?: boolean;                   // default false
  proseWrap?: "always" | "never" | "preserve"; // default "preserve"
  cursorOffset?: number;               // formatWithCursor only
}
```

### Example 4: boundary or error behavior
```text
await format("const x={a:1,b:[2,3]}", { parser: "babel" });
// "const x = { a: 1, b: [2, 3] };\n"

await format('{"b":2,"a":[1,2]}', { parser: "json" });
// '{ "b": 2, "a": [1, 2] }\n'

await format("type User={name:string;age?:number};", {
  parser: "typescript"
});
// "type User = { name: string; age?: number };\n"

await format("query User($id:ID!){user(id:$id){id name email}}", {
  parser: "graphql"
});
// "query User($id: ID!) {\n  user(id: $id) {\n    id\n    name\n    email\n  }\n}\n"
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
