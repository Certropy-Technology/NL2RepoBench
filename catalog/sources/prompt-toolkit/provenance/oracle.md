# Oracle And Control Evidence

The official Harbor 0.21.0 Oracle used the local private source bundle; it did
not fetch reference source and no model agent was run.

- Oracle command exited `0`.
- `valid=true`, `collected=9`, `expected_total=9`, `passed=9`, `failed=0`,
  `reward=1.0`.
- Oracle result:
  `.nl2repo/authoring-work/repairs/prompt-toolkit/.work/runs/oracle/2026-08-24__23-36-05/result.json`
- Trusted grading:
  `.nl2repo/authoring-work/repairs/prompt-toolkit/.work/runs/oracle/2026-08-24__23-36-05/prompt-toolkit__BXccETL/verifier/grading.json`
- The verifier network probe recorded `public_network_available=false`.

Negative controls used the same separate no-network verifier:

- Empty/nop exited `0`; candidate installation failed as expected and the
  trusted grader emitted `valid=true`, `reward=0.0`, and
  `failure_reason=candidate-installation-failed`.
- Stub exited `0`; it collected nine leaves, failed all nine, and scored `0.0`.
- Forgery exited `0`; it collected nine leaves, failed all nine, and scored
  `0.0`. Attempts to write candidate reward or trusted verifier files did not
  affect trusted grading.

Exact structured records and paths are bundled in private evidence artifact
`sha256:11f68c92a1f1e0803fa47a6a39fe320e75b1f877f27472afe62156bdef461577`.

The selected denominator is the documented headless slice, not the full
upstream terminal suite. No upstream source assertions were deleted; excluded
TTY and OS-specific behavior is explicit in `instruction.md` and `scope.md`.
