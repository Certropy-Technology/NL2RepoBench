# parse-json API Inventory

Frozen package: `parse-json@8.3.0`, ESM root export at `index.js`, declarations
at `index.d.ts`.

Public runtime exports are the default `parseJson` function and the named
`JSONError` class. `parseJson` accepts JSON text, an optional JSON reviver, and
an optional filename; it returns the parsed value or throws `JSONError`.
`JSONError` exposes `name`, `message`, `fileName`, `codeFrame`, and
`rawCodeFrame`, and preserves the native parse exception as `cause`.

The source also depends on `@babel/code-frame` for source rendering and
`index-to-position` for UTF-16 error locations. Type-only `type-fest` metadata
is not included in the runtime closure.

Out of scope for the fixed JSON adapter: passing arbitrary callback functions
from the model, direct filesystem parsing, a CLI, color-terminal detection,
and non-JSON values returned by custom revivers.
