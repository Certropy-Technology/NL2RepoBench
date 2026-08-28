# Project Description

Build a complete installable npm package named `es-to-primitive`, version
`1.3.4`, from an empty workspace. The package implements the ECMAScript ES5
and ES2015 object-to-primitive abstract operations without using JavaScript's
implicit coercion as a substitute for the specified method-selection rules.

This is a repository-generation task. Implement the described public contract
with your own package files; do not fetch or copy a reference repository.

# Supports

- Node.js `24.19.0`, npm `11.17.0`, `linux/amd64`, and CommonJS semantics.
- `package.json` must identify `es-to-primitive` version `1.3.4`, set
  `"main": "index.js"`, and expose the package root plus `./es5`, `./es6`,
  and `./es2015` JavaScript modules.
- Provide matching declarations in `index.d.ts`, `es5.d.ts`, `es6.d.ts`, and
  `es2015.d.ts`. The root declaration uses `export = ToPrimitive` and exposes
  the `ES5`, deprecated `ES6`, and `ES2015` namespace properties.
- Commit an npm lockfile with `lockfileVersion: 3`. A clean verifier must be
  able to run this command without network access:

  ```bash
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- You may implement the package without runtime dependencies. If you use the
  upstream-compatible helpers, the only allowed direct runtime dependencies
  are exact `es-abstract-get@1.0.0`, `es-define-property@1.0.1`,
  `es-errors@1.3.0`, `is-callable@1.2.7`, `is-date-object@1.1.0`, and
  `is-symbol@1.1.1`. Their exact transitive closure is available offline.
- Do not use native addons, npm workspaces, registry configuration, custom
  loaders, generated downloads, or lifecycle scripts such as `preinstall`,
  `install`, `postinstall`, `prepare`, `prepack`, or `postpack`.
- Runtime behavior is synchronous, deterministic, and offline. The package has
  no CLI and must not access the filesystem, environment, clock, randomness,
  subprocesses, or network.

# API Usage Guide

## Root export `ToPrimitive(input, preferredType?)`

**Import path:** `require('es-to-primitive')`.

**TypeScript signature:**

```ts
declare function ToPrimitive(
    input: unknown,
    preferredType?: StringConstructor | NumberConstructor,
): ToPrimitive.primitive;
```

The root export is the ES2015 function. It is named `ToPrimitive`, has a
JavaScript `length` of `1`, and also exposes non-enumerable `ES5`, `ES6`, and
`ES2015` function properties. `ES6` is a deprecated alias of `ES2015`, and the
root function is the same function object as `ES2015`.

Primitive inputs are returned unchanged, preserving identity and edge cases:
`undefined`, `null`, booleans, strings, numbers including `NaN` and `-0`,
BigInts, and Symbols.

For an object, `preferredType === String` uses the string hint,
`preferredType === Number` uses the number hint, and an omitted or other value
uses the default hint. If a callable `input[Symbol.toPrimitive]` exists, call
it with exactly `"string"`, `"number"`, or `"default"`. Return its primitive
result. If it returns an object, throw `TypeError` with this exact message:

```text
unable to convert exotic object to primitive
```

A non-null, non-callable `Symbol.toPrimitive` value throws `TypeError`.
Exceptions raised by the exotic method propagate unchanged. A null or absent
exotic method falls back to ordinary conversion.

Ordinary conversion tries methods in this order:

- string hint: `toString`, then `valueOf`;
- number hint: `valueOf`, then `toString`;
- default hint: normally number order, but Date and boxed Symbol objects use
  string order.

Skip non-callable methods. Call each selected method with `this === input` and
return the first primitive result. If every callable method returns an object,
or no callable method exists, throw `TypeError` with this exact message:

```text
No default value
```

Examples:

```js
var toPrimitive = require('es-to-primitive');

toPrimitive({ valueOf: function () { return 3; } });
// 3

toPrimitive({
  toString: function () { return 'record'; },
  valueOf: function () { return 7; }
}, String);
// 'record'

var value = {};
value[Symbol.toPrimitive] = function (hint) { return hint; };
toPrimitive(value);
// 'default'
```

## `ES2015(input, preferredType?)`

**Import paths:** `require('es-to-primitive/es2015')` and the root
`ToPrimitive.ES2015` property.

**Signature:** the same runtime signature and behavior as the root function.
The TypeScript result union is `null | undefined | string | number | boolean |
symbol`. Runtime primitive preservation also includes BigInt on supported Node
versions. A boxed Symbol converts back to its primitive Symbol for every hint.

## `ES6(input, preferredType?)`

**Import paths:** `require('es-to-primitive/es6')` and the root
`ToPrimitive.ES6` property.

This deprecated compatibility name is an alias of `ES2015` and has the same
runtime behavior and declaration shape.

## `ES5(input, preferredType?)`

**Import paths:** `require('es-to-primitive/es5')` and the root
`ToPrimitive.ES5` property.

**TypeScript signature:**

```ts
declare function ToPrimitive(
    input: ToPrimitive.unknownES5,
    preferredType?: StringConstructor | NumberConstructor,
): ToPrimitive.primitiveES5;
```

The ES5 variant preserves ES5 primitives and uses the same ordinary method
ordering: String selects `toString` first, Number selects `valueOf` first, and
an omitted hint selects String for Date objects and Number otherwise. It does
not consult `Symbol.toPrimitive`. Supplying a preferred type other than the
`String` or `Number` constructors throws `TypeError` with the exact message
`invalid [[DefaultValue]] hint supplied`.

# Implementation Notes

Do not call `String(input)`, `Number(input)`, template interpolation, or another
implicit coercion operation as the implementation of object conversion: those
paths cannot reproduce ES5 selection or the required method order. Primitive
short-circuiting must happen before object method lookup. Treat a method as
usable only when it is callable, preserve thrown exception objects, and stop
immediately after the first primitive result.
