# python-fire Remediation Evidence

The exact Apache-2.0 source revision is
`716bbc23d7eca949fdb682172283c8d18f742cb6`; its unprefixed source archive is
`sha256:a0254d68a6e3b4aef32ce2f9fd1b10f45755149a1194b683897809d80b670494`.

The broad upstream suite includes live Python objects, IPython behavior and
unseeded Hypothesis fuzzing, so it was not used as a direct trusted-process
denominator. The remediation freezes a 20-leaf noninteractive JSON/CLI slice
and pins setuptools, termcolor and wheel in private artifacts referenced from
`task.toml`. The source, adapter and hidden expected bytes stay outside the
public catalog.

The task is now `oracle-passed`; timeout, review and pilot remain open. No model
run was started.

## Generic compiled evidence

- The first compiled Oracle failed before grading because the separate verifier
  runtime omitted the newly required `domain/network_policy.py`; this was a
  verifier runtime failure, not a candidate result. The compiler runtime copy
  list was corrected and the task was recompiled.
- Oracle: `valid=true`, `20/20`, reward `1.0`, at
  `.nl2repo/runs/oracle/python-fire-custom-compiled-v3/2026-08-24__16-00-59/python-fire__cN5QAHP/verifier/grading.json`.
- Empty: reward `0.0`, candidate-install failure classified as `model`, at
  `.nl2repo/runs/controls/python-fire-custom-empty-v1/2026-08-24__16-04-31/python-fire-empty__HhxyYS7/verifier/grading.json`.
- Stub: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/python-fire-custom-stub-v1/2026-08-24__16-02-27/python-fire-stub__DhzA39J/verifier/grading.json`.
- Forgery: reward `0.0`, `20/20` leaves failed, at
  `.nl2repo/runs/controls/python-fire-custom-forgery-v1/2026-08-24__16-02-27/python-fire-forgery__znWCtqj/verifier/grading.json`.
- Offline: the compiled verifier uses the no-network profile.
