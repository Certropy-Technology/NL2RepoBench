# Generic Compiled Oracle

The generic private-bundle compiled Oracle passed:

- `valid=true`
- `collected=20`, `passed=20`, `failed=0`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/docstring-parser-custom-compiled-current/2026-08-24__14-15-41/docstring-parser__6rRTZ8Q/verifier/grading.json`

Control evidence:

- empty: reward `0.0`, candidate installation failure classified as `model`,
  at `.nl2repo/runs/controls/docstring-parser-custom-empty-v1/2026-08-24__14-18-29/docstring-parser-empty__tH96TMY/verifier/grading.json`
- stub: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/docstring-parser-custom-stub-v1/2026-08-24__14-16-56/docstring-parser-stub__V62T6gq/verifier/grading.json`
- forgery: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/docstring-parser-custom-forgery-v1/2026-08-24__14-16-56/docstring-parser-forgery__cYkU6XF/verifier/grading.json`
- offline: the compiled verifier uses the no-network profile; network probes
  are part of the structured verifier evidence.

The denominator is the bounded JSON-safe parse/composition slice documented in
`instruction.md`, not the complete upstream test suite.
