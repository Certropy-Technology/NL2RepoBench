# Oracle And Control Evidence

The final Harbor 0.21.0 bundle used only the local private Oracle source
archive. It did not fetch reference source and no model agent was run.

- Final Oracle command exited `0`.
- `valid=true`, `collected=9`, `expected_total=9`, `passed=9`, `failed=0`,
  `reward=1.0`.
- Final job result:
  `.nl2repo/authoring-work/repairs/prompt-toolkit/.work/runs/oracle-final-release/2026-08-25__00-13-31/result.json`
- Final trusted grading:
  `.nl2repo/authoring-work/repairs/prompt-toolkit/.work/runs/oracle-final-release/2026-08-25__00-13-31/prompt-toolkit__onkY5g2/verifier/grading.json`
- The verifier network probe recorded `public_network_available=false`.

Negative controls used the same final separate no-network verifier:

- Empty/nop exited `0`; candidate installation failed as expected and the
  trusted grader emitted `valid=true`, `reward=0.0`, and
  `failure_reason=candidate-installation-failed`.
- Stub exited `0`; it collected nine leaves, failed all nine, and scored `0.0`.
- Forgery exited `0`; it collected nine leaves, failed all nine, and scored
  `0.0`. Candidate attempts to write reward or trusted verifier files did not
  affect trusted grading.

The lifecycle evidence artifact is
`sha256:52d123a02d779f7fbf3c8e3e8fc99dcab15d1088b6d1351b4adb252eeac8cc32`.
It records the pre-lifecycle release campaign; the grading paths above are the
post-lifecycle final bundle campaign with the same verifier/source/denominator.

The selected denominator is the documented headless slice, not the full
upstream terminal suite. No upstream source assertions were deleted; excluded
TTY and OS-specific behavior is explicit in `instruction.md` and `scope.md`.
