# Headless Scope And Traceability

This repair deliberately freezes a reproducible headless contract before
collecting Oracle evidence. The upstream project has terminal rendering,
platform console, mouse, clipboard, and live event-loop behavior whose output
depends on a real TTY or OS-specific facilities. Those behaviors cannot be
fairly scored in this Linux separate-verifier environment without a separately
frozen terminal adapter and platform matrix.

The private verifier has nine fixed leaves, each mapped to public instruction
sections:

| Leaf | Public contract |
| --- | --- |
| `api-surface-and-packaging` | Supports and Root API |
| `document-cursor-lines-and-search` | Documents and Buffers |
| `buffer-editing-undo-readonly-and-apply-completion` | Documents and Buffers |
| `completion-data-model` | Completion |
| `word-completion-case-and-sentence-rules` | Completion |
| `nested-and-deduplicated-completion-order` | Completion |
| `in-memory-history-clipboard-and-selection-data` | History, Clipboard, and Validation Data |
| `validator-data-and-buffer-cursor-placement` | History, Clipboard, and Validation Data |
| `key-binding-prefix-longest-match-and-any` | Headless Key Bindings |

Every assertion is evaluated through a fresh unprivileged child adapter. The
trusted verifier only compares bounded JSON observations and writes the
collection/JUnit/reward artifacts. No trusted hidden test imports candidate
modules. The key-binding leaf creates only `PipeInput` and `DummyOutput`; it
does not run `Application.run()` or render terminal bytes.

Excluded behavior is explicitly documented in `instruction.md`: terminal
escape rendering, raw/cooked mode restoration, sizing, mouse input, native
Windows console paths, system clipboard integration, SSH/telnet, and live
prompt loops. This is a rescope of the denominator, not removal of source
assertions. The full 3.0.53 archive remains in the private Oracle bundle.
