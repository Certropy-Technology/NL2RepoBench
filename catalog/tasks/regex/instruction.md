# Build `regex`

Create a complete, installable Python package named `regex` from an empty
workspace. It is an alternative regular-expression engine with a compatible
core API and additional Unicode and fuzzy-matching features. The package must
work without network access and without any preinstalled copy of `regex`.

## Project Description

Implement the deterministic public behavior described below. The reference
revision contains a Python parser/core and a native `_regex` extension. Preserve
that split or provide an equivalent implementation, but the package must be
installable from source using the standard Python build interface. The scored
surface is intentionally focused on useful local regex operations rather than
the full upstream development repository.

## Supports

- Support CPython 3.12 on Linux x86_64.
- Provide an installable distribution named `regex` and an import package named
  `regex`.
- Runtime behavior must be local and deterministic. Do not contact a network,
  invoke a subprocess, inspect a VCS checkout, or require a service.
- Source-only installation must work without a `.git` directory. Resolve the
  version deterministically in `pyproject.toml` or equivalent packaging files.
- Build the native matching extension when using the upstream architecture.
  The evaluation image supplies a compiler, but the candidate must declare its
  build backend and not download anything during installation.

# Natural Language Instruction

Create the installable `regex` package from an empty workspace. Implement the
root exports, compiled-pattern and match APIs, replacements, iteration, Unicode
and fuzzy matching, bytes/text separation, flags, and stated errors. Preserve
the native build boundary when needed, without copying source or tests.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE.txt
├── README.md
└── regex/
    ├── __init__.py
    ├── _main.py
    ├── _regex_core.py
    └── py.typed
```

# API Usage Guide

### Package exports

The root package must expose the public names below, with the same value or
callable behavior as the reference revision:

```text
__version__, DEFAULT_VERSION, RegexFlag, Regex, Pattern, Match, error,
compile, template, purge, cache_all, escape, match, fullmatch, prefixmatch,
search, sub, subf, subn, subfn, split, splititer, findall, finditer,
VERSION0, VERSION1, V0, V1, ASCII, A, BESTMATCH, B, DEBUG, D, ENHANCEMATCH,
E, FULLCASE, F, IGNORECASE, I, LOCALE, L, MULTILINE, M, POSIX, P, REVERSE,
R, DOTALL, S, UNICODE, U, WORD, W, VERBOSE, X
```

`regex._main` is the implementation-facing module and must provide the same
public functions and constants. `regex._regex_core` must be importable and
must expose `RegexFlag` and the named flag aliases used by the root package.

### Compilation and matching

Implement these signatures and preserve positional and keyword behavior:

```python
compile(pattern, flags=0, ignore_unused=False, cache_pattern=None, **kwargs)
match(pattern, string, flags=0, pos=None, endpos=None, partial=False, concurrent=None, timeout=None, ignore_unused=False, **kwargs)
fullmatch(pattern, string, flags=0, pos=None, endpos=None, partial=False, concurrent=None, timeout=None, ignore_unused=False, **kwargs)
prefixmatch(pattern, string, flags=0, pos=None, endpos=None, partial=False, concurrent=None, timeout=None, ignore_unused=False, **kwargs)
search(pattern, string, flags=0, pos=None, endpos=None, partial=False, concurrent=None, timeout=None, ignore_unused=False, **kwargs)
```

Patterns may be strings, bytes, or an already compiled pattern. Return a
`Match` object or `None`; compiled patterns expose `pattern`, `flags`, `groups`,
`groupindex`, `search`, `match`, `fullmatch`, `findall`, `finditer`, `split`,
`splititer`, `sub`, `subn`, `scanner`, and `__repr__`. Match objects support
`group`, `groups`, `groupdict`, `span`, `start`, `end`, `expand`, `__getitem__`,
`string`, `re`, `pos`, `endpos`, `lastindex`, `lastgroup`, and `fuzzy_counts`.

The default matching semantics include ordinary alternation, groups, named
groups, backreferences, lookarounds, anchors, character classes, escapes,
quantifiers, inline flags, and the standard flag aliases. Preserve match
spans, unmatched groups, replacement expansion, and the distinction between
text and bytes. Invalid patterns and mixed text/bytes operations raise the
normal `regex.error` or `TypeError` exceptions.

### Search, replacement, and iteration

`sub`, `subf`, `subn`, and `subfn` accept string or callable replacements and
respect `count`, flags, `pos`, and `endpos`. `split` and `splititer` preserve
captured delimiters. `findall` returns the documented scalar or tuple shape;
`finditer` and `splititer` are iterators. With `overlapped=True`, `finditer`
and `findall` may return overlapping matches in left-to-right order.

### Extended behavior

Support VERSION0 and VERSION1 modes, nested set operations in VERSION1,
Unicode properties such as `\\p{L}` and `\\p{Script=Greek}`, full case folding,
the `\\X` grapheme matcher, fuzzy constraints such as `{e<=1}`, BESTMATCH,
ENHANCEMATCH, POSIX and REVERSE behavior, partial matches, repeated named
groups, branch-reset groups, named lists, and `(?r)` reverse matching. Fuzzy
matches expose `fuzzy_counts` and `fuzzy_changes`.

`escape(pattern, special_only=True, literal_spaces=False)` must return an
escaped text or bytes pattern. `purge()` clears the pattern cache and
`cache_all(value=True)` controls whether patterns are cached.

## Determinism and Error Boundaries

- Fixed patterns, input values, flags, callbacks, and process hash seeds produce
  identical explicit results. Preserve input order and match order.
- Do not promise object identity, memory addresses, hash values, or pickles
  across processes. A verifier will compare explicit projections of matches.
- File or packaging metadata must not depend on a mutable branch or network.
- Invalid pattern syntax, incompatible types, invalid keyword arguments, and
  timeout limits must raise normal Python exceptions rather than silently
  changing the result.

## Implementation Notes

Keep the implementation modular and make the root re-exports consistent with
the implementation modules. The task does not require the upstream repository's
documentation, development helpers, release automation, or coverage tooling.
Do not copy the upstream source or its tests into the generated project.

The distribution metadata must report version `2026.8.12`, require Python
`>=3.10`, and use a deterministic source-only build configuration. Runtime
dependencies are not required beyond the Python standard library; the native
extension may use only the CPython C API.

# Examples

```python
import regex
pattern = regex.compile(r"(?P<word>\p{L}+)")
pattern.search("café").group("word")
```

```python
regex.findall(r"a", "banana", overlapped=True)
```

```python
regex.sub(r"cat", "dog", "a cat")
```

# Error Handling and Boundary Conditions

Invalid syntax and keyword combinations raise `regex.error` or `TypeError`;
mixed text and bytes operations are rejected. Preserve match spans, unmatched
groups, replacement expansion, timeout errors, and deterministic match order.
