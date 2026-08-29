# Public contract traceability

The private verifier contains 24 fixed leaves. Each leaf starts a fresh
candidate-side process and compares only JSON-safe observations in the trusted
parent. The parent never imports candidate modules and owns the expected
observations. The upstream 981-test run is inventory evidence, not the hidden
denominator.

| Leaf group | Instruction sections | Coverage |
| --- | --- | --- |
| metadata | Supports; Root package and metadata | version, exports, repr, default options |
| rendering | `MarkdownIt` | headings, emphasis, links, blocks, inline mode, tables, escaping |
| parsing | `MarkdownIt`; `Token` | inline children, block token fields, references |
| token-api | `Token` | attributes, copy, upstream serialization, reconstruction, nested children |
| tree | `SyntaxTreeNode` | root/child relationships, traversal, token reconstruction |
| configuration | `MarkdownIt`; rule components | presets, OptionsDict, enable/disable, custom config |
| extension | Renderer and rule components | custom core plugin and renderer subclass |
| safety/helpers | URL methods; CLI and helpers | dangerous URL rejection, URL normalization, entity unescape, CLI args, input errors |

The adapter does not expose expected values to the candidate process and does
not permit the candidate to write trusted reports. The generic Harbor wrapper
creates collection, JUnit, grading, and numeric reward files from the fixed
24-leaf report.
