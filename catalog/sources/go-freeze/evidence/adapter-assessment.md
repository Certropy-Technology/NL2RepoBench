# Adapter assessment

Command: static Go source, test, and dependency inventory plus typed-bridge
assessment at revision `f4276107b7b7a1ad33882cb26baf2102f90887b0`.

Assessment result: blocked. The upstream entry point is `package main` and the
test suite launches a built executable with `os/exec`. The functional surface
requires all of the following boundaries:

| Boundary | Frozen behavior | Current contract gap |
| --- | --- | --- |
| TTY and PTY | `xpty.NewPty`, terminal dimensions, ANSI capture, `isatty` | No reviewed deterministic PTY child adapter or terminal-size contract |
| Interactive mode | `huh.NewForm().Run()` reads terminal input | No bounded JSON representation of TUI interaction |
| External process | `exec.CommandContext` runs a shell-parsed command | Arbitrary child commands and ANSI timing are outside the typed bridge |
| Filesystem | input/config/font reads and output writes | Golden fixtures and output tree need a task-specific filesystem adapter |
| Rendering | Chroma, etree, embedded fonts, `resvg`, optional `rsvg-convert` | Native/image dependencies and exact raster output are not in the current Go lane |
| Golden tests | 29 SVG and 27 PNG artifacts, with 36 test events | A reduced JSON contract would omit the primary tested product behavior |

The source has no cgo imports, but `github.com/kanrichan/resvg-go` still
introduces native rendering behavior and the executable can invoke the external
`rsvg-convert` binary. The repository contains 64 Go modules, 16 direct
requirements in `go.mod`, and 113 tracked files including font and golden image
assets.

Conclusion: do not create a Harbor task with a narrowed bridge or trusted
direct import. The minimum remediation is to approve a deterministic CLI/PTY
adapter, freeze the module and native/font closure, and define bounded SVG/PNG
golden comparisons in a separate verifier.
