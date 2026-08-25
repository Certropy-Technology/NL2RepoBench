# Build a pure-Go text utility

Create the single module `example.com/go-synthetic` with a public package
`textx` and exported function `Normalize(value string) string`. The function
returns the input with surrounding ASCII whitespace removed and must be
callable through the verifier's typed JSON subprocess bridge. Use no cgo,
external services, workspaces, or replace directives.
