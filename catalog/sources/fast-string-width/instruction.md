# Build `fast-string-width`

## Project Description

Create a complete installable npm package named `fast-string-width`, version
`3.0.2`, from an empty workspace. The package exports one ESM default
function that calculates the visual terminal width of a string without
truncating it. Reproduce the observable behavior of the pinned
`fabiospampinato/fast-string-width` revision, not a generic approximation.

## Natural Language Instruction

Create the `fast-string-width` package from an empty `workspace/`. Implement
the default root ESM function and its five numeric width options while
preserving ANSI stripping, control and tab widths, combining marks, emoji
sequences, East Asian width, deterministic floating-point totals, and the
non-truncating behavior. Use the declared lower-level dependency rather than
replacing the calculation with JavaScript string length.

## Supports

- Node `24.19.0`, npm `11.17.0`, Linux amd64 with glibc.
- ESM package semantics (`"type": "module"`). The package root must expose
  `dist/index.js` through `exports` and `main`, and its default export must be
  callable as `import fastStringWidth from 'fast-string-width'`.
- A committed npm v3 lockfile that makes the package installable in the
  verifier with:

  ```text
  npm ci --offline --ignore-scripts --no-audit --no-fund
  ```

- The runtime dependency `fast-string-truncated-width` must be declared and
  resolved by the lockfile. Use the exact lock-resolved version selected by
  the supplied offline closure; do not use git, file, workspace, native-addon,
  or network dependencies.
- The submitted package must be packable with `npm pack --ignore-scripts`.
  Do not rely on a prepare hook, a globally installed compiler, the current
  working directory, or a network service at evaluation time.

## Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
└── dist/
    ├── index.js
    └── index.d.ts
```

The package root resolves to `dist/index.js` through both `exports` and `main`.
The lockfile must describe the exact `fast-string-truncated-width` runtime
dependency closure. No CLI, server, source checkout, lifecycle hook, or
runtime download is required.

## API Usage Guide

### Default export

**Import path:** the package root default export.

```js
import fastStringWidth from 'fast-string-width';
fastStringWidth('hello'); // 5
```

**Signature:**

```js
fastStringWidth(input, options?)
```

`input` is a string. The return value is a finite number giving the number of
terminal columns occupied by the string. The function does not mutate its
input and is deterministic for the same input and options. A call with no
options is equivalent to the default width configuration.

`options` is an object with these optional numeric fields:

| Field | Default | Meaning |
| --- | ---: | --- |
| `controlWidth` | `0` | Width assigned to C0/C1 control characters such as `\n`. |
| `tabWidth` | `8` | Width assigned to each tab character. |
| `emojiWidth` | `2` | Width assigned to one recognized emoji sequence. |
| `regularWidth` | `1` | Width assigned to ordinary printable characters. |
| `wideWidth` | `2` | Width assigned to wide non-CJK/non-emoji characters and CJK blocks. |

The implementation also recognizes terminal ANSI escape sequences and OSC 8
hyperlink sequences; these contribute zero columns. Combining marks do not add
columns. Recognized emoji sequences (including joined family/worker sequences,
skin-tone modifiers, flags, and keycaps) contribute one `emojiWidth`, rather
than one width per code point. East Asian wide/full-width characters contribute
two columns with the default settings. Ambiguous characters use
`regularWidth`, as in the lower-level dependency.

Examples:

```js
fastStringWidth('hello'); // 5
fastStringWidth('\x1b[31mhello\x1b[0m'); // 5
fastStringWidth('👨‍👩‍👧‍👦'); // 2
fastStringWidth('👶👶🏽', {emojiWidth: 1.5}); // 3
fastStringWidth('漢字', {wideWidth: 1}); // 2
fastStringWidth('\ta', {tabWidth: 4}); // 5
```

The wrapper is intentionally non-truncating: fields named `limit`, `ellipsis`,
or `ellipsisWidth` are not part of this function's options and must not change
the result merely because they are present in an otherwise accepted object.

## Implementation Notes

- Keep the public entry point at `dist/index.js`; a declaration file at
  `dist/index.d.ts` is recommended but is not required by the JSON calls.
- Use a lifecycle-free package for evaluation. Development-only TypeScript
  sources and compilers are optional, but `npm ci --ignore-scripts` must leave
  the packed runtime usable.
- Preserve the lower-level dependency's handling of ANSI/control/tab/emoji/
  wide/combining characters and the five width options. Do not replace the
  dependency with `String.length`, `Math.random`, or a locale-dependent API.
- Do not include hidden tests, verifier code, Oracle files, reward files,
  credentials, private dependency cache bytes, or generated Harbor assets in
  the candidate repository.

## Examples

```js
import fastStringWidth from 'fast-string-width';

fastStringWidth('plain'); // 5
fastStringWidth('\x1b[31mplain\x1b[0m'); // 5
```

```js
fastStringWidth('A\t漢', {tabWidth: 4, wideWidth: 1}); // 6
fastStringWidth('👩‍💻', {emojiWidth: 1}); // 1
```

```js
const options = {regularWidth: 3, limit: 1, ellipsis: '...'};
fastStringWidth('ab', options); // 6; no truncation is performed
```

## Error Handling and Boundary Conditions

The scored boundary supplies strings and JSON objects containing finite numeric
options. Preserve the normal JavaScript `TypeError` behavior for a non-string
input rather than silently coercing arbitrary values. Do not add a CLI, server,
custom JSON protocol, or extra package export to implement the task.
