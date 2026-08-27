# Build `prettier`

## Project Description

Create an installable npm package named `prettier`, version `3.10.0-dev`, from
an empty workspace. This task is a deterministic, dependency-free formatter
slice for JavaScript, TypeScript, JSON, CSS, Markdown, YAML, HTML, and GraphQL.
It reproduces the root formatting behavior described below; configuration
files, filesystem discovery, plugins, a CLI, and the rest of the full upstream
project are outside the scored surface.

Implement the behavior in your own package files. This is repository
generation, not a request to retrieve the pinned upstream implementation or
private verifier assets.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64`.
- `package.json` must use name `prettier`, version `3.10.0-dev`, and
  `"type": "commonjs"`.
- The package root export must include at least this mapping (additional export
  conditions and subpaths are allowed):

  ```json
  {
    "exports": {
      ".": {
        "types": "./index.d.ts",
        "default": "./index.mjs"
      }
    }
  }
  ```

- Both entry files must exist. The runtime entry is ESM and must export
  `format`, `check`, `formatWithCursor`, and the string `version`. Additional
  exports are allowed. `version` must equal `"3.10.0-dev"`.
- Include a v3 `package-lock.json` that agrees with `package.json`. The package
  must declare no runtime dependencies, optional dependencies, peer
  dependencies, or npm workspaces. A clean verifier runs `npm ci`, `npm pack`,
  and installation from the packed tarball with npm's offline mode enabled.
- Do not add `preinstall`, `install`, `postinstall`, `prepare`, `prepublish`,
  `prepublishOnly`, `publish`, or `postpublish` scripts. Do not use native
  addons, custom loaders, registry configuration, package-manager caches, or
  network access.
- The installed package must work without a build step. Do not include hidden
  tests, graders, reward files, Oracle files, credentials, or private verifier
  material.

## API Usage Guide

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

## Implementation Notes

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
