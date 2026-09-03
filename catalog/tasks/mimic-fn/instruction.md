# Build `mimic-function`

## Project Description

Create an installable npm package named `mimic-function`, version `5.0.1`, from
an empty workspace. The package is an ESM utility that makes one function mimic
another function while keeping the destination function body and prototype
object.

## Supports

- Run on Node `24.19.0` with npm `11.17.0` on `linux/amd64` with glibc.
- `package.json` must set `name` to `mimic-function`, `version` to `5.0.1`,
  declare `type: "module"`, and expose the root with `types: "./index.d.ts"`
  and `default: "./index.js"`.
- Include `index.js`, `index.d.ts`, and a v3 `package-lock.json` consistent
  with the manifest. There are no runtime dependencies, native addons,
  workspaces, lifecycle scripts, or development dependencies required in the
  published package.
- A clean verifier must be able to run
  `npm ci --offline --ignore-scripts --no-audit --no-fund` followed by
  `npm pack --ignore-scripts`.
- Do not use network services, wall-clock timing, random state, or browser
  globals to determine behavior.

## Supports

### `mimicFunction(to, from, options?)`

Import the default export from `mimic-function`:

```js
import mimicFunction from 'mimic-function';

function source(value) {
  return value;
}

function wrapper(value) {
  return source(value);
}

mimicFunction(wrapper, source);
```

The function accepts two callable values. It mutates and returns `to`; it does
not replace the destination function body. For every own key of `from`, copy
the property descriptor to `to` except `length`, `prototype`, `arguments`, and
`caller`. The destination's pre-existing configurable properties remain in
place. Symbol keys must be handled in the same way as string keys.

The `name` and custom properties of `from` therefore become visible on `to`.
Inherited behavior is copied by setting the destination's prototype to the
source function's prototype when they differ. The function prototype object
itself is not copied.

The return type is the same callable type as `from` in the declaration file.
The operation is synchronous and returns the exact `to` object.

### `options.ignoreNonConfigurable`

`options` is optional. Its `ignoreNonConfigurable` boolean defaults to `false`.
When false, a conflicting non-configurable destination property raises the
ordinary `Object.defineProperty` error. When true, that property is left
unchanged and the remaining properties continue to be processed.

### Wrapped `toString()`

After a successful call, `to.toString()` and `String(to)` return the source's
captured `toString()` text prefixed with `/* Wrapped with <destination-name>() */`.
The patched method remains non-enumerable and its own `name` is `toString`.
Calling `Function.prototype.toString.call(to)` still exposes the original
destination function source. Repeated wrapping preserves the earlier wrapper
text in the captured source string.

## API Usage Guide

The package has one default export, `mimicFunction`, from `index.js`; its type
is declared in `index.d.ts`. The inputs are functions or classes, and the
result is the mutated destination callable. Property values may include
symbols and descriptors, but the function never performs I/O or network work.

## Implementation Notes

Keep the package self-contained and deterministic. Do not copy the upstream
implementation or tests. Preserve property enumerability, writability,
configurability, symbols, source prototype identity rules, and the distinction
between the destination function body and its displayed `toString()` value.
The verifier constructs functions and descriptors inside a candidate child
process; no callback or executable source crosses the trusted boundary.
