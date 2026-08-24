# Build `lark`

Create a complete, installable Python package named `lark` from an empty
workspace. Lark is a general-purpose context-free grammar toolkit. A caller
writes an EBNF-like grammar, selects a parsing algorithm and lexer, parses text
or bytes, and receives a tree, an ambiguity forest, or a value produced by a
transformer. The implementation must be a real multi-module repository, not a
single-function facade or a wrapper around an installed copy of Lark.

## Project Description

The package must expose the frozen Lark 1.3.1 behavior described here. It is a
library first, with optional Python-module tools for standalone parser
creation, parser-state serialization, and Nearley grammar conversion. The
normal library path is local and deterministic: it must not fetch grammars,
packages, or services at runtime.

A valid implementation can parse ordinary deterministic grammars, ambiguous
context-free grammars, grammars with templates and imports, byte input, and
Unicode text. It must construct source-position metadata, report useful
lexing/parsing errors, and allow callers to process results with visitors and
transformers.

## Supports

- Support CPython 3.8 and newer Python 3.x versions. The final package must
  import on the selected interpreter without relying on PyPy-specific or
  platform-specific behavior.
- Use an installable package layout containing `lark/`, its `parsers/`,
  `tools/`, `grammars/`, and `__pyinstaller/` subpackages. Include the four
  built-in `.lark` grammar resources (`common.lark`, `lark.lark`,
  `python.lark`, and `unicode.lark`) and the `py.typed` marker.
- Expose package version `lark.__version__ == "1.3.1"` and the root names in
  the following order:

  ```text
  GrammarError, LarkError, LexError, ParseError, UnexpectedCharacters,
  UnexpectedEOF, UnexpectedInput, UnexpectedToken, Lark, Token, ScanMatch,
  ParseTree, Tree, logger, Discard, Transformer, Transformer_NonRecursive,
  TextSlice, Visitor, v_args
  ```

- Declare no third-party runtime dependency. The standard library is enough
  for the normal parser, tree, visitor, lexer, cache, and grammar-resource
  paths.
- Treat these as optional feature dependencies, not mandatory runtime
  imports: `regex` for advanced regular expressions, `interegular` for regex
  collision analysis and strict-mode diagnostics, `atomicwrites` for atomic
  cache writes, `pydot` for tree/forest graph output, `rich` for rich tree
  display, and `Js2Py==0.68` plus a checked-out Nearley grammar repository for
  the Nearley converter. Absence of an optional package must not break the
  ordinary import path; a requested feature must fail with its documented
  import or configuration error.
- Build and install without the evaluator tests being present. Runtime tests
  and examples supplied by the evaluator are not package data and must not be
  required for import.
- Work offline after installation. Do not download grammars, invoke a package
  manager, call a network service, or silently import a preinstalled `lark`
  distribution.

## API Usage Guide

### Root package and public modules

`import lark` must initialize the logger and re-export the root API listed in
`Supports`. The corresponding objects imported through their defining modules
must be identical to the root re-exports where both paths are provided. In
particular, `lark.Lark`, `lark.Tree`, `lark.Token`, `lark.Transformer`,
`lark.Visitor`, `lark.Discard`, `lark.TextSlice`, and the exception classes must
not be unrelated duplicate implementations.

The following modules are part of the supported package surface when their
names are used in the signatures below:

```text
lark.ast_utils
lark.common
lark.exceptions
lark.grammar
lark.indenter
lark.lark
lark.lexer
lark.load_grammar
lark.parser_frontends
lark.parsers.earley_forest
lark.parsers.lalr_interactive_parser
lark.reconstruct
lark.tree
lark.tree_matcher
lark.tree_templates
lark.utils
lark.visitors
lark.tools
lark.tools.nearley
lark.tools.serialize
lark.tools.standalone
```

Do not expose private helpers merely because they happen to exist in the
source. Names explicitly documented below are the application-facing contract;
internal parser state may be represented differently as long as observations
through this contract agree.

### `Lark` parser object

Construct a parser with:

```python
Lark(grammar, **options)
```

`grammar` may be a grammar string, a text file-like object with `read()`, or a
compiled `Grammar` object from `lark.load_grammar`. The default start rule is
`start`. A parser instance is reusable: parsing one input must not mutate its
grammar or make a later parse depend on the previous input, except for the
explicit persistent cache file requested by the caller.

The supported options and defaults are:

```text
parser="earley"
lexer="auto"
start="start"              # a string or a list of start rule names
ambiguity="auto"
priority="auto"
debug=False
strict=False
transformer=None
propagate_positions=False
maybe_placeholders=True
keep_all_tokens=False
tree_class=None
postlex=None
cache=False
cache_grammar=False
regex=False
g_regex_flags=0
lexer_callbacks={}
use_bytes=False
ordered_sets=True
edit_terminals=None
import_paths=[]
source_path=None
_plugins={}
```

Important option rules:

- `parser` accepts `"earley"`, `"lalr"`, `"cyk"`, or `None` for lexer-only
  operation. Earley supports `basic`, `dynamic`, and `dynamic_complete`
  lexers; LALR supports `basic` and `contextual`; CYK uses `basic`.
- With `lexer="auto"`, Earley selects `dynamic` unless a post-lexer requires
  `basic`, LALR selects `contextual`, and CYK selects `basic`.
- Earley supports `ambiguity="resolve"`, `"explicit"`, or `"forest"`.
  `resolve` chooses one derivation, `explicit` returns `_ambig` tree nodes,
  and `forest` returns the shared packed parse forest. Ambiguous results and
  priority handling must be deterministic for a fixed interpreter and input.
- `strict=True` is currently meaningful for LALR. It must reject shift/reduce
  conflicts and, when collision analysis is requested, requires
  `interegular`; without it, raise an informative `LexError` or
  `ConfigurationError` rather than silently claiming strict validation.
- `regex=True` selects the optional `regex` module. If it is unavailable,
  constructing a parser with this option raises `ImportError`. With the option
  disabled, use the standard-library `re` behavior.
- `transformer` applies callbacks during LALR parsing. An embedded transformer
  with Earley is invalid and raises `ConfigurationError`; callers can instead
  transform the returned tree.
- `cache=True` or a cache path is supported for LALR grammar analysis. A string
  is a specific cache path; `True` chooses a deterministic temporary name from
  the grammar, options, package version, and Python major/minor version.
  `cache_grammar=True` is only valid with caching enabled. Cache reads must
  validate the grammar/import file digest and recover by rebuilding if the
  cache is missing or stale. `atomicwrites`, when installed, may be used for
  writes; otherwise ordinary safe file writing is sufficient.
- `propagate_positions=True` records source ranges on tree metadata. A callable
  value may filter which nodes receive positions. `maybe_placeholders` controls
  whether an unmatched bracketed item produces `None` or no child.
- `use_bytes=True` accepts bytes input and requires an ASCII grammar. Grammar
  text containing non-ASCII characters with this option must raise
  `ConfigurationError`.
- Unknown options and invalid parser/lexer/ambiguity/priority combinations
  must raise `ConfigurationError`, which is also a `ValueError`.

The main methods are:

```python
parser.parse(text, start=None, on_error=None)
parser.parse_interactive(text=None, start=None)
parser.lex(text, dont_ignore=False)
parser.scan(text, start=None)
parser.get_terminal(name)
parser.save(file_object, exclude_options=())
Lark.load(file_object)
Lark.open(grammar_filename, rel_to=None, **options)
Lark.open_from_package(package, grammar_path, search_paths=[""], **options)
```

`parse` consumes the complete input and returns a `Tree` by default, or the
value returned by an embedded transformer. `start` selects one start rule when
several were configured. `on_error` is only supported by LALR: it receives an
`UnexpectedInput` exception and may return true to resume or false to re-raise.

`parse_interactive` is LALR-only. It returns an `InteractiveParser` that keeps
parser and lexer state and supports incremental token feeding, copying,
lookahead inspection, EOF feeding, and resuming automated parsing. Calling it
with an unsupported parser raises `ConfigurationError`.

`lex` yields `Token` objects for lexer-only inspection. By default ignored
terminals are omitted; `dont_ignore=True` includes them. It accepts `str`,
`bytes`, or a `TextSlice` for built-in lexers. `scan` is LALR-only and requires
no post-lexer or custom lexer. It searches for non-overlapping, greedily
longest matches and silently skips positions that do not begin a valid parse.
A callback that drops source positions must produce a clear `LexError`; a
callback that raises `ValueError` skips that candidate, while other exceptions
propagate.

`get_terminal(name)` returns the corresponding `TerminalDef` and raises
`KeyError` for an unknown terminal. `save`/`load` serialize LALR parser state
using the package's safe structured serializer rather than requiring pickle;
callbacks and other explicitly excluded options are restored from the caller's
load options.

### Grammar language

Grammar text is line-oriented. Rule names are lower case and terminal names
are upper case. A rule has the form `name: expression`, while terminals may be
literals, regular expressions, ranges, or combinations of terminals. Support:

- string literals, `/regular expression/`, case-insensitive literals and regex
  flags `i`, `m`, `s`, `l`, `u`, and `x`;
- grouping with parentheses; optional `?`, repetition `*` and `+`, exact and
  bounded repetition `~ n` and `~ n..m`; alternatives with `|`; aliases with
  `-> alias`; and signed rule/terminal priorities;
- comments beginning with `//` or `#`;
- grammar templates such as `_separated{x, sep}: x (sep x)*` and their use in
  rules and terminals;
- `%ignore` for discarded whitespace/comments;
- `%import` of built-in grammars and relative `.lark` files, including renamed
  rules/terminals and grouped imports;
- `%declare` for an externally supplied terminal, `%override` for replacing an
  imported definition, and `%extend` for adding an alternative; and
- built-in `common`, `lark`, `python`, and `unicode` grammar resources.

The grammar compiler must report undefined rules/terminals, malformed escapes,
invalid ranges, bad repetition bounds, illegal terminal recursion, import
cycles or missing files, and invalid directives with `GrammarError` or the
specific parse/lex error type documented by the public API.

Tree construction follows these rules:

- Each matched rule normally creates `Tree(rule_name, children)`; an alias uses
  the alias as the data name.
- Unnamed string literals and names beginning with `_` are filtered from the
  children. Named terminals beginning with a letter remain as `Token` values.
- A rule beginning with `!` retains its literals. A rule beginning with `_` is
  inlined. A rule beginning with `?` is inlined when it has one surviving
  child. Repetition produces lists; optional `?` produces no child, and
  bracketed optional items produce `None` when `maybe_placeholders=True`.
- Terminal priority, theoretical regex width, pattern length, and name provide
  stable tie-breaking for the basic/contextual lexer. Earley dynamic lexing
  must preserve its documented greedy or complete-ambiguity behavior.
- `%ignore` terminals are consumed but do not appear in the tree. Position
  metadata still accounts for ignored and inlined symbols when the relevant
  propagation option is enabled.

### `Tree`, metadata, tokens, and slices

Construct a tree with:

```python
Tree(data, children, meta=None)
```

`data` is the rule or alias name and `children` is an ordered list of trees,
tokens, or application values. `meta` is optional; accessing `tree.meta` lazily
creates a `Meta` object whose `empty` flag is initially true. Position fields
may include `line`, `column`, `end_line`, `end_column`, `start_pos`, `end_pos`,
and the corresponding `container_*` fields. Tree equality and hashing are
based on `data` and children, not incidental metadata. `repr(tree)` must be
runnable for ordinary trees. Preserve copy, deepcopy, pickle, and structural
pattern-matching behavior.

Provide these tree methods:

```python
pretty(indent_str="  ")
iter_subtrees()
iter_subtrees_topdown()
find_pred(predicate)
find_data(data)
find_token(token_type)
expand_kids_by_data(*data_values)
scan_values(predicate)
copy()
set(data, children)
```

`iter_subtrees` is depth-first bottom-up and must not return the same DAG node
more than once. `iter_subtrees_topdown` is breadth-first/top-down. `find_token`
recursively selects `Token` children by type. `expand_kids_by_data` inlines
matching child trees in place and reports whether it changed anything.

`Token` is a `str` subclass with this constructor:

```python
Token(
    type, value, start_pos=None, line=None, column=None,
    end_line=None, end_column=None, end_pos=None,
)
```

It exposes `type`, `value`, and all six optional source-position fields. The
string value and `value` agree for ordinary string tokens. `Token(type_=...)`
and `update(type_=...)` remain accepted with a deprecation warning, but mixing
`type` and `type_` is an error. `update(type=None, value=None)` returns a new
token retaining source positions; `Token.new_borrow_pos(type_, value,
borrow_token)` copies positions from another token. Token equality compares
string content, except two tokens with different types are unequal; positions
do not affect equality or hashing. `repr` includes the type and value.

`TextSlice(text, start, end)` is an immutable view over a `str` or `bytes`
input. Negative bounds are resolved relative to the input, and invalid types
or bounds raise the documented `TypeError`/`AssertionError`. It supports the
slice-like operations needed by lexers (`count`, `rindex`, indexing/length,
and conversion to complete text) without copying the whole input.

`ScanMatch` is an immutable record with `range=(start, end)` and `value`.

### Exceptions and error details

Expose these classes and inheritance relationships:

```text
LarkError
  ConfigurationError (also ValueError)
  GrammarError
  ParseError
  LexError
  UnexpectedInput
    UnexpectedEOF (also ParseError)
    UnexpectedCharacters (also LexError)
    UnexpectedToken (also ParseError)
  VisitError
  MissingVariableError
```

`UnexpectedInput` exposes `line`, `column`, `pos_in_stream`, parser state where
available, and `get_context(text, span=40)`. For text it marks the error with a
caret; for bytes it returns an ASCII-safe representation. `match_examples`
may compare an error against malformed examples and returns the best label.
`UnexpectedEOF` exposes expected terminals; `UnexpectedCharacters` exposes the
bad character, allowed/considered terminals, prior token history, and context;
`UnexpectedToken` exposes the offending token, expected set, considered rules,
accepted terminals, interactive parser, and token history. Their string forms
must include useful line/column and expected-token information and must not
leak an internal traceback for an ordinary parse failure.

`VisitError(rule, obj, orig_exc)` wraps an exception raised by a visitor or
transformer callback and preserves the rule name, object, and original
exception. `MissingVariableError` is used when a tree template references an
unbound variable.

### Visitors and transformers

`lark.visitors` provides `Discard`, `Visitor`, `Visitor_Recursive`,
`Interpreter`, `Transformer`, `InlineTransformer`, `TransformerChain`,
`Transformer_InPlace`, `Transformer_NonRecursive`,
`Transformer_InPlaceRecursive`, `merge_transformers`, `visit_children_decor`,
and `v_args`.

A `Visitor` walks bottom-up; `visit_topdown` walks from root to leaves.
`Visitor_Recursive` has the same observable order using recursion. A visitor
method named after a tree rule receives the tree; `__default__` handles other
rules. `Interpreter` is top-down and may call `visit_children(tree)` to control
subtree traversal; `visit_children_decor` adapts a callback that wants the
children result.

A `Transformer` transforms children before invoking a method named after the
rule. Rule callbacks normally receive one list of transformed children and
return a replacement value. Token callbacks receive one token. Missing rule
callbacks use `__default__(data, children, meta)` to create a tree; missing
Token callbacks use `__default_token__(token)` to return the token. Returning
`Discard` removes that result from its parent. Callback exceptions are wrapped
in `VisitError`, except the grammar errors explicitly allowed to propagate.

`Transformer_InPlace` is non-recursive and mutates trees; `Transformer_NonRecursive`
returns a transformed copy without recursive Python calls;
`Transformer_InPlaceRecursive` mutates recursively. Transformers compose with
`a * b` and `TransformerChain`. `merge_transformers(base_transformer=None,
**transformers_to_merge)` installs methods under `prefix__method` names and
rejects collisions.

`v_args(inline=False, meta=False, tree=False, wrapper=None)` and class-level
`@v_args` alter callback arguments. `inline=True` passes children as positional
arguments, `meta=True` adds the tree metadata, and `tree=True` passes the whole
tree. A per-method decorator overrides a class setting. Static methods,
class methods, partials, callable objects, and descriptors used as callbacks
must retain their normal binding behavior.

### Forest and ambiguity transformation

`lark.parsers.earley_forest` exposes the shared packed forest node types and
`ForestVisitor`, `ForestTransformer`, `ForestSumVisitor`, `ForestToParseTree`,
`TreeForestTransformer`, and `handles_ambiguity`. Forest visitors must detect
cycles, visit packed/symbol/intermediate/token nodes, and preserve child order.
`TreeForestTransformer` has constructor options `tree_class=Tree`,
`prioritizer=ForestSumVisitor()`, `resolve_ambiguity=True`, and `use_cache=False`.
Rule methods receive transformed children; token methods receive a token;
methods decorated with `handles_ambiguity` receive all derivations. The
`__default__`, `__default_ambig__`, and `__default_token__` hooks construct
ordinary trees, `_ambig` trees, or unchanged tokens. `Discard` removes a forest
result.

### Lexer, grammar, and indentation helpers

The supported lower-level classes include `Pattern`, `PatternStr`, `PatternRE`,
`TerminalDef`, `LineCounter`, `Lexer`, `BasicLexer`, and `ContextualLexer` in
`lark.lexer`; `Symbol`, `Terminal`, `NonTerminal`, `RuleOptions`, and `Rule` in
`lark.grammar`; and `LexerConf`/`ParserConf` in `lark.common`.

Patterns expose their value/flags and `to_regexp`, `min_width`, and `max_width`.
A `TerminalDef(name, pattern, priority=0)` retains its terminal name, pattern,
and priority. `LineCounter` starts at line 1/column 1 and updates positions as
text or bytes tokens are fed. Built-in lexers yield source-positioned tokens,
respect callbacks, ignored terminals, terminal priorities, and bytes input.

`Indenter` is an abstract post-lexer with `process(stream)` and the abstract
properties `NL_type`, `OPEN_PAREN_types`, `CLOSE_PAREN_types`, `INDENT_type`,
`DEDENT_type`, and `tab_len`. It tracks parenthesis nesting, emits indent and
dedent tokens after newline tokens, and raises `DedentError` for an indentation
level that does not match a prior level. `PythonIndenter` supplies Python-style
names and an eight-space tab width.

`lark.load_grammar` must provide the documented grammar-loader helpers,
including `FromPackageLoader`, `find_grammar_errors`, `list_grammar_imports`,
`load_grammar`, `verify_used_files`, `eval_escaping`, `symbol_from_strcase`,
and `sha256_digest`. Loaders must support relative package resources and
custom import path callbacks without reading outside the caller's requested
paths.

### Reconstruction and AST helpers

`Reconstructor(parser, term_subs=None)` in `lark.reconstruct` reconstructs source
text from a complete parse tree. Its method is:

```python
reconstruct(tree, postproc=None, insert_spaces=True)
```

It must restore discarded literal terminals, aliases, repetitions, inlined
rules, and whitespace needed for a grammar to parse the reconstructed result.
Regex terminals cannot be regenerated automatically; `term_subs` supplies
callables for such terminals. `postproc` can transform the emitted iterable.

`lark.ast_utils` provides marker classes `Ast`, `AsList`, and `WithMeta`,
`camel_to_snake(name)`, and `create_transformer(ast_module, transformer=None,
decorator_factory=v_args)`. The factory finds public `Ast` subclasses,
converts class names to snake case, and creates callbacks with list/meta
arguments according to the marker bases.

`lark.tree_templates` provides `TemplateConf(parse=None)`, `Template(tree,
conf=TemplateConf())`, `TemplateTranslator(translations)`, and `translate(t1,
t2, tree)`. A template variable is a string beginning with `$` or a `var` tree
whose first child is such a string. `Template.match` returns a variable-to-tree
mapping or `None`; `search` yields matching subtrees; `apply_vars` replaces all
variables and raises `MissingVariableError` for missing or unused mappings;
`translate` applies a template replacement in place.

### Utility and serialization helpers

`lark.utils` provides `classify`, `get_regexp_width`, `is_id_continue`,
`is_id_start`, `dedup_list`, `combine_alternatives`, `classify_bool`, `bfs`,
`bfs_all_unique`, `small_factors`, `OrderedSet`, `fzset`, `Enumerator`,
`Serialize`, `SerializeMemoizer`, `FS`, and `TextSlice`. Preserve deterministic
ordering where the helper's return type is ordered. `Serialize` must encode
only declared fields and permitted classes, support memoized shared objects,
and reject unknown serialized classes rather than importing arbitrary code.

### Optional tools

The following module-level tools are part of the supported behavior:

- `python -m lark.tools.standalone` generates a standalone LALR parser from a
  grammar file. `gen_standalone(lark_instance, output=None, out=sys.stdout,
  compress=False)` emits a self-contained module with `Lark_StandAlone`,
  serialized parser data, and compatible `Tree`, `Token`, transformer, and
  error behavior. The standalone source and generated code carry the separate
  Mozilla Public License notice present in the upstream source; do not silently
  relicense that path as MIT.
- `lark.tools.serialize.serialize(lark_instance, outfile)` writes JSON parser
  data and `python -m lark.tools.serialize` exposes the corresponding command.
- `create_code_for_nearley_grammar(grammar, start, builtin_path, folder_path,
  es6=False)` and `lark.tools.nearley.main(fn, start, nearley_lib, es6=False)`
  convert Nearley grammar text and JavaScript postprocessors into Python source.
  The converter requires `Js2Py` and a compatible Nearley repository with its
  `builtin` and example grammar files. It supports imports and UTF-8 input but
  does not support Nearley templates or exporting a Lark grammar to Nearley.

Missing optional tools must produce a clear import/configuration failure or,
where the source contract explicitly treats a test as optional, a controlled
skip. They must not make `import lark` fail.

## Implementation Notes

- Preserve deterministic grammar compilation, terminal ordering, alternative
  selection, ambiguity resolution, tree child order, source positions, cache
  keys, serialization output, and error expectation ordering for a fixed
  interpreter and input.
- Keep parser instances reusable and avoid mutating caller-owned grammar text,
  tree children, token positions, transformer objects, or custom lexer state
  except where an explicitly in-place API promises mutation.
- Support ordinary `str`, `bytes`, `TextSlice`, file-like grammar sources,
  custom lexer input, Unicode literals, escaped characters, multiline regexes,
  and arbitrary user values returned by transformers.
- Preserve public signatures, aliases, generic type annotations where they are
  observable, class attributes such as `__match_args__`, and pickling/copying
  protocols. Include package data in wheels and sdists.
- Normal library operation must not use the network or subprocesses. File
  access is limited to explicit grammar/resource/cache paths supplied by the
  caller. Do not use a system-installed Lark as a fallback.
- Do not copy the upstream implementation, upstream test files, hidden
  assertions, or complete algorithm listings into the public instruction. The
  evaluator supplies its own tests; self-authored smoke tests are optional and
  must not be required for installation.
