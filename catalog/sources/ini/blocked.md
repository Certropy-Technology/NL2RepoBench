# ini blocked remediation record

Status: **blocked**. The exact source revision and ISC license are frozen, and a
runtime-only disposable probe passed npm ci offline, but that probe was not
retained as a private artifact. The development lock is v2, its closure fails
offline with lock synchronization/cache errors, and the repository has no
frozen node:test adapter, denominator, separate verifier, Oracle, or controls.

Source authority: `npm/ini`, revision `3c96c74fd42584bd655e17a4e63e2ef0a3b406ee`,
Git archive SHA-256 `a78f7cd279d5a73c235c24358625f72743bb51622a72905f9fc40d062735b7f4`,
ISC license SHA-256 `4ec3d4c66cd87f5c8d8ad911b10f99bf27cb00cdfcff82621956e379186b016b`.

The initial descriptor-validation probe is preserved at
`evidence/post-descriptor-validation.txt`; it exited 1 because the descriptor
was absent. Reopen only after freezing a compliant Node/npm v3 dependency
closure, generated package provenance, bounded parse/stringify tests, and all
separate-verifier Oracle/control evidence.
