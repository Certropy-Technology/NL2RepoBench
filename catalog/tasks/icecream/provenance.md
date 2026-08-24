# Icecream Remediation Evidence

The exact MIT source revision is `816e6c6bbac50f16fda8f801c658fe5ebcfd50bc`.
Its unprefixed source archive is recorded as
`sha256:cf563c74849444da66c3e3914346d1f89086da3565980876f037f542daf5367c`.

The original 40-case legacy contract was not used as the production denominator
because it mixes terminal/process behavior with platform-dependent output. The
remediation freezes a deterministic 20-case mocked-output slice and stores the
candidate dependency, verifier and Oracle bytes behind private artifact refs in
`task.toml`. Large source and wheel artifacts remain under the task-local
`.work` directory, not the public catalog.

The task is now `oracle-passed`; timeout, review and pilot remain open. No model
run was started.

## Generic compiled evidence

- Oracle: `valid=true`, `20/20`, reward `1.0`, at
  `.nl2repo/runs/oracle/icecream-custom-compiled-current/2026-08-24__14-28-29/icecream__iCtwqFW/verifier/grading.json`.
- Empty: reward `0.0`, candidate-install failure classified as `model`, at
  `.nl2repo/runs/controls/icecream-custom-empty-v1/2026-08-24__14-32-08/icecream-empty__8dwLnde/verifier/grading.json`.
- Stub: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/icecream-custom-stub-v1/2026-08-24__14-30-10/icecream-stub__FRcLdxc/verifier/grading.json`.
- Forgery: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/icecream-custom-forgery-v1/2026-08-24__14-30-10/icecream-forgery__JY24Xne/verifier/grading.json`.
- Offline: the compiled verifier uses the no-network profile.
