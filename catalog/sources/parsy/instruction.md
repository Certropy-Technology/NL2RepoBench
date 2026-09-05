# parsy

## Project Description

Build an installable `parsy` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `parsy`; public import package begins at `parsy`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Streams, results, and errors`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Result`: preserve the documented object or module behavior, including state and side effects.
3. `ParseError`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Parser`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `parsy`; public import package begins at `parsy`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `iniconfig==2.3.0`, `packaging==26.3`, `pluggy==1.6.0`, `pygments==2.21.0`, `pytest==9.1.1`, `setuptools==80.10.2`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── an/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

### Streams, results, and errors

Parsers operate on a string, a `bytes` value, or a list of arbitrary tokens.
Indexes are zero-based. A low-level parser callback receives `(stream, index)`
and returns a `Result`.

#### `Result`

Expose `Result` with these public fields:

```python
Result(status, index, value, furthest, expected)
```

- `status` is a boolean indicating success.
- On success, `index` is the next input position and `value` is the produced
  value. `furthest` is `-1` and `expected` is an empty frozen set.
- On failure, `index` is `-1`, `value` is `None`, `furthest` is the input
  position at which the failure occurred, and `expected` contains the expected
  description.
- `Result.success(index, value)` and `Result.failure(index, expected)` create
  the corresponding results.
- `aggregate(other)` keeps the failure information that reached furthest. If
  both failures reached the same position, combine their expected descriptions
  while preserving the current result's status, index, and value. A missing
  `other` leaves the current result unchanged.

#### `ParseError`

Construct `ParseError(expected, stream, index)`, a `RuntimeError` with public
`expected`, `stream`, and `index` attributes. Its `line_info()` reports a
zero-based `(line, column)` position as
`"line:column"` for a string stream. For non-string streams it reports the
numeric index as text. Its string form is:

- `expected 'x' at 0:0` for one expectation;
- `expected one of 'x', 'y' at 0:0` for multiple expectations.

Expected descriptions are represented using their `repr` values and are sorted
in the message. `line_info_at(stream, index)` returns the zero-based line and
column for a string, counts `\n` before the index, and raises `ValueError` when
the index is greater than the stream length. The end position is valid.

### `Parser`

Construct a parser with:

```python
Parser(wrapped_fn)
```

where `wrapped_fn(stream, index)` returns a `Result`. Calling a parser as
`parser(stream, index)` invokes that callback.

`parse(stream)` requires the parser to consume the entire stream and returns
the produced value. It raises `ParseError` on failure or when unconsumed input
remains. `parse_partial(stream)` permits a remainder and returns
`(value, remainder)`, or raises `ParseError` on failure. For strings and bytes,
the remainder has the same type; for token lists, it is the unconsumed list
slice.

The following methods return new parsers and leave the original parser
unchanged:

- `bind(bind_fn)`: after success, call `bind_fn(value)` to obtain the next
  parser and continue at the next input position.
- `map(map_function)`: transform the produced value without consuming more
  input.
- `combine(combine_fn)`: pass a sequence result to `combine_fn` with `*args`.
- `combine_dict(combine_fn)`: convert the result to a mapping and call the
  function with keyword arguments. Omit entries whose key is `None` or whose
  string key starts with `_`.
- `concat()`: join a sequence of produced strings into one string.
- `then(other)`: run `other` after this parser and return `other`'s value.
- `skip(other)`: run `other` after this parser and retain this parser's value.
- `result(value)`: after a successful match, return the supplied value without
  consuming additional input.
- `many()`: repeat zero or more times and return a list.
- `times(min, max=None)`: repeat between the inclusive bounds and return a
  list. With only one argument, require exactly that number of matches.
- `at_most(n)`: shorthand for zero through `n` matches.
- `at_least(n)`: require at least `n` matches, with no upper bound.
- `optional(default=None)`: accept zero or one match and return `default` when
  the match is absent.
- `until(other, min=0, max=float("inf"), consume_other=False)`: repeatedly
  match this parser until `other` matches. The terminator is not consumed by
  default and is excluded from the returned list. With `consume_other=True`,
  consume the terminator and include its value. Enforce the supplied minimum
  and maximum counts and fail if the terminator is not found after the minimum
  has been met. If the maximum is reached first, fail with `"at most
  {max} items"`. If the repeated parser stops after the minimum but before the
  terminator, fail with `"did not find other parser"`. If it stops before the
  minimum, fail with `"at least {min} items; got {count} item(s)"`.
- `sep_by(sep, *, min=0, max=float("inf"))`: repeat this parser with `sep`
  between items. Disallow a trailing separator, enforce the bounds, and return
  an empty list when zero items are allowed and no item is present.
- `desc(description)`: replace the failure expectations with only the supplied
  description and report the failure at this parser's starting index.
- `mark()`: return `((start_line, start_column), value,
  (end_line, end_column))` for the matched value.
- `tag(name)`: return `(name, value)`.
- `should_fail(description)`: implement negative lookahead. If the wrapped
  parser succeeds, fail without consuming input using `description`; if it
  fails, succeed without consuming input and produce that underlying failure
  `Result` as the value.

Parser operators provide equivalent composition:

- `left + right` sequences two parsers and combines their values with `+`.
- `parser * n` repeats exactly `n` times. `parser * range(a, b)` repeats from
  `a` through `b - 1`.
- `left | right` tries alternatives in order. An alternative is tried when
  the preceding parser fails; failure details at the furthest position are
  aggregated.
- `left >> right` is `then`; `left << right` is `skip`.

### Constructors and combinators

- `alt(*parsers)` tries parsers in order and returns the first success. With no
  parsers it always fails with the description `"<empty alt>"`.
- `seq(*parsers, **keyword_parsers)` returns a parser producing a list for
  positional arguments or a dictionary for keyword arguments. The two forms
  cannot be mixed and mixing them raises `ValueError`. With no arguments it
  succeeds with an empty list. Keyword order follows declaration order.
- `generate(fn)` turns a generator function into a parser. Each yielded value
  is a parser; its result is sent back into the generator. The generator's
  returned value is the final result. If it returns another `Parser`, apply
  that parser at the current position. `generate("description")` is a decorator
  form that applies the description to failures.
- `success(value)` succeeds without consuming input and returns `value`.
- `fail(expected)` always fails with the supplied expectation.
- `noop(value)` returns `value` unchanged.

### Primitive parsers

- `string(expected_string, transform=noop)` matches the expected string at the
  current position. Apply `transform` to both the expected and candidate text
  for comparison, while returning the original expected string. Matching is
  fixed-width and does not consume a suffix beyond that width. On mismatch, use
  `expected_string` as the failure expectation.
- `regex(exp, flags=0, group=0)` accepts a string, bytes pattern, or compiled
  regular expression and applies it at the current position. Return the full
  match by default. `group` may be an integer, group name, or tuple of group
  selectors; return the selected group or tuple of groups. A non-match fails
  with the pattern description.
- `test_item(func, description)` tests the next item with `func` and returns
  that item on success. For a bytes stream, pass a one-byte `bytes` slice to
  the predicate rather than an integer. For a list, pass the list element.
- `test_char(func, description)` has the same behavior as `test_item` and is
  the character-oriented spelling.
- `match_item(item, description=None)` matches the next item by equality. When
  `description` is omitted, use `str(item)` as the failure description.
- `string_from(*strings, transform=noop)` is an alternative over the supplied
  strings, checking longer strings first so overlapping choices prefer the
  longest match. Return the original matched string.
- `char_from(string_or_bytes)` matches one character or one byte from the
  supplied collection. Its failure expectation is the collection enclosed in
  square brackets, preserving `str` or `bytes` type.
- `peek(parser)` runs a parser as lookahead and returns its value without
  consuming input; propagate its failure unchanged.

Expose these parser objects:

- `any_char`: one item of any kind; failure expectation `"any character"`;
- `whitespace`: one or more characters matching the regular expression `\s+`;
  failure expectation `r"\s+"`;
- `letter`: one character for which `str.isalpha()` is true; failure expectation
  `"a letter"`;
- `digit`: one character for which `str.isdigit()` is true, including Unicode
  digits such as superscript two; failure expectation `"a digit"`;
- `decimal_digit`: one ASCII character from `0123456789`; failure expectation
  `"[0123456789]"`;
- `index`: succeeds without consuming input and returns the current zero-based
  stream index;
- `line_info`: succeeds without consuming input and returns the current
  zero-based `(line, column)` pair;
- `eof`: succeeds only at or beyond the end of the stream and returns `None`;
  failure expectation `"EOF"`.

### Enum and recursive parsers

- `from_enum(enum_cls, transform=noop)` builds a parser from an `enum.Enum`
  class. Match the string form of each member value, prefer longer values,
  apply `transform` for matching, and return the corresponding enum member.
- `forward_declaration()` creates a parser placeholder for recursive grammar
  definitions. It must raise `ValueError` if parsed before `.become(parser)`.
  `.become(parser)` installs the target parser exactly once; recursive and
  mutually dependent definitions must then parse using the installed behavior.


- Preserve deterministic ordering in alternatives, enum values, error
  expectations, and sequence outputs.
- Parsing must support both text and byte streams where a primitive supports
  them, as well as arbitrary token lists for `test_item`, `match_item`, and
  parser composition.
- `parse` and `parse_partial` must expose the furthest failure position and
  aggregated expectations through `ParseError` rather than leaking internal
  callback exceptions for ordinary parse failures.
- Do not add a command-line interface or third-party runtime dependency; this
  project is a library.
- A caller can build recursive grammars, token lexers, and structured parsers
  using only the public API. For example, a parser made from
  `regex(r"[0-9]{4}").map(int)` should produce the integer year, and
  `seq(letter, digit).parse("a1")` should produce `["a", "1"]`.
- Keep tests and examples optional and self-authored. The evaluator supplies
  its own tests; do not depend on evaluator files being present in the agent
  workspace.

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
Result(status, index, value, furthest, expected)
```

### Example 2: ordinary usage
```text
Parser(wrapped_fn)
```

### Example 3: boundary or error behavior
```text
Result(status, index, value, furthest, expected)
```

### Example 4: boundary or error behavior
```text
Parser(wrapped_fn)
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
