# Project Description

Create an installable Python project named `Jinja2` with import package
`jinja2`. It is a deterministic template engine: environments parse templates
with expressions and statements, loaders provide source text, and templates
render synchronous or asynchronous output. The project also includes undefined
policies, escaping, sandbox decisions, native rendering, metadata analysis,
extensions, and bytecode cache interfaces.

# Natural Language Instruction

From an empty workspace implement the documented Jinja2 public surface without
using a preinstalled Jinja or runtime network. Provide packaging and typing
metadata, root exports, environment/template lifecycle, the core template
language, loaders, undefined classes, sandbox, native helpers, extensions, and
cache APIs. Preserve source order, escaping, exception relationships, async
ordering, loader path safety, and deterministic rendering. Do not copy
reference source or tests.

# Supports or Environment Configuration

- CPython 3.10+; evaluation uses Python 3.12 on Linux.
- Distribution `Jinja2`, version `3.2.0.dev`; import package `jinja2`.
- Use a `src/jinja2/` package layout and PEP 517 metadata. Runtime dependency
  is `MarkupSafe>=3.0`; `flit_core<4` is build-only.
- FileSystemLoader may read explicitly requested local files. No runtime pip,
  git, subprocess, network, current time, or user-specific service is allowed.
- Agent, candidate, verifier, Oracle, and controls run no-network.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
├── README.md
├── LICENSE.txt
└── src/
    └── jinja2/
        ├── __init__.py
        ├── py.typed
        ├── environment.py
        ├── runtime.py
        ├── loaders.py
        ├── filters.py
        ├── lexer.py
        ├── parser.py
        ├── nodes.py
        ├── compiler.py
        ├── sandbox.py
        ├── meta.py
        ├── ext.py
        ├── nativetypes.py
        ├── bccache.py
        ├── debug.py
        ├── constants.py
        ├── defaults.py
        ├── utils.py
        └── async_utils.py
```

# API Usage Guide

Root imports must include `Environment`, `Template`, `TemplateError`,
`TemplateNotFound`, `TemplatesNotFound`, `TemplateSyntaxError`,
`TemplateAssertionError`, `TemplateRuntimeError`, `UndefinedError`,
`Undefined`, `ChainableUndefined`, `DebugUndefined`, `StrictUndefined`,
`make_logging_undefined`, `select_autoescape`, the `pass_*` decorators,
`is_undefined`, `clear_caches`, `BaseLoader`, `FileSystemLoader`,
`PackageLoader`, `DictLoader`, `FunctionLoader`, `PrefixLoader`, `ChoiceLoader`,
`ModuleLoader`, `BytecodeCache`, `FileSystemBytecodeCache`, and
`MemcachedBytecodeCache`.

```python
Environment(...)
Environment.from_string(source, globals=None, template_class=None)
Environment.get_template(name, parent=None, globals=None)
Environment.select_template(names, parent=None, globals=None)
Environment.compile(source, name=None, filename=None, raw=False, defer_init=False)
Template.render(*args, **kwargs)
Template.generate(*args, **kwargs)
Template.stream(*args, **kwargs)
```

`Environment` accepts the standard delimiter, whitespace, `extensions`,
`undefined`, `finalize`, `autoescape`, `loader`, cache, bytecode, and async
options. Its `filters`, `tests`, `globals`, and `policies` mappings are
mutable before use. It can parse/lex/compile source and load or select named
templates. `overlay(**options)` creates an environment variant. `Template`
supports rendering, generation, streaming, module creation, metadata, and the
async counterparts when `enable_async=True`; one positional mapping plus
keywords forms the render context.

The language includes variable output, comments, expressions, filters/tests,
conditionals, loops and loop metadata, macros/call, set/with/filter, include,
import, inheritance, blocks, `super`, escaping, and whitespace controls.
Syntax errors expose line/name/filename/source context through
`TemplateSyntaxError`.

`DictLoader`, `FunctionLoader`, `ChoiceLoader`, `PrefixLoader`, and
`FileSystemLoader` load source text; filesystem paths must remain under the
configured roots and listing is sorted. `BytecodeCache`, `Bucket`, and the
filesystem/memcached cache classes retain public methods and checksum/version
behavior. Undefined variants implement empty, strict, diagnostic, and
chainable policies. `SandboxedEnvironment` rejects unsafe attributes/calls;
`select_autoescape`, `meta.find_undeclared_variables`,
`meta.find_referenced_templates`, `NativeEnvironment`, `NativeTemplate`,
`native_concat`, and `ext.Extension` are importable and functional.

# Implementation Notes

Keep module import paths and root re-exports compatible. Custom filters, tests,
globals, loaders, extensions, and async generators must be observed in later
operations. Keep output ordering and newline options stable; preserve normal
exception inheritance and metadata. Do not expose implementation-only files
as required agent files beyond the listed public modules.

# Examples

```python
from jinja2 import Environment

env = Environment()
template = env.from_string("Hello {{ name|upper }}")
assert template.render(name="Ada") == "Hello ADA"
```

```python
from jinja2 import DictLoader, Environment

env = Environment(loader=DictLoader({"base": "{% block body %}{% endblock %}"}))
assert env.get_template("base").render() == ""
```

# Error Handling and Boundary Conditions

- `StrictUndefined` raises `UndefinedError` when printed, iterated, converted
  to bool, or used arithmetically; ordinary `Undefined` stringifies empty.
- `FileSystemLoader` rejects traversal outside configured roots with
  `TemplateNotFound` and reports sorted names.
- Sandbox operations that are not safe raise `SecurityError`.
- Syntax failures preserve useful line and source metadata; async output keeps
  source order.
- Rendering and loading must remain deterministic and no-network.
