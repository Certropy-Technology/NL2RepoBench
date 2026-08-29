# `lines-and-columns` Traceability

| Published contract | Private bridge behavior | Leaves |
| --- | --- | ---: |
| package name/version, ESM and CommonJS root export | package metadata and named class inventory | 1 |
| single-line and LF line starts | `locationForIndex` and `indexForLocation` calls | 9 |
| CR, LF, and joined CRLF semantics | index probes around each newline code unit | 9 |
| empty lines, trailing newline, UTF-16 columns | empty/trailing/emoji fixtures | 6 |
| null for invalid line, column, and index | bounded invalid-location probes | 7 |
| stable inverse mapping | deterministic repeated calls and valid-position round trips | 2 |

The adapter accepts only fixed operation names (`inventory`, `location`, and
`index`) and a package name fixed to `lines-and-columns`. It accepts no source
code, module specifier, command, host, port, filesystem path, callback, or
candidate-supplied report. The original Jest suite is represented by the
behavioral slice above; Jest tooling and TypeScript compilation internals are
outside the task boundary.
