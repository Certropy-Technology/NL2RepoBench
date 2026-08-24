# Oracle And Remediation Evidence

The task-local public source is backed by an opaque private dependency bundle,
private custom JSON verifier bundle, and private exact-revision Oracle bundle.
The generic compiler materializes those bytes only inside the separate
no-network verifier/Oracle environments.

Oracle evidence from the remediation worker:

- `valid=true`
- `collected=20`, `expected=20`, `passed=20`
- `reward=1.0`
- nop control reward `0.0`
- generic compiled evidence: `.nl2repo/runs/oracle/pydantic-settings-custom-compiled-correct/2026-08-24__11-41-41/pydantic-settings__uhMgx82/verifier/grading.json`

Remediation included pinning `editables`, selecting CPython 3.12 wheels rather
than host CPython 3.14 artifacts, isolating dotenv fixtures, pinning the
runtime/build/test closure, and adding a private JSON subprocess controller.
No model run was started by the authoring loop; stub, forgery, timeout, review,
and pilot gates remain downstream work.
