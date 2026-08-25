# Project Description

Create an installable Python package named `parse` that extracts values from
text by applying a small, deterministic subset of Python's format-string
syntax in reverse. The package is built from an empty workspace and must not
depend on network services or non-standard runtime packages.

The supported surface is intentionally bounded to exact parsing, first-match
search, non-overlapping iteration, reusable parsers, and result access. Date
and time formats, custom type callbacks, internal regular-expression strings,
and undocumented implementation helpers are outside this task.

# Supports

- CPython 3.12 on Linux.
- An installable distribution named `parse`, importable with `import parse`.
- A `pyproject.toml` build using setuptools. The package has no third-party
  runtime dependencies.
- Either a top-level `parse.py` module or an equivalent `parse` package.
- All matching is deterministic and has no file, environment, or network side
  effects.

# API Usage Guide

## `parse.parse`

```python
parse(format, string, extra_types=None, evaluate_result=True,
      case_sensitive=False)
```

Match `format` against the whole `string`. Both required arguments are
strings. Return `None` when the text does not match. Otherwise return a
`Result`; when `evaluate_result=False`, return a `Match` whose
`evaluate_result()` method produces that same `Result`.

Literal text is escaped: regular-expression metacharacters such as `?`, `|`,
`[`, `]`, `(`, and `*` have no special meaning. `{{` and `}}` denote literal
braces. Matching is case-insensitive by default and case-sensitive when
requested. Matching and extracted values preserve Unicode and newlines.

Fields use `{}`, `{name}`, or `{0}` syntax. Unnamed and numeric fields are
placed in `Result.fixed` in field order. Named fields are placed in
`Result.named`. A format may mix both kinds. Repeating a named field requires
the same source text each time; a different repeated value does not match.
Dot-separated names such as `{user.name}` remain flat dictionary keys.
Bracket paths such as `{user[name]}` create nested dictionaries.

The following type codes are required:

| Code | Accepted text | Result value |
| --- | --- | --- |
| absent or `s` | any non-empty text | `str` |
| `w` | one or more word characters | `str` |
| `W` | one or more non-word characters | `str` |
| `d` | signed decimal or `0b`/`0o`/`0x` integer | `int` |
| `b`, `o`, `x` | binary, octal, hexadecimal integer | `int` |
| `f`, `F`, `e`, `g` | signed decimal floating point | `float`, except `F` returns `Decimal` |
| `%` | decimal percentage ending in `%` | fraction as `float` |
| `l` | one or more ASCII letters | `str` |

For text fields, a width (`{:4}`) is a minimum unless precision is also
present. Precision (`{:.4}`) is a maximum. Equal width and precision
(`{:4.4}`) therefore require exactly four characters. Adjacent fixed-width
fields split deterministically. Numeric zero padding such as `{:02d}` is
supported.

Alignment markers `<`, `>`, and `^` strip matching padding from the extracted
value. A character before the marker is the fill character, for example
`{:.>}`. Sign flags on numeric fields are accepted but do not require a sign.

## `parse.search`

```python
search(format, string, pos=0, endpos=None, extra_types=None,
       evaluate_result=True, case_sensitive=False)
```

Return the first match anywhere in `string`, or `None`. Search starts at
`pos`; `endpos` is an exclusive upper bound. Result evaluation, case handling,
field conversion, and result shape are the same as for `parse()`.

## `parse.findall`

```python
findall(format, string, pos=0, endpos=None, extra_types=None,
        evaluate_result=True, case_sensitive=False)
```

Return an iterable of successive, non-overlapping matches in source order.
The range and case options have the same meaning as in `search()`. Each item is
a `Result`, or a `Match` when evaluation is delayed. An empty match set is an
empty iterable.

## `parse.compile` and `parse.Parser`

```python
compile(format, extra_types=None, case_sensitive=False) -> Parser
Parser(format, extra_types=None, case_sensitive=False)
```

Create a reusable parser. `Parser.parse(string, evaluate_result=True)`,
`Parser.search(string, pos=0, endpos=None, evaluate_result=True)`, and
`Parser.findall(string, pos=0, endpos=None, evaluate_result=True)` follow the
function contracts above. `Parser.format` retains the original format string.
`fixed_fields` lists the zero-based positions of fixed fields among all fields
in the format, and `named_fields` lists named fields in format order.

Malformed fields and an unknown type code raise `ValueError`. Compiling the
same repeated field name with incompatible type codes raises
`RepeatedNameError`, a `ValueError` subclass.

## `parse.Result`

```python
Result(fixed, named, spans)
```

`fixed` is exposed as a tuple and `named` as a dictionary. Integer and slice
subscription reads `fixed`; string subscription reads `named`. Missing integer
indexes raise `IndexError`, and missing names raise `KeyError`. Membership
tests dictionary keys only. Results from parsing also expose `spans`, mapping
each fixed index or named key to the half-open `(start, end)` source range.

# Implementation Notes

The parser should translate the supported format grammar into safe matching
logic and then convert captured text. It must treat format literals as
literals, anchor `parse()` to the complete input, preserve source order for
`findall()`, and avoid zero-length iteration loops. Public behavior, not a
particular regular-expression construction, is graded.

```python
from parse import compile, findall, parse, search

assert parse("hello {}", "hello world").fixed == ("world",)
assert parse("{n:d}", "0x10").named == {"n": 16}
assert search("age: {:d}", "name: Ada; age: 42").fixed == (42,)
assert [r.fixed[0] for r in findall("<{}>", "<a><b>")] == ["a", "b"]
assert compile("{name:w}:{score:03d}").parse("Ada:007").named == {
    "name": "Ada",
    "score": 7,
}
```
