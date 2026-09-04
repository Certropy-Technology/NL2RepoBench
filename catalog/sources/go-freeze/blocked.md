# go-freeze blocked remediation record

Status: **blocked before Harbor packaging**.

The source is frozen at `f4276107b7b7a1ad33882cb26baf2102f90887b0` from
`https://github.com/charmbracelet/freeze`. The source archive and MIT license
bytes are recorded in `evidence/source-freeze.json` and the source-freeze log.
The upstream Go tests pass in the authoring checkout, including the offline
probe, but that probe uses the authoring machine's pre-existing module cache;
the complete 64-module closure has not been materialized as a private Harbor
artifact.

The primary blocker is verifier fidelity. `freeze` is a `package main` CLI,
not a JSON-safe library. Its tested behavior includes:

- PTY allocation and terminal-size detection through `xpty` and `isatty`;
- `--execute` launching arbitrary external commands and capturing ANSI output;
- an interactive TUI using `huh` and terminal input;
- reading input/config/font files and writing SVG, PNG, and WebP outputs;
- embedded JetBrains Mono font data and optional caller-supplied font files;
- SVG/XML generation and native `resvg` rendering, with optional `rsvg-convert`;
- 29 SVG and 27 PNG golden artifacts across 36 test events.

The current Harbor Go lane requires a reviewed child-side typed bridge. A bridge
that drops TTY, subprocess, interactive, native rendering, or pixel-golden
behavior would test a different product. Directly importing the candidate into
the trusted verifier is prohibited. No runtime projection, Oracle, private
test bundle, or controls were generated.

Reopen only after approving a deterministic CLI/PTY and image-rendering
adapter, freezing the complete Go module closure and required native/font
assets, and defining bounded golden-artifact assertions that remain faithful
to the frozen revision under no-network separate verification.
