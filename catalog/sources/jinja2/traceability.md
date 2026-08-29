# Jinja2 Traceability

| Public contract | Private leaf IDs |
| --- | --- |
| Root exports and distribution metadata | `exports`, `metadata` |
| Basic interpolation, expressions, escaping, whitespace | `basic-render`, `expression`, `escape`, `trim-blocks` |
| Statements, loops, conditionals, set, macros, call | `if-loop`, `loop-meta`, `set-block`, `macro`, `call-block` |
| Filters, tests, custom globals and filters | `filters`, `tests`, `custom-filter`, `custom-test` |
| Undefined classes and exceptions | `undefined`, `strict-undefined`, `chainable-undefined`, `syntax-error` |
| Environment options and template methods | `environment-options`, `generate`, `stream`, `overlay` |
| Dict/function/file/prefix/choice loaders and safety | `dict-loader`, `function-loader`, `filesystem-loader`, `loader-path`, `composed-loaders` |
| Bytecode and template metadata | `bytecode`, `template-metadata` |
| Async rendering and async filters | `async-render`, `async-generate`, `async-filter` |
| Sandbox and security errors | `sandbox-attribute`, `sandbox-call`, `sandbox-mutable` |
| Meta, native types, and helpers | `meta`, `native`, `autoescape`, `utils` |

The specification states each behavior exercised by these leaves without
revealing the frozen source revision, private scenario code, or expected-value
table.
