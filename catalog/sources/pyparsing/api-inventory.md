# `pyparsing` API inventory at `efd56db4e59f36b1673ce0eb0823e3afaa9d1201`

This is a source inventory, not a publication approval or a claim that every
unprefixed implementation name is stable. It combines the explicit root
`__all__`, module inspection, constructor signatures, and a tracked-file AST
cross-check. Behavior is summarized in `instruction.md`; source and execution
evidence are in `audit.md` and `evidence.json`.

## Inventory method and limits

- The exact detached source contains 17 tracked runtime Python files.
- `pyparsing.__all__` was parsed from the frozen `pyparsing/__init__.py` and
  cross-checked by importing the same checkout under CPython 3.12.11.
- The list has **171 ordered, unique entries**. Its newline-delimited SHA-256 is
  `c1a066bc7472906088a17275a1792ba65bf9c5df7db2a513c7153b546f3b1277`.
- A separate AST heuristic found 73 unique public class names, 41 unique public
  module-function names, and 177 unique public class-member names. Those counts
  include module-only helpers and inherited/implementation-facing surfaces;
  they are not an API denominator.
- Runtime introspection can show generated aliases and bound parser objects as
  callable. This inventory classifies them by source role instead of treating
  every callable object as a function definition.
- Private names used by upstream tests are not promoted merely because tests
  import them. Conversely, documented module APIs such as `pyparsing.diagram`
  and `pyparsing.tools.cvt_pyparsing_pep8_names` are recorded even though their
  names are not all in the root `__all__`.

## Package modules and tracked size

| module/tree | Python files | physical lines | role |
| --- | ---: | ---: | --- |
| root `pyparsing/*.py` | 11 | 12,080 | parser core, results, exceptions, helpers, namespaces, testing |
| `pyparsing/diagram/` | 1 | 761 | optional railroad-diagram conversion |
| `pyparsing/tools/` | 2 | 142 | PEP8-name conversion tool |
| `pyparsing/ai/` | 3 | 2 | best-practices module entry point; behavior is backed by Markdown data |
| **total** | **17** | **12,985** | installed pure-Python package |

The installed data surface also includes the empty `py.typed` marker and
`pyparsing/ai/best_practices.md`. There is no extension module in the source.

## Exact root exports

The first 125 entries are metadata, modern classes/functions, constants,
parser objects, and namespace classes:

```text
__version__, __version_time__, __author__, __compat__, __diag__,
And, AtLineStart, AtStringStart, CaselessKeyword, CaselessLiteral,
CharsNotIn, CloseMatch, Combine, DelimitedList, Dict, Each, Empty,
FollowedBy, Forward, GoToColumn, Group, IndentedBlock, Keyword, LineEnd,
LineStart, Literal, Located, PrecededBy, MatchFirst, NoMatch, NotAny,
OneOrMore, OnlyOnce, OpAssoc, Opt, Optional, Or, ParseBaseException,
ParseElementEnhance, ParseException, ParseExpression, ParseFatalException,
ParseResults, ParseSyntaxException, ParserElement, PositionToken,
PyparsingDeprecationWarning, PyparsingDiagnosticWarning, PyparsingWarning,
QuotedString, RecursiveGrammarException, Regex, SkipTo, StringEnd,
StringStart, Suppress, Tag, Token, TokenConverter, White, Word, WordEnd,
WordStart, ZeroOrMore, Char, alphanums, alphas, alphas8bit, any_close_tag,
any_open_tag, autoname_elements, c_style_comment, col,
common_html_entity, condition_as_parse_action, counted_array,
cpp_style_comment, dbl_quoted_string, dbl_slash_comment, delimited_list,
dict_of, empty, hexnums, html_comment, identchars, identbodychars,
infix_notation, java_style_comment, line, line_end, line_start, lineno,
make_html_tags, make_xml_tags, match_only_at_col, match_previous_expr,
match_previous_literal, nested_expr, null_debug_action, nums, one_of,
original_text_for, printables, punc8bit, pyparsing_common,
pyparsing_test, pyparsing_unicode, python_style_comment, quoted_string,
remove_quotes, replace_with, replace_html_entity, rest_of_line,
sgl_quoted_string, show_best_practices, srange, string_end, string_start,
token_map, trace_parse_action, ungroup, unicode_set, unicode_string,
with_attribute, with_class
```

The remaining 46 entries are legacy spellings or short namespace aliases:

```text
__versionTime__, anyCloseTag, anyOpenTag, cStyleComment,
commonHTMLEntity, conditionAsParseAction, countedArray, cppStyleComment,
dblQuotedString, dblSlashComment, delimitedList, dictOf, htmlComment,
indentedBlock, infixNotation, javaStyleComment, lineEnd, lineStart,
locatedExpr, makeHTMLTags, makeXMLTags, matchOnlyAtCol,
matchPreviousExpr, matchPreviousLiteral, nestedExpr, nullDebugAction,
oneOf, opAssoc, originalTextFor, pythonStyleComment, quotedString,
removeQuotes, replaceHTMLEntity, replaceWith, restOfLine,
sglQuotedString, stringEnd, stringStart, tokenMap, traceParseAction,
unicodeString, withAttribute, withClass, common, unicode, testing
```

Additional observable root metadata includes the `version_info` named-tuple
class, `__version_info__`, and `__version_time__`. The frozen values resolve to
version `3.3.3`; `__versionTime__` is the compatibility spelling.

## Core constructors

Signatures below are from the exact source/import. Type annotations are
abbreviated only where the full union repeats `ParserElement | str`.

### Atomic and position elements

```python
ParserElement(savelist: bool = False)
Token()
NoMatch()
Literal(match_string: str = "", **kwargs)
CaselessLiteral(match_string: str = "", **kwargs)
Keyword(match_string: str = "", ident_chars: str | None = None,
        caseless: bool = False, **kwargs)
CaselessKeyword(match_string: str = "", ident_chars: str | None = None,
                 **kwargs)
CloseMatch(match_string: str, max_mismatches: int | None = None,
           *, caseless=False, **kwargs)
Word(init_chars: str = "", body_chars: str | None = None,
     min: int = 1, max: int = 0, exact: int = 0,
     as_keyword: bool = False, exclude_chars: str | None = None, **kwargs)
Char(charset: str, as_keyword: bool = False,
     exclude_chars: str | None = None, **kwargs)
Regex(pattern, flags=0, as_group_list: bool = False,
      as_match: bool = False, **kwargs)
QuotedString(quote_char: str = "", esc_char: str | None = None,
             esc_quote: str | None = None, multiline: bool = False,
             unquote_results: bool = True,
             end_quote_char: str | None = None,
             convert_whitespace_escapes: bool = True, **kwargs)
CharsNotIn(not_chars: str = "", min: int = 1, max: int = 0,
           exact: int = 0, **kwargs)
White(ws: str = " \\t\\r\\n", min: int = 1, max: int = 0, exact: int = 0)
Empty(match_string="", *, matchString="")
GoToColumn(colno: int)
LineStart(); LineEnd(); StringStart(); StringEnd()
WordStart(word_chars=printables, **kwargs)
WordEnd(word_chars=printables, **kwargs)
Tag(tag_name: str, value=True)
```

`PositionToken` is the abstract position-token base. `AtStringStart(expr)` and
`AtLineStart(expr)` are position-constrained wrappers rather than aliases of
`StringStart`/`LineStart`.

### Expression and enhancement elements

```python
ParseExpression(exprs, savelist: bool = False)
And(exprs_arg, savelist: bool = True)
Or(exprs, savelist: bool = False)
MatchFirst(exprs, savelist: bool = False)
Each(exprs, savelist: bool = True)
ParseElementEnhance(expr, savelist: bool = False)
FollowedBy(expr)
PrecededBy(expr, retreat: int = 0)
NotAny(expr)
OneOrMore(expr, stop_on=None, max: int | None = None, **kwargs)
ZeroOrMore(expr, stop_on=None, max: int | None = None, **kwargs)
Opt(expr, default=<null-token>)
Optional(expr, default=<null-token>)
SkipTo(other, include: bool = False, ignore=None, fail_on=None, **kwargs)
Forward(other=None)
IndentedBlock(expr, *, recursive: bool = False, grouped: bool = True)
DelimitedList(expr, delim=",", combine: bool = False,
              min: int | None = None, max: int | None = None,
              *, allow_trailing_delim: bool = False)
```

`Opt` and `Optional` are the same public class. `Forward` supports deferred
assignment. Repetition also has index/operator forms on `ParserElement`.

### Result converters

```python
TokenConverter(expr, savelist=False)
Combine(expr, join_string: str = "", adjacent: bool = True,
        *, joinString: str | None = None)
Group(expr, aslist: bool = False)
Dict(expr, asdict: bool = False)
Suppress(expr, savelist: bool = False)
Located(expr, savelist: bool = False)
```

## Shared `ParserElement` surface

Concrete parser elements inherit the following application-facing operations.
Legacy camelCase aliases exist for the corresponding snake_case methods and
emit the source-defined deprecation warnings.

### Construction, naming, and actions

```python
copy() -> ParserElement
set_results_name(name: str, list_all_matches: bool = False, **kwargs)
set_name(name: str | None)
set_parse_action(*fns, call_during_try: bool = False, **kwargs)
add_parse_action(*fns, call_during_try: bool = False, **kwargs)
add_condition(*fns, call_during_try: bool = False, **kwargs)
set_fail_action(fn)
suppress() -> ParserElement
ignore(other)
ignore_whitespace(recursive: bool = True)
leave_whitespace(recursive: bool = True)
set_whitespace_chars(chars, copy_defaults: bool = False)
parse_with_tabs()
```

Class/global configuration includes:

```python
ParserElement.set_default_whitespace_chars(chars)
ParserElement.inline_literals_using(cls)
ParserElement.reset_cache()
ParserElement.disable_memoization()
ParserElement.enable_packrat(cache_size_limit=128, *, force=False)
ParserElement.enable_left_recursion(cache_size_limit=None, *, force=False)
```

Packrat and left-recursion modes are mutually exclusive unless `force=True`
first resets the competing mode. These are process-global settings with
process-global caches and locks.

### Execution and observation

```python
parse_string(instring: str, parse_all: bool = False, **kwargs) -> ParseResults
scan_string(instring: str, max_matches=sys.maxsize, overlap: bool = False,
            always_skip_whitespace=True, *, debug: bool = False, **kwargs)
search_string(instring: str, max_matches=sys.maxsize,
              *, debug: bool = False, **kwargs) -> ParseResults
transform_string(instring: str, *, debug: bool = False) -> str
split(instring: str, maxsplit=sys.maxsize,
      include_separators: bool = False, **kwargs)
parse_file(file_or_filename, encoding: str = "utf-8",
           parse_all: bool = False, **kwargs) -> ParseResults
matches(test_string: str, parse_all: bool = True, **kwargs) -> bool
run_tests(tests, parse_all=True, comment="#", full_dump=True,
          print_results=True, failure_tests=False, post_parse=None,
          file=None, with_line_numbers=False, **legacy_kwargs)
create_diagram(output_html, vertical=3, show_results_names=False,
               show_groups=False, embed=False, show_hidden=False, **kwargs)
```

The shared surface also includes debug actions, recursion/streamlining
inspection, `try_parse`, `can_parse_next`, and deprecated `validate`. Internal
methods such as `parseImpl`, `preParse`, and `postParse` are subclass extension
seams; they are inventory entries, not an invitation for ordinary callers to
bypass `parse_string`.

### Operators

The source implements `+`, `-`, `|`, `^`, `&`, unary `~`, repetition by `*`
and `[]`, results naming by call syntax, reverse string operands, and
`Forward << expr` / `Forward <<= expr`. The exact behavior contract is in the
instruction draft.

## `ParseResults`

```python
ParseResults(toklist=None, name=None, **kwargs)
```

It supports list-style indexing/slicing, iteration, length, truth testing,
mutation, concatenation, and named lookup by key or attribute. Public methods:

```text
keys, values, items, haskeys, pop, get, insert, append, extend, clear,
as_list(flatten=False), as_dict, copy, deepcopy, get_name, dump, pprint,
from_dict
```

`ParseResults.List` marks a real list that should remain a Python list inside
results. Named values can be modal (last value) or list-all-matches values.
Nested `ParseResults` and arbitrary parse-action values make this a rich Python
object, not a JSON-native result type.

## Exceptions and warnings

```python
ParseBaseException(pstr: str, loc: int = 0, msg: str | None = None, elem=None)
ParseException(...)
ParseFatalException(...)
ParseSyntaxException(...)
RecursiveGrammarException(parseElementList)
```

`ParseBaseException` exposes source text, location, message, parser element,
`line`, `lineno`, `col`/`column`, `found`, formatted messages,
`mark_input_line`, and `explain`; it also supplies static/class explanation
helpers. Warning classes are `PyparsingWarning`,
`PyparsingDeprecationWarning`, and `PyparsingDiagnosticWarning`.

`pyparsing.core.Diagnostics`, `__diag__`, `__compat__`, `enable_diag`,
`disable_diag`, and `enable_all_warnings` form the diagnostic/configuration
surface. Some of these are module APIs rather than root `__all__` entries.

## Actions and helper functions

### `pyparsing.actions`

```python
OnlyOnce(method_call); OnlyOnce.reset()
match_only_at_col(n)
replace_with(repl_str)
remove_quotes(s, loc, tokens)
with_attribute(*name_value_pairs, **attributes)
with_class(classname, namespace="")
```

`with_attribute.ANY_VALUE` is the sentinel for requiring an attribute without
fixing its value.

### Root/helper combinators

```python
counted_array(expr, int_expr=None, **kwargs)
match_previous_literal(expr)
match_previous_expr(expr)
one_of(strs, caseless=False, use_regex=True, as_keyword=False, **kwargs)
dict_of(key, value)
original_text_for(expr, as_string=True, **kwargs)
ungroup(expr)
nested_expr(opener="(", closer=")", content=None, ignore_expr=NoMatch, **kwargs)
make_html_tags(tag_str); make_xml_tags(tag_str)
replace_html_entity(s, loc, tokens)
infix_notation(base_expr, op_list, lpar=Suppress("("), rpar=Suppress(")"))
delimited_list(expr, delim=",", combine=False, min=None, max=None,
               *, allow_trailing_delim=False)
condition_as_parse_action(fn, message=None, fatal=False)
null_debug_action(*args)
trace_parse_action(fn)
srange(source)
token_map(func, *args)
autoname_elements()
```

`OpAssoc.LEFT` and `OpAssoc.RIGHT` describe associativity for
`infix_notation`. The old `indentedBlock` and `locatedExpr` functions coexist
with the modern `IndentedBlock` and `Located` classes and are not behaviorally
identical simple aliases.

## Built parser objects and character constants

The root exports character strings `alphas`, `nums`, `alphanums`, `hexnums`,
`printables`, `alphas8bit`, `punc8bit`, `identchars`, and `identbodychars`.
It exports reusable parser objects for line/string boundaries, quoted strings,
Unicode string literals, rest-of-line, empty input, Python/C/C++/Java comments,
HTML comments/entities, and arbitrary opening/closing tags. These are parser
objects and must be copyable/nameable like other elements; they are not factory
functions merely because they are callable for results naming.

## `common`, `unicode`, and `testing` namespaces

### `pyparsing.common` / `pyparsing.pyparsing_common`

The common namespace exposes these built parsers:

```text
integer, signed_integer, hex_integer, fraction, mixed_integer, real,
sci_real, number, fnumber, ieee_float, identifier, comma_separated_list,
ipv4_address, ipv6_address, mac_address, iso8601_date,
iso8601_datetime, iso8601_date_validated, iso8601_datetime_validated,
uuid, url
```

It exposes parse actions/factories:

```text
convert_to_integer, convert_to_float, convert_to_date,
convert_to_datetime, as_datetime, strip_html_tags, upcase_tokens,
downcase_tokens
```

Compatibility spellings (`convertToInteger`, `stripHTMLTags`, etc.) remain
observable and follow the package's deprecation policy.

### `pyparsing.unicode` / `pyparsing.pyparsing_unicode`

`unicode_set` provides class properties `printables`, `alphas`, `nums`,
`alphanums`, `identchars`, `identbodychars`, and `identifier`. The namespace
contains `Latin1`, `LatinA`, `LatinB`, `Greek`, `Cyrillic`, `Chinese`,
`Japanese`, `Hangul`, `Korean`, `CJK`, `Thai`, `Arabic`, `Hebrew`,
`Devanagari`, `BMP`/`BasicMultilingualPlane`, plus native-script aliases for
several sets. Set union composes Unicode ranges.

### `pyparsing.testing` / `pyparsing.pyparsing_test`

```text
TestParseResultsAsserts
reset_pyparsing_context
with_line_numbers(s, start_line=None, end_line=None, expand_tabs=True,
                  eol_mark="|", mark_spaces=None, mark_control=None,
                  *, indent="", base_1=True)
```

The reset context saves/restores whitespace, keyword characters, literal
class, packrat/left-recursion mode and cache policy, diagnostics, and related
global state.

## Optional diagrams

`pyparsing.diagram` requires the `diagrams` extra (`railroad-diagrams` and
`jinja2`). Its direct surface includes:

```python
to_railroad(element, diagram_kwargs=None, vertical=3,
            show_results_names=False, show_groups=False,
            show_hidden=False) -> list[NamedDiagram]
railroad_to_html(diagrams, embed=False, **kwargs) -> str
resolve_partial(partial)
NamedDiagram(name, index, diagram=None)
AnnotatedItem(label, item)
EachItem(*items)
EditablePartial(func, args, kwargs)
ElementState(...)
ConverterState(diagram_kwargs=None)
```

`ParserElement.create_diagram` is the root entry point and raises installation
guidance when the extra is unavailable. It accepts a text stream or writes an
HTML path.

## Tools and module entry points

- `pyparsing.tools.cvt_pyparsing_pep8_names` exposes the `pep8_converter`
  parser, conversion-name tables, and `camel_to_snake`; as a script it scans
  path patterns, prints diffs/status, optionally rewrites files, and uses exit
  status to report required changes.
- `show_best_practices(file=sys.stdout)` reads the bundled Markdown resource,
  prints it by default, or returns it when `file=None`; a built-in fallback is
  used for resource I/O failure.
- `python -m pyparsing.ai.show_best_practices` prints the same guidance.
- The distribution declares no console-script entry point.

## Boundary conclusion

The full inventory is not transparently representable through a stateless JSON
function call. Parser graphs contain callbacks, regex objects, recursive
`Forward` references, exception objects, mutable `ParseResults`, process-global
caches/configuration, and optional diagram objects. A production verifier must
provide a reviewed pyparsing-specific child-side scenario vocabulary; direct
trusted imports are not an acceptable substitute.
