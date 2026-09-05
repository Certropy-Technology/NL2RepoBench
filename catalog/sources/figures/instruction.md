# Project Description

Build an installable ESM npm package named `figures`, version `6.1.0`, from an
empty workspace. The package exposes a deterministic catalogue of terminal
symbols and ASCII-compatible replacements for symbols that are not supported
by an older terminal.

# Natural Language Instruction

Create the installable ESM `figures` package from an empty workspace. Export
the default terminal-selected symbol namespace and the named main, fallback,
and replacement tables exactly as specified below.

# Supports or Environment Configuration

- Use Node.js 24.19.0 and npm 11.17.0 with the exact package metadata and
  offline dependency closure in `task.toml`.
- Values are deterministic strings; no runtime network access is permitted.
- Agent, candidate, verifier, Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── package.json
├── package-lock.json
├── index.js
├── index.d.ts
└── license
```

# API Usage Guide

The API Usage Guide below is authoritative for symbol names, values, table
shapes, replacement behavior, and default export identity.

# Implementation Notes

Keep all symbol tables stable and ensure the default namespace has exactly the
documented property names.

# Examples

```js
import figures, {mainSymbols} from 'figures';
figures.tick;
```

```js
mainSymbols.arrowUp;
```

# Error Handling and Boundary Conditions

```js
Object.keys(figures).sort();
```

```js
figures.cross;
```

# Supports

- Node.js `24.19.0`, npm `11.17.0`, Linux amd64, and ESM package semantics.
- The package name and version must be `figures` and `6.1.0`.
- The package root must export the default namespace plus the named exports
  `mainSymbols`, `fallbackSymbols`, and `replaceSymbols`.
- The default namespace contains the same symbol names as `mainSymbols` and
  `fallbackSymbols`, with no extra public members. Symbol values are strings.
- `mainSymbols` uses the Unicode values and `fallbackSymbols` uses the ASCII or
  conservative terminal values described below. Values shared by both tables
  are unchanged in both tables.
- `replaceSymbols(string, options?)` returns the input string unchanged when
  `useFallback` is false. When `useFallback` is true, it replaces every
  occurrence of each special main symbol with its fallback value, including
  repeated and multiline occurrences. It must not change unrelated text or
  common symbols.
- When `useFallback` is omitted, the function chooses the fallback mode from
  terminal Unicode support at module evaluation time. The evaluator passes
  `useFallback` explicitly for deterministic fallback and preservation checks;
  the omitted option is checked only for its stable ordinary-text behavior.
- The package must have no lifecycle scripts, workspaces, native addons,
  generated downloads, subprocesses, or network access. Runtime dependency
  installation must work with the supplied offline npm closure.

# API Usage Guide

Import the package root as an ESM module:

```js
import figures, {mainSymbols, fallbackSymbols, replaceSymbols} from 'figures';

figures.tick;
mainSymbols.tick;
fallbackSymbols.tick;
replaceSymbols('✔ done', {useFallback: true});
```

`mainSymbols` and `fallbackSymbols` are plain objects whose properties are
read-only at the TypeScript boundary. The following special mappings are part
of the contract:

| Name | Main | Fallback |
| --- | --- | --- |
| `tick` | `✔` | `√` |
| `info` | `ℹ` | `i` |
| `warning` | `⚠` | `‼` |
| `cross` | `✘` | `×` |
| `squareSmall` | `◻` | `□` |
| `squareSmallFilled` | `◼` | `■` |
| `circle` | `◯` | `( )` |
| `circleFilled` | `◉` | `(*)` |
| `circleDotted` | `◌` | `( )` |
| `circleDouble` | `◎` | `( )` |
| `circleCircle` | `ⓞ` | `(○)` |
| `circleCross` | `ⓧ` | `(×)` |
| `circlePipe` | `Ⓘ` | `(│)` |
| `radioOn` | `◉` | `(*)` |
| `radioOff` | `◯` | `( )` |
| `checkboxOn` | `☒` | `[×]` |
| `checkboxOff` | `☐` | `[ ]` |
| `checkboxCircleOn` | `ⓧ` | `(×)` |
| `checkboxCircleOff` | `Ⓘ` | `( )` |
| `pointer` | `❯` | `>` |
| `triangleUpOutline` | `△` | `∆` |
| `triangleLeft` | `◀` | `◄` |
| `triangleRight` | `▶` | `►` |
| `lozenge` | `◆` | `♦` |
| `lozengeOutline` | `◇` | `◊` |
| `hamburger` | `☰` | `≡` |
| `smiley` | `㋡` | `☺` |
| `mustache` | `෴` | `┌─┐` |
| `star` | `★` | `✶` |
| `play` | `▶` | `►` |
| `nodejs` | `⬢` | `♦` |
| `oneSeventh` | `⅐` | `1/7` |
| `oneNinth` | `⅑` | `1/9` |
| `oneTenth` | `⅒` | `1/10` |

The function accepts a string and an optional object with a boolean
`useFallback`. It is synchronous, deterministic after import, and returns a
string. An invalid input should fail normally rather than silently producing a
different type.

# Implementation Notes

Keep the implementation self-contained apart from the declared
`is-unicode-supported` runtime dependency. Preserve ESM exports and the
package root export map. Replacement order must be stable and replacement
must be literal, not a regular-expression interpretation of symbol text.
Some names intentionally share a main glyph. For `replaceSymbols`, the first
matching entry in the source declaration order wins; therefore the shared
glyph `Ⓘ` is replaced as the `circlePipe` value `(│)`.
Keep TypeScript declarations aligned with runtime exports and reject unknown
options or non-boolean `useFallback` values at the type level.
