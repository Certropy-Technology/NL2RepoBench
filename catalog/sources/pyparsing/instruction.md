## Project Description

Build `pyparsing`, a pure-Python parser-combinator library for Python
developers who need to describe a grammar, parse text, transform matched
tokens, and inspect structured parse results without writing a separate lexer.
The package is used for small configuration languages, command syntaxes,
data formats, and embedded domain-specific languages.

The candidate starts from an empty workspace and must produce an installable
distribution named `pyparsing` whose import package is also `pyparsing`.
Reproduce the public behavior of the pinned 3.3.3 API: parser expressions,
composition operators, parse actions, named and nested results, diagnostics,
Unicode helpers, common parsers, testing helpers, and the documented optional
diagram and conversion modules. Public behavior includes result ordering,
whitespace handling, source locations, deterministic failure information,
warnings, and compatibility spellings.

The public boundary is Python API behavior and the two documented module
entry points. A caller must be able to construct a grammar, invoke it on a
string or file, receive `ParseResults` or a documented exception, and use the
returned objects through their list, mapping, and attribute interfaces.
Parser callbacks supplied by a caller are part of the supported API; they may
return replacement tokens, mutate tokens, or raise a parse exception.

Do not add network clients, a service, a database, a command-line product, or
an unrelated parser framework. Do not require a compiler or native extension.
The diagram extra may depend on its declared pure/Python dependencies, but
the core package must work without that extra. Do not expose private source
helpers as additional compatibility guarantees merely because they are useful
internally.

## Supports

- Runtime: CPython 3.9 or newer. The target package version is `3.3.3` and
  the implementation must be portable pure Python on POSIX and Windows.
- Distribution and import: package name `pyparsing`; `import pyparsing` must
  expose the documented root names and compatibility aliases. Use
  `pyproject.toml` with the `flit_core.buildapi` backend and a build
  requirement compatible with `flit_core>=3.12,<4`.
- Installation: `python -m pip install .` must install the package and its
  package data. `pip install -e .` is useful during development. Core runtime
  dependencies are empty. The optional `diagrams` extra provides
  `railroad-diagrams` and `jinja2` for `pyparsing.diagram`.
- Test tooling: pytest is used by the harness. It may invoke
  `python -m pytest --continue-on-collection-errors -q tests
  examples/tiny/tests`; the candidate must not depend on ambient pytest
  plugins. Development-only tools such as tox, coverage, pre-commit, Sphinx,
  mypy, and matplotlib are not core runtime dependencies.
- Network: the agent, candidate, verifier, Oracle, and controls run with no
  network. They must not access GitHub, PyPI, a package proxy, DNS, or an
  external service during execution. Required dependencies must be installed
  before an offline run; diagram behavior when its extra is absent must be a
  clear installation-related failure, not a network attempt.
- Expected layout and setup: the harness installs the current workspace,
  invokes Python from that workspace, and may create temporary text files for
  `parse_file`, converter tests, or diagram output. Do not assume a current
  directory beyond normal relative-path resolution. Preserve the bundled
  `pyparsing/ai/best_practices.md` resource and an empty `pyparsing/py.typed`
  marker.

Project Directory Structure:

```text
workspace/
├── pyproject.toml
└── pyparsing/
    ├── __init__.py
    ├── actions.py
    ├── common.py
    ├── core.py
    ├── exceptions.py
    ├── helpers.py
    ├── pyparsing_common.py
    ├── pyparsing_unicode.py
    ├── results.py
    ├── testing.py
    ├── unicode.py
    ├── py.typed
    ├── ai/
    │   ├── __init__.py
    │   ├── best_practices.md
    │   └── show_best_practices.py
    ├── diagram/
    │   ├── __init__.py
    │   └── template.jinja2
    └── tools/
        ├── __init__.py
        └── cvt_pyparsing_pep8_names.py
```

The distribution has no console-script entry point. The supported executable
module is `python -m pyparsing.ai.show_best_practices`. The converter is also
usable as `python -m pyparsing.tools.cvt_pyparsing_pep8_names`.

## API Usage Guide

All names in this section are importable from the stated path. Unless a
signature says otherwise, a parser argument may be a `ParserElement` or a
string that is converted to a literal parser. Matching consumes input from a
location and normally skips the configured whitespace before an element.
Successful tokens retain source order. A failed match raises
`ParseException` through the public parsing methods unless a combinator
handles that failure as part of its documented alternative or lookahead
semantics.

### Root metadata and exports

Import with `import pyparsing as pp`. `__version__` is the string `"3.3.3"`;
`__version_time__`, `__versionTime__`, `__author__`, `__compat__`, `__diag__`,
`version_info`, and `__version_info__` expose package metadata and compatibility
state. Metadata is read-only for normal callers and does not parse input.
Example: `assert pp.__version__.count(".") == 2`. Edge case: importing the
package must still work when the diagram extra is not installed.

The root `__all__` contains these modern names and namespace exports:
`And`, `AtLineStart`, `AtStringStart`, `CaselessKeyword`, `CaselessLiteral`,
`CharsNotIn`, `CloseMatch`, `Combine`, `DelimitedList`, `Dict`, `Each`,
`Empty`, `FollowedBy`, `Forward`, `GoToColumn`, `Group`, `IndentedBlock`,
`Keyword`, `LineEnd`, `LineStart`, `Literal`, `Located`, `MatchFirst`,
`NoMatch`, `NotAny`, `OneOrMore`, `OnlyOnce`, `OpAssoc`, `Opt`, `Optional`,
`Or`, `ParseBaseException`, `ParseElementEnhance`, `ParseException`,
`ParseExpression`, `ParseFatalException`, `ParseResults`,
`ParseSyntaxException`, `ParserElement`, `PositionToken`,
`PyparsingDeprecationWarning`, `PyparsingDiagnosticWarning`,
`PyparsingWarning`, `QuotedString`, `RecursiveGrammarException`, `Regex`,
`SkipTo`, `StringEnd`, `StringStart`, `Suppress`, `Tag`, `Token`,
`TokenConverter`, `White`, `Word`, `WordEnd`, `WordStart`, `ZeroOrMore`,
`Char`, and all helpers, constants, parser objects, and namespaces listed
below. Keep this export set and its compatibility spellings available.

### Atomic and position parser classes

The following classes are imported from `pyparsing` and construct parser
elements. They return a `ParserElement` (or a subclass) and have no I/O side
effect at construction time. They are deterministic for fixed arguments.

- `ParserElement(savelist: bool = False)` is the base parser element. It is
  subclassable and is the receiver of the common methods and operators below.
  `Token()` is the minimal token base. These bases are not useful for matching
  by themselves: parsing an unimplemented/base token is an unsuccessful or
  abstract operation rather than a match of arbitrary text.
- `Literal(match_string: str = "", **kwargs)` matches the exact string and
  returns that text. `CaselessLiteral(match_string: str = "", **kwargs)`
  compares without case sensitivity while returning the matched text.
  Empty literals are valid and succeed without consuming input; a non-string
  match value is invalid.
- `Keyword(match_string: str = "", ident_chars: str | None = None,
  caseless: bool = False, **kwargs)` matches a word only when identifier
  boundaries, defined by `ident_chars`, surround it. `CaselessKeyword` has
  signature `CaselessKeyword(match_string: str = "", ident_chars: str | None =
  None, **kwargs)` and uses case-insensitive matching. A prefix of a longer
  identifier fails, unlike `Literal`.
- `CloseMatch(match_string: str, max_mismatches: int | None = None,
  *, caseless=False, **kwargs)` accepts a string with at most the configured
  mismatches and returns the matched text plus mismatch information in its
  parse results. The pattern must be a string and the mismatch limit cannot
  be negative. An input outside the tolerance raises `ParseException`.
- `Word(init_chars: str = "", body_chars: str | None = None, min: int = 1,
  max: int = 0, exact: int = 0, as_keyword: bool = False,
  exclude_chars: str | None = None, **kwargs)` consumes a word beginning with
  one `init_chars` character followed by `body_chars` characters. `max=0`
  means no upper bound; `exact` requests an exact length. `Char(charset: str,
  as_keyword: bool = False, exclude_chars: str | None = None, **kwargs)`
  consumes one character from a set. `CharsNotIn(not_chars: str = "", min: int
  = 1, max: int = 0, exact: int = 0, **kwargs)` consumes characters not in a
  set. `White(ws: str = " \\t\\r\\n", min: int = 1, max: int = 0, exact: int =
  0, **kwargs)` consumes configured whitespace. Length constraints that cannot
  be met fail; an empty character set is therefore an edge case, not a
  wildcard promise.
- `Regex(pattern, flags=0, as_group_list: bool = False, as_match: bool =
  False, **kwargs)` matches a compiled or compilable regular expression.
  Its result is normally the matched text; `as_group_list` returns groups as a
  list and `as_match` returns the match object. Invalid regular expressions
  propagate the regular-expression error at construction.
- `QuotedString(quote_char: str = "", esc_char: str | None = None,
  esc_quote: str | None = None, multiline: bool = False,
  unquote_results: bool = True, end_quote_char: str | None = None,
  convert_whitespace_escapes: bool = True, **kwargs)` matches a quoted value,
  supports distinct end quotes and escape conventions, and returns either the
  unquoted value or the source-quoted value according to `unquote_results`.
  Unterminated or disallowed multiline input fails. `Empty(match_string="",
  *, matchString="")` succeeds without consuming input and may return its
  configured empty token.
- `GoToColumn(colno: int)` advances to a requested column, failing if the
  current line cannot reach it. `LineStart()` and `LineEnd()` assert or match
  physical line boundaries; `StringStart()` and `StringEnd()` assert the
  complete input boundaries. `WordStart(word_chars=printables, **kwargs)` and
  `WordEnd(word_chars=printables, **kwargs)` assert word boundaries. These
  position elements generally return no meaningful text and do not consume
  characters. Negative or otherwise invalid column values are rejected.
- `Tag(tag_name: str, value=True)` emits a named result with `tag_name` and
  `value` when reached. The name must be usable as a result key. `PositionToken`
  is the base for position-constrained tokens; `AtStringStart(expr)` and
  `AtLineStart(expr)` wrap an expression and require it at the corresponding
  beginning without consuming an extra prefix.

Ordinary example: `word = pp.Word(pp.alphas, pp.alphanums + "_")` parses
`"name_2"` as one token. Edge example: `pp.StringEnd().parse_string("x",
parse_all=True)` raises because the parser has not consumed the preceding
`x`.

### Expression, enhancement, and repetition classes

`ParseExpression(exprs, savelist: bool = False)` is the base for expressions
over a sequence. `And(exprs_arg, savelist: bool = True)` requires every child
in sequence and concatenates their tokens. `MatchFirst(exprs, savelist:
bool = False)` tries alternatives in declaration order and returns the first
successful one. `Or(exprs, savelist: bool = False)` tries alternatives and
selects the longest successful match. `Each(exprs, savelist: bool = True)`
requires all expressions, allowing them to appear in a different order; its
result ordering follows the expressions and named-result rules, not input
sorting. All accept parser elements or convertible strings and return parser
elements. Empty expression lists are allowed only where the class can
represent an empty expression; invalid child values fail at construction.

`ParseElementEnhance(expr, savelist: bool = False)` is the enhancement base.
`FollowedBy(expr)` and `PrecededBy(expr, retreat: int = 0)` perform zero-width
positive lookahead at the current position. `NotAny(expr)` is negative
lookahead. Lookahead does not consume input and fails with `ParseException`
when its condition is not satisfied. `SkipTo(other, include: bool = False,
ignore=None, fail_on=None, **kwargs)` consumes through the next `other`,
optionally includes it, skips ignored constructs, and can stop on `fail_on`.
If no stopping expression is found it fails rather than silently returning
the remainder.

`OneOrMore(expr, stop_on=None, max: int | None = None, **kwargs)` requires at
least one repetition. `ZeroOrMore` has the same shape but permits zero.
`Opt(expr, default=<null-token>)` and `Optional(expr, default=<null-token>)`
are the same public class: they parse once when present and otherwise emit
the supplied default behavior. `max` limits repetitions. A repeated parser
that succeeds without consuming input is guarded against infinite loops.

`Forward(other=None)` is a deferred parser reference. Assign a parser with
`forward <<= expression` (or the compatibility `<<`) before parsing a
recursive grammar; parsing before assignment fails. `IndentedBlock(expr, *,
recursive: bool = False, grouped: bool = True)` parses indentation-based
blocks and returns grouped or ungrouped results. `DelimitedList(expr,
delim=",", combine: bool = False, min: int | None = None, max: int | None =
None, *, allow_trailing_delim: bool = False)` parses delimited values and
optionally combines them into a string. Bounds and trailing delimiter policy
are enforced; malformed separators raise `ParseException`.

`TokenConverter(expr, savelist=False)` is the converter base. `Combine(expr,
join_string: str = "", adjacent: bool = True, *, joinString: str | None =
None)` joins adjacent token text, `Group(expr, aslist: bool = False)` nests
tokens in one `ParseResults`, `Dict(expr, asdict: bool = False)` maps grouped
key/value tokens to named results, `Suppress(expr, savelist: bool = False)`
matches but removes tokens, and `Located(expr, savelist: bool = False)` adds
source-location information around the wrapped result. These wrappers retain
the wrapped parser's failure and callback behavior.

Example: `number = pp.Word(pp.nums); grammar = pp.DelimitedList(number)`
parses `"1, 20"` into two ordered values. Edge example:
`pp.OneOrMore(pp.Empty()).parse_string("")` must terminate deterministically
and must not loop forever.

### ParserElement methods and operators

Every concrete parser element supports the following methods. Methods that
configure a parser return the parser for chaining unless noted; `copy()`
returns an independent parser copy. `set_results_name(name: str,
list_all_matches: bool = False, **kwargs)` names results, while
`set_name(name: str | None)` changes its diagnostic/display name. A named
result is available by key and attribute, and `list_all_matches=True` retains
all values under that key instead of the modal last value.

`set_parse_action(*fns, call_during_try: bool = False, **kwargs)` replaces
parse actions; `add_parse_action` appends them; `add_condition(*fns,
call_during_try: bool = False, **kwargs)` rejects results when a predicate is
false; and `set_fail_action(fn)` registers a failure callback. A parse action
may use `(s, loc, tokens)`, `(loc, tokens)`, `(tokens)`, or a compatible
callable shape, and its return value replaces or augments tokens according to
the action contract. Exceptions from a callback are observable; a false
condition produces a parse failure. `suppress()` returns a token-suppressing
copy/wrapper. `ignore(other)` registers an ignored expression. `ignore_whitespace
(recursive: bool = True)`, `leave_whitespace(recursive: bool = True)`, and
`set_whitespace_chars(chars, copy_defaults: bool = False)` control whitespace
for this element and optionally its descendants. `parse_with_tabs()` preserves
tab positions for column calculations.

`parse_string(instring: str, parse_all: bool = False, **kwargs) ->
ParseResults` parses from the beginning, optionally requiring end-of-input.
`scan_string(instring: str, max_matches=sys.maxsize, overlap: bool = False,
always_skip_whitespace=True, *, debug: bool = False, **kwargs)` yields
`(ParseResults, start, end)` triples in increasing source order. `search_string`
returns the collected scan results. `transform_string(instring: str, *,
debug: bool = False) -> str` applies parse actions and replaces matched spans,
preserving unmatched text. `split(instring: str, maxsplit=sys.maxsize,
include_separators: bool = False, **kwargs)` returns an ordered list of text
parts. `parse_file(file_or_filename, encoding: str = "utf-8", parse_all: bool =
False, **kwargs) -> ParseResults` accepts a path or readable file object and
performs file I/O; missing paths and decoding errors propagate. `matches
(test_string: str, parse_all: bool = True, **kwargs) -> bool` converts a
successful or failed parse into a boolean. `try_parse` and
`can_parse_next` provide non-consuming probing. `run_tests(tests,
parse_all=True, comment="#", full_dump=True, print_results=True,
failure_tests=False, post_parse=None, file=None, with_line_numbers=False,
**legacy_kwargs)` runs supplied examples, reports results, and returns the
documented success status/output shape; `file=None` uses the normal output.

`copy`, parser configuration, and execution are deterministic for fixed input
and callbacks. `parse_string` with `parse_all=True` rejects a valid prefix
followed by unconsumed non-whitespace. `scan_string` and `search_string`
preserve left-to-right order, and `overlap` controls whether a new scan may
start before the previous match ends.

Parser operators compose the same public objects: `+` and `-` sequence
expressions, with `-` making a following failure fatal; `|` is first-match
choice; `^` is longest-match choice; `&` is `Each`; unary `~` is `NotAny`; `*`
creates repetition; `[]` indexes or slices results; calling an expression with
a string names it and calling it with a callable adds a parse action. Reverse
string operands are supported. `Forward << expr` and `Forward <<= expr` set a
deferred expression. Operator inputs that are neither strings nor parser
elements raise a type-related error. Example: `pp.Literal("[") +
pp.Word(pp.alphas) + pp.Literal("]")` parses a bracketed word; edge example:
`pp.Literal("a").parse_string("ab", parse_all=True)` raises rather than
silently accepting the suffix.

Class configuration is process-global: `ParserElement.set_default_whitespace_chars
(chars)`, `ParserElement.inline_literals_using(cls)`,
`ParserElement.reset_cache()`, `ParserElement.disable_memoization()`,
`ParserElement.enable_packrat(cache_size_limit=128, *, force=False)`, and
`ParserElement.enable_left_recursion(cache_size_limit=None, *, force=False)`
change defaults or caching for subsequently constructed/executed parsers.
Packrat and left-recursion modes are mutually exclusive unless `force=True`
resets the competing mode. Cache reset and disable operations affect global
state and should be safe to call repeatedly.

### ParseResults

`pyparsing.ParseResults(toklist=None, name=None, **kwargs)` is the ordered
parse-result container. It supports integer indexing, slicing, iteration,
`len`, truth testing, mutation, concatenation, named key lookup, and named
attribute lookup. `keys()`, `values()`, `items()`, `haskeys()`, `pop`, `get`,
`insert`, `append`, `extend`, `clear`, `copy`, `deepcopy`, `get_name`, `dump`,
`pprint`, `as_list(flatten=False)`, `as_dict`, and `from_dict` expose the
mapping/list and display operations. `ParseResults.List` marks a real list
that must remain a Python list within nested results.

The returned type is not JSON-normalized: nested `ParseResults`, named
values, and arbitrary values returned by parse actions are retained. Positional
values preserve parse order. Duplicate modal names resolve according to the
name configuration; list-all-matches names retain a list. `as_list` produces
ordinary nested lists and `as_dict` produces a dictionary representation.
Missing numeric indexes raise `IndexError`; missing named values follow the
mapping accessor contract, while `get` permits a default. Example:
`(pp.Word(pp.alphas)("word")).parse_string("abc").word == "abc"`. Edge case:
`pp.ParseResults().as_list() == []`, and a missing optional key must not be
invented as a positional token.

### Exceptions and warnings

`ParseBaseException(pstr: str, loc: int = 0, msg: str | None = None, elem=None)`
is the base parse error. `ParseException`, `ParseFatalException`, and
`ParseSyntaxException` specialize ordinary, fatal, and syntax failures;
`RecursiveGrammarException(parseElementList)` reports recursive grammar
validation failures. Parse exceptions expose input text, location, message,
parser element, `line`, `lineno`, `col`/`column`, and `found`, plus formatted
messages, `mark_input_line`, and `explain`. They are deterministic for fixed
input and location. `ParseFatalException` must not be silently downgraded by
an alternative combinator. Invalid grammar recursion raises the recursive
exception rather than hanging.

`PyparsingWarning`, `PyparsingDeprecationWarning`, and
`PyparsingDiagnosticWarning` are the warning classes used for compatibility,
deprecation, and diagnostics. `pyparsing.core.Diagnostics`, `__diag__`, and
`__compat__` expose diagnostic state; `enable_diag`, `disable_diag`, and
`enable_all_warnings` configure it. Configuration changes process-global
warning/diagnostic behavior and must not alter already-returned results.
Example: catch `pp.ParseException` from a failed `Word(pp.nums)` parse and
inspect `.lineno` and `.col`. Edge example: a parse action that raises a
`ParseFatalException` remains fatal and does not fall through `|`.

### Actions module

Import these APIs from `pyparsing.actions`: `OnlyOnce(method_call)` is a
parse-action wrapper that invokes its callable once per parser use;
`OnlyOnce.reset()` permits later invocation. `match_only_at_col(n)` creates
an action that accepts a match at column `n`; `replace_with(repl_str)` creates
an action replacing tokens with the supplied value; `remove_quotes(s, loc,
tokens)` removes quote delimiters from token text; `with_attribute
(*name_value_pairs, **attributes)` validates XML/HTML-style attributes and
exposes `with_attribute.ANY_VALUE` as a sentinel for “attribute exists with
any value”; `with_class(classname, namespace="")` validates a class attribute.
Actions return parse-action-compatible callables or transformed tokens, do not
perform network I/O, and preserve source order. Invalid attribute constraints
cause a parse failure. Example: `pp.QuotedString('"').set_parse_action
(pp.remove_quotes)` returns the interior text; edge example: a required
attribute absent from a tag fails instead of producing an empty value.

### Root helper functions

The following helpers are imported from `pyparsing` and are also available
under their implementation modules where stated. Each constructs a parser,
parse action, or deterministic utility; invalid parser arguments fail at
construction or parse time, and no helper performs external I/O.

- `counted_array(expr, int_expr=None, **kwargs)` parses a count followed by
  that many `expr` values. `dict_of(key, value)` parses repeated key/value
  pairs into named dictionary-style results. `one_of(strs, caseless=False,
  use_regex=True, as_keyword=False, **kwargs)` builds alternatives from a
  whitespace-separated string or sequence, preserving longest/declared
  matching semantics. Empty alternatives are not a wildcard.
- `match_previous_literal(expr)` and `match_previous_expr(expr)` match text or
  a prior expression result. The latter also handles nested and repeated
  expressions. They require the referenced expression/result to exist;
  otherwise parsing fails. `original_text_for(expr, as_string=True, **kwargs)`
  returns the exact source span matched by `expr`, as a string by default or
  with location-aware results when requested. `ungroup(expr)` removes one
  grouping layer.
- `nested_expr(opener="(", closer=")", content=None, ignore_expr=NoMatch,
  **kwargs)` parses balanced nested delimiters and returns nested results.
  `make_html_tags(tag_str)` and `make_xml_tags(tag_str)` return open/close tag
  parser pairs. `replace_html_entity(s, loc, tokens)` decodes an HTML entity
  in a parse action. Delimiters must be balanced; an unterminated nest fails.
- `infix_notation(base_expr, op_list, lpar=Suppress("("),
  rpar=Suppress(")"))` builds an expression parser from operator precedence
  specifications. Each operator entry describes an expression, arity, and
  `OpAssoc.LEFT` or `OpAssoc.RIGHT` associativity. `delimited_list` is the
  compatibility function form of `DelimitedList` with signature `delimited_list
  (expr, delim=",", combine=False, min=None, max=None, *,
  allow_trailing_delim=False)`.
- `condition_as_parse_action(fn, message=None, fatal=False)` wraps a
  predicate as a parse action and raises an ordinary or fatal parse failure
  when false. `null_debug_action(*args)` is a no-op debug callback.
  `trace_parse_action(fn)` wraps a callback while exposing entry/exit tracing
  through the parser's normal debug path.
- `srange(source)` converts a range expression into a character-set string;
  malformed range syntax is rejected. `token_map(func, *args)` creates a
  parse action that maps `func` over tokens with fixed extra arguments.
  `autoname_elements()` applies automatic names to parser elements and changes
  diagnostic names, not matched text.

`OpAssoc` is the associativity namespace with `LEFT` and `RIGHT`. The modern
helper names coexist with compatibility aliases: `countedArray`, `dictOf`,
`infixNotation`, `matchOnlyAtCol`, `matchPreviousExpr`,
`matchPreviousLiteral`, `nestedExpr`, `nullDebugAction`, `oneOf`,
`originalTextFor`, `replaceHTMLEntity`, `replaceWith`, `removeQuotes`,
`delimitedList`, `locatedExpr`, `indentedBlock`, `makeHTMLTags`, `makeXMLTags`,
`pythonStyleComment`, `quotedString`, `restOfLine`, and the other aliases in
the root export list. They preserve the corresponding behavior and may emit
the package's deprecation warning. Example: `pp.one_of("red green blue")`
parses one declared color; edge example: `pp.nested_expr("(", ")").parse_string
("(x")` raises `ParseException`.

### Built parser objects and constants

Root character constants are strings: `alphas`, `nums`, `alphanums`,
`hexnums`, `printables`, `alphas8bit`, `punc8bit`, `identchars`, and
`identbodychars`. They are deterministic character sets and can be passed to
`Word` or `Char`; an empty set is not silently expanded.

The root also exports reusable parser objects: `any_open_tag`, `any_close_tag`,
`c_style_comment`, `cpp_style_comment`, `java_style_comment`,
`python_style_comment`, `html_comment`, `dbl_slash_comment`,
`common_html_entity`, `quoted_string`, `dbl_quoted_string`,
`sgl_quoted_string`, `unicode_string`, `rest_of_line`, `line`, `line_start`,
`line_end`, `string_start`, `string_end`, and `empty`. They can be copied,
named, combined, and parsed like any `ParserElement`; they are not factories.
Comment parsers consume their comment syntax, quote parsers return their
configured string result, and boundary parsers are zero-width where
applicable. Example: `pp.python_style_comment + pp.LineEnd()` recognizes a
comment line. Edge example: `pp.empty.parse_string("")` succeeds without
consuming input.

### Common namespace

`pyparsing.common` and its compatibility namespace
`pyparsing.pyparsing_common` provide reusable parsers named `integer`,
`signed_integer`, `hex_integer`, `fraction`, `mixed_integer`, `real`,
`sci_real`, `number`, `fnumber`, `ieee_float`, `identifier`,
`comma_separated_list`, `ipv4_address`, `ipv6_address`, `mac_address`,
`iso8601_date`, `iso8601_datetime`, `iso8601_date_validated`,
`iso8601_datetime_validated`, `uuid`, and `url`. They return parser results
with the corresponding converted Python values or text and reject malformed
input according to each format. Results are ordered and deterministic.

The same namespace exposes `convert_to_integer`, `convert_to_float`,
`convert_to_date`, `convert_to_datetime`, `as_datetime`, `strip_html_tags`,
`upcase_tokens`, and `downcase_tokens` parse actions/factories. Compatibility
spellings such as `convertToInteger`, `stripHTMLTags`, and the other
camelCase forms remain available and may warn. Example:
`pp.common.integer.parse_string("42").as_list() == [42]`. Edge example:
`pp.common.ipv4_address.parse_string("999.1.1.1")` raises rather than
normalizing an invalid address.

### Unicode namespace

`pyparsing.unicode` and `pyparsing.pyparsing_unicode` expose `unicode_set` and
script-set classes `Latin1`, `LatinA`, `LatinB`, `Greek`, `Cyrillic`,
`Chinese`, `Japanese`, `Hangul`, `Korean`, `CJK`, `Thai`, `Arabic`, `Hebrew`,
`Devanagari`, `BMP`/`BasicMultilingualPlane`, and native-script aliases.
Each set provides `printables`, `alphas`, `nums`, `alphanums`, `identchars`,
`identbodychars`, and `identifier` properties where defined. Set union
composes Unicode ranges. These are parser-ready strings or parser objects,
not locale-dependent byte classes. Example:
`pp.Word(pp.pyparsing_unicode.Greek.alphas).parse_string("alpha")` uses the
selected Unicode alphabet. Edge example: a non-ASCII input must be handled as
Unicode text and must not be implicitly encoded as ASCII.

### Testing namespace

`pyparsing.testing` and the compatibility name `pyparsing.pyparsing_test`
export `TestParseResultsAsserts`, `reset_pyparsing_context`, and
`with_line_numbers(s, start_line=None, end_line=None, expand_tabs=True,
eol_mark="|", mark_spaces=None, mark_control=None, *, indent="",
base_1=True)`. `with_line_numbers` returns annotated text with deterministic
line markers and configurable tab/control display. `TestParseResultsAsserts`
provides assertion helpers for comparing parse results. The reset context
saves and restores whitespace, keyword characters, literal class,
packrat/left-recursion mode, cache policy, diagnostics, and related global
state, including when an exception exits the context. Example:
`with pp.reset_pyparsing_context(): pp.ParserElement.set_default_whitespace_chars
(" ")`. Edge example: nested reset contexts restore the outer settings in
LIFO order.

### Optional diagram API

Import from `pyparsing.diagram` only when the `diagrams` extra is installed.
`to_railroad(element, diagram_kwargs=None, vertical=3,
show_results_names=False, show_groups=False, show_hidden=False) ->
list[NamedDiagram]` converts a parser graph to diagram objects;
`railroad_to_html(diagrams, embed=False, **kwargs) -> str` renders HTML;
`resolve_partial(partial)` resolves a deferred diagram operation;
`NamedDiagram(name, index, diagram=None)`, `AnnotatedItem(label, item)`,
`EachItem(*items)`, `EditablePartial(func, args, kwargs)`, `ElementState(...)`,
and `ConverterState(diagram_kwargs=None)` hold diagram conversion state.
`ParserElement.create_diagram(output_html, vertical=3,
show_results_names=False, show_groups=False, embed=False,
show_hidden=False, **kwargs)` is the parser-facing entry point. It accepts a
text stream or writes an HTML path and returns the documented diagram/output
value. Diagram conversion is deterministic for a fixed graph and options;
missing `railroad-diagrams` or `jinja2` raises an installation-guidance
error. It must not attempt installation or network access. Example:
`grammar.create_diagram(None)` produces the in-memory representation when the
extra is present. Edge example: invoking the diagram API without the extra
fails clearly while ordinary parsing continues to work.

### Best practices and tools

`show_best_practices(file=sys.stdout)` reads the bundled Markdown guidance,
prints it to the supplied text stream by default, and returns the guidance
when `file=None`. Resource-read failure uses the package's built-in fallback.
`python -m pyparsing.ai.show_best_practices` prints the same guidance and
returns a normal process status. It performs no network access.

`pyparsing.tools.cvt_pyparsing_pep8_names` exposes `pep8_converter`, the
conversion-name tables, and `camel_to_snake`. As a module/script it accepts
path patterns, scans Python files for old names, prints a diff or status, and
can rewrite files only when its explicit rewrite option is requested. Its
exit status reports whether changes are required. File encoding and I/O
errors are reported rather than silently discarding content. Example:
`python -m pyparsing.tools.cvt_pyparsing_pep8_names "src/*.py"` performs a
status/diff scan. Edge example: an empty path match reports no files and does
not rewrite the current directory. There is no package console command named
`pyparsing`; callers must use these module invocations or Python imports.

## Implementation Notes

Keep the package pure Python and keep root re-exports synchronized with the
module implementations. Modern snake_case names and the listed camelCase
compatibility aliases must refer to the corresponding public behavior, with
warnings only where the compatibility policy calls for them. Include package
metadata, `py.typed`, and the Markdown best-practices resource in the built
wheel.

Parser expressions are composable objects, not one-shot functions. Preserve
the expression graph, deferred `Forward` assignment, parser copies, parse
actions, ignored expressions, result names, and global whitespace/cache/
diagnostic state. Do not make callbacks run during lookahead unless the
configured `call_during_try` behavior requests it. Prevent zero-width
repetition from hanging. Preserve left-to-right scan ordering, exact source
locations, Unicode code points, and deterministic exception fields.

`ParseResults` must preserve both positional and named values, nested results,
duplicate-name policy, mutation, and conversion behavior. Do not serialize
results to JSON internally because parse actions may return arbitrary Python
objects. File parsing must close files opened by the library while leaving a
caller-owned file object usable according to normal context ownership rules.

The core package must be usable without optional diagram dependencies. Diagram
and converter resources are separate module boundaries. No public function
may fetch a missing dependency, contact an external service, or rely on the
repository's test files at runtime. Keep errors as the documented exception
class and avoid converting malformed input into a successful partial result
when `parse_all=True`.

Small verifiable examples:

1. `integer = pp.Word(pp.nums).set_parse_action(lambda t: int(t[0]))` returns
   integer `17` for `"17"`, while `"x"` raises `ParseException`.
2. `item = pp.Word(pp.alphas)("item"); (item + pp.Suppress(",") + item)`
   retains ordered positional tokens and the configured named-value policy.
3. `pp.Literal("a").search_string("ba a")` reports matches in source order;
   `parse_all=True` separately rejects an unconsumed suffix.
4. `pp.nested_expr("[", "]")` accepts balanced nested text and rejects
   `"[unclosed"` with a parse exception; the same grammar works with Unicode
   content inside the delimiters.

The implementation may use any internal organization consistent with the
public layout, but it must not require callers to import private helpers or
rely on undocumented object identity. Keep repeated calls deterministic for
fixed input and configuration, and make process-global configuration changes
explicit and reversible through the documented reset APIs.
