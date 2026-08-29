# Jinja Template Engine

Create a complete, installable Python project named `Jinja2` from an empty
workspace. The import package is `jinja2`. Implement the behavior of the
frozen Jinja revision described below without relying on a preinstalled copy
of Jinja or network access at runtime.

## Project Description

Jinja is a Python template engine. It parses templates containing expressions,
statements, filters, tests, macros, imports, inheritance, and comments, then
renders deterministic text from a context. The implementation must also
provide loaders, undefined-value policies, bytecode caching, extensions,
syntax/parser helpers, native-type rendering, asynchronous rendering, and a
sandboxed environment.

## Supports

- Support CPython 3.10 and newer Python 3.x versions in the supported source
  range, with explicit behavior for the running interpreter.
- Use a `src/jinja2/` package layout and normal PEP 517 metadata. The
  distribution name is `Jinja2`, and its version at the frozen revision is
  `3.2.0.dev`.
- Declare `MarkupSafe>=3.0` as the only runtime dependency. Build metadata
  uses `flit_core<4`; runtime code must not invoke pip, git, a subprocess, or
  a network service.
- Install and import successfully when the private verifier tests are absent.
- Keep rendering, parsing, loading, error reporting, and sandbox decisions
  deterministic for the same inputs. FileSystemLoader may read explicitly
  requested local template files; no implicit network or service access is
  allowed.
- Preserve public module names, aliases, exception relationships, generated
  template metadata, ordinary Python data-model behavior, and async semantics.

## API Usage Guide

### Root exports

The following names must be importable from `jinja2`:

`Environment`, `Template`, `TemplateError`, `TemplateNotFound`,
`TemplatesNotFound`, `TemplateSyntaxError`, `TemplateAssertionError`,
`TemplateRuntimeError`, `UndefinedError`, `Undefined`, `ChainableUndefined`,
`DebugUndefined`, `StrictUndefined`, `make_logging_undefined`,
`select_autoescape`, `pass_context`, `pass_environment`, `pass_eval_context`,
`is_undefined`, `clear_caches`, `BaseLoader`, `FileSystemLoader`,
`PackageLoader`, `DictLoader`, `FunctionLoader`, `PrefixLoader`,
`ChoiceLoader`, `ModuleLoader`, `BytecodeCache`, `FileSystemBytecodeCache`,
and `MemcachedBytecodeCache`.

### `jinja2.Environment`

Implement the normal constructor with the standard options, including
`block_start_string`, `block_end_string`, `variable_start_string`,
`variable_end_string`, `comment_start_string`, `comment_end_string`,
`line_statement_prefix`, `line_comment_prefix`, `trim_blocks`,
`lstrip_blocks`, `newline_sequence`, `keep_trailing_newline`,
`extensions`, `optimized`, `undefined`, `finalize`, `autoescape`, `loader`,
`cache_size`, `bytecode_cache`, `enable_async`, `auto_reload`, and
`prettify`. Expose mutable `filters`, `tests`, `globals`, and `policies`
mappings before the environment is used.

Provide these methods with their ordinary Jinja signatures and semantics:
`from_string(source, globals=None, template_class=None)`,
`get_template(name, parent=None, globals=None)`,
`select_template(names, parent=None, globals=None)`,
`get_or_select_template(template_name_or_list, parent=None, globals=None)`,
`from_string`, `compile(source, name=None, filename=None, raw=False,
defer_init=False)`, `parse(source, name=None, filename=None)`,
`lex(source, name=None, filename=None)`, `overlay(**options)`, and
`join_path(template, parent)`. A loaded template is cached according to
`cache_size`; `clear_caches()` clears shared spontaneous-environment caches.

### `jinja2.Template`

Templates are normally returned by `Environment.from_string` or a loader.
They must support `render(*args, **kwargs)`, `generate(*args, **kwargs)`,
`stream(*args, **kwargs)`, `make_module(vars=None, shared=False,
defer_init=False)`, `module`, `blocks`, `name`, `filename`, and `root_render_func`.
With `enable_async=True`, support `render_async`, `generate_async`, and
`make_module_async`; async filters and generators must be awaited or consumed
in order. Rendering accepts at most one positional mapping and keyword
values; later values override earlier context keys as in ordinary Jinja.

### Syntax and rendering language

Support variable output `{{ value }}`, statements `{% ... %}`, comments
`{# ... #}`, whitespace trimming, escaped output via autoescape, dotted and
bracket attribute/item access, literals, arithmetic and comparisons, boolean
operators, conditional expressions, filters, tests, calls, loops with
`loop.index`, `loop.first`, `loop.last`, `loop.cycle`, `else`, recursive
loops, `if`/`elif`/`else`, `set` (including block form), `for`, `with`,
`filter`, `apply`, `macro`, `call`, `include`, `import`, `from ... import`,
`extends`, `block`, `super`, and `self`. Preserve source order and newline
options. Syntax failures raise `TemplateSyntaxError` with `lineno`, `name`,
`filename`, `source`, and a useful `str()` representation.

The built-in filters and tests must include ordinary Jinja behavior for
`upper`, `lower`, `replace`, `default`, `join`, `sort`, `unique`, `map`,
`select`, `reject`, `selectattr`, `rejectattr`, `list`, `first`, `last`,
`length`, `batch`, `slice`, `dictsort`, `indent`, `trim`, `wordcount`,
`escape`/`e`, `safe`, `tojson`, and tests such as `defined`, `undefined`,
`equalto`, `sameas`, `escaped`, `iterable`, `sequence`, `mapping`, and
`callable`. Custom filters, tests, and globals added to the environment must
be visible to subsequent compilation and rendering.

### Loaders and bytecode

`DictLoader(mapping)` loads named strings and lists them. `FunctionLoader`
accepts a callable returning source, `(source, filename, uptodate)`, or
`None`. `ChoiceLoader` tries loaders in order and `PrefixLoader` dispatches
`prefix/name`. `FileSystemLoader(searchpath, encoding="utf-8",
followlinks=False)` reads only paths below its search roots, rejects `..`
segments with `TemplateNotFound`, and reports `list_templates()` in sorted
order. `BaseLoader.get_source` and `list_templates` retain their documented
failure behavior. `PackageLoader` and `ModuleLoader` expose their normal
import/package interfaces for installed resources.

`BytecodeCache`, `Bucket`, `FileSystemBytecodeCache`, and
`MemcachedBytecodeCache` retain their public methods and checksum/version
behavior. Cache hits must not change rendered output.

### Undefined values, safety, and helpers

`Undefined` stringifies as an empty string and raises `UndefinedError` for
unsupported operations. `StrictUndefined` raises on printing, iteration,
boolean conversion, and arithmetic. `DebugUndefined` prints a diagnostic
placeholder. `ChainableUndefined` allows chained lookup until a value is
used. `make_logging_undefined(logger=None, base=Undefined)` returns a
subclass with the documented logging behavior.

`SandboxedEnvironment` and `ImmutableSandboxedEnvironment` live in
`jinja2.sandbox`. They reject unsafe attributes/callables and raise
`SecurityError` for blocked operations. `is_internal_attribute`,
`modifies_known_mutable`, `safe_range`, and the sandbox environment hooks
remain usable. `select_autoescape` returns a deterministic callback based on
enabled/disabled extensions and `default_for_string`.

`jinja2.meta.find_undeclared_variables` and
`find_referenced_templates` inspect parsed ASTs. `jinja2.nativetypes`
provides `NativeEnvironment`, `NativeTemplate`, and `native_concat` so a
single literal can retain a native Python type while multi-value output joins
as text. `jinja2.ext` exposes `Extension`, `do`, `i18n`, `loopcontrols`, and
`debug`; extension tags may add filters, globals, and parser nodes.

### Exceptions and compatibility

Expose `TemplateNotFound` as an `IOError`/`LookupError`/`TemplateError`
compatible exception with `name`, `message`, and `templates` attributes.
`TemplatesNotFound` is its multi-name subclass. `TemplateSyntaxError` and
`TemplateAssertionError` retain line/name/filename/source attributes;
`TemplateRuntimeError`, `UndefinedError`, `SecurityError`, and
`FilterArgumentError` preserve their relationships and messages.

## Implementation Notes

- This is a repository-generation task: start with an empty workspace and
  provide packaging, source modules, and typing marker as a complete project.
- Keep public imports compatible with the module layout: environment, runtime,
  loaders, filters, lexer, parser, nodes, compiler, sandbox, meta, ext,
  nativetypes, bccache, debug, constants, defaults, utils, and async_utils.
- Do not copy the upstream implementation or its tests into the answer. The
  hidden verifier checks independent behavior through a bounded child-process
  adapter, including packaging metadata and no-network execution.
- Favor normal Python protocols and informative exceptions. Preserve ordering,
  escaping, undefined behavior, loader path safety, async output order, and
  deterministic repr/metadata.
