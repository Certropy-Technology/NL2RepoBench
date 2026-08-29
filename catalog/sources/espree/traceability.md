# Espree contract traceability

The public instruction describes the package root, parser options, token and
comment metadata, version helpers, JSX mode, and deterministic error fields.
The private 24-leaf contract exercises each of those behaviors through the
JSON child adapter. Upstream inventory was taken from the frozen
`packages/espree` package and its 12 `tests/lib/*` test files (135 `it` cases).

The task intentionally scores a bounded JSON-compatible slice rather than
copying all upstream fixtures or exposing callbacks and process-local parser
classes. The Oracle uses the same frozen revision and dependencies, while the
candidate is installed from the private npm closure and tested in a separate
UID-isolated subprocess.
