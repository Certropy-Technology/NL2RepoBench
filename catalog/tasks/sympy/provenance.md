# Oracle And Remediation Evidence

The generic private-bundle Harbor verifier passed one Oracle run for the bounded
public slice:

- `valid=true`
- `collected=24`, `expected=24`, `passed=24`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/sympy-custom-compiled-20260824-v3/2026-08-24__05-47-36/sympy__BHZ9rjU/verifier/grading.json`

Remediation included replacing the placeholder solution with an exact-revision
materializer and JSON-safe facade, fixing Docker build contexts, adding
`mpmath` to the verifier lock, making hidden test files readable, and
rejecting unknown solve symbols. The 24-case denominator is intentionally a
public slice, not the full SymPy suite. Controls and publication remain
separate gates. No model run was started by the authoring loop.
