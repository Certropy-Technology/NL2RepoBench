# Oracle And Remediation Evidence

The generic private-bundle Harbor verifier passed one Oracle run for the bounded
public slice:

- Historical attempt: `valid=true`, `collected=24`, `expected=24`, `passed=24`.
- The current production contract is 25 leaves after adding an explicit
  Python-code rejection assertion; the current Oracle gate is recorded under
  `.nl2repo/runs/sympy/oracle-20260827/`.
- Current gate: `valid=true`, `collected=25`, `expected=25`, `passed=25`,
  `reward=1.0`.
- Current evidence: `.nl2repo/runs/sympy/oracle-20260827-v2/sympy-oracle-20260827-v2/sympy__VYDYBp6/verifier/grading.json`

Remediation included replacing the placeholder solution with an exact-revision
materializer and JSON-safe facade, fixing Docker build contexts, adding
`mpmath` to the verifier lock, making hidden test files readable, rejecting
unknown solve symbols, and adding AST validation before symbolic evaluation.
The denominator is intentionally a public slice, not the full SymPy suite.
Controls and publication remain separate gates. No model run was started by
the authoring loop. The current control receipts are under
`.nl2repo/runs/sympy/controls-20260827-v2/` and each has `valid=true`,
`reward=0.0`.
