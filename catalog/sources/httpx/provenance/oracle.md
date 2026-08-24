# Oracle And Remediation Evidence

The generic private-bundle compiled Oracle passed:

- `valid=true`
- `collected=24`, `expected=24`, `passed=24`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/httpx-custom-compiled-current/2026-08-24__12-47-27/httpx__wpuNkhd/verifier/grading.json`

The task uses an offline MockTransport contract for the public slice. The full
live/httpbin/socket suite is not the frozen denominator. Dependency closure,
custom verifier and Oracle artifacts are private refs in `task.toml`; no model
run was started by the authoring loop.

Control evidence:

- nop/empty: reward `0.0`, valid candidate-install failure classified as
  `model`, at `.nl2repo/runs/controls/httpx-custom-nop/2026-08-24__13-01-22/httpx__joKwiUv/verifier/grading.json`
- stub: reward `0.0`, `24/24` leaves failed, at
  `.nl2repo/runs/controls/httpx-custom-stub-v3/2026-08-24__13-05-10/httpx-stub__dB786qR/verifier/grading.json`
- forgery: reward `0.0`, `24/24` leaves failed, at
  `.nl2repo/runs/controls/httpx-custom-forgery-v3/2026-08-24__13-05-10/httpx-forgery__d3ugRRg/verifier/grading.json`
- offline: the Oracle verifier recorded both external probes as unavailable in
  its `network.json`.
