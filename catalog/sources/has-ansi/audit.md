# has-ansi Audit

Status: **controls-passed** pending integrator review, model Agent Run, and publication.

The candidate is a small ESM string utility with a clear MIT license, a frozen
full revision, and an executable upstream test baseline. The dependency probe
resolved the only runtime dependency to `ansi-regex@6.3.0`; its v3 npm lock and
integrity-checked cache are stored as a private artifact. The public task
contract intentionally describes observable ANSI detection rather than copying
the upstream implementation or AVA tests.

The private 24-leaf `node:test` slice covers package/export metadata, the
TypeScript declaration, ordinary and empty text, SGR/CSI/OSC/C1 examples,
embedded and multiline sequences, literal and partial escapes, and invalid
input handling at the child boundary. The separate verifier uses the locked
Node runtime and no network. Oracle, empty, stub, forgery, timeout, install,
loader, and offline controls are recorded in task-local evidence before
handoff. Oracle, empty, stub, forgery, timeout, install, loader, and offline
controls completed against the final compiled bundle; receipts are recorded in
task-local evidence before handoff.
