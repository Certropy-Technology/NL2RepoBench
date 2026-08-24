# Generic Compiled Oracle

Evidence: `.nl2repo/runs/oracle/pyperclip-custom-compiled-v5/2026-08-24__12-41-14/pyperclip__Fqr66Xa/verifier/grading.json`

Result: `valid=true`, `collected=10`, `effective_total=10`, `passed=10`, `skipped=0`, `pytest_exit_code=0`, `reward=1.0`. The candidate was the immutable upstream revision recorded in `task.toml`; no model run was started.

The empty-workspace control was also run with the same network and verifier image. Installation failed and the trusted grader emitted `reward=0.0`, `failure_class=model`, `reason=candidate-installation-failed`.

The generic compiler now resolves private dependency, verifier, and Oracle bundles
by digest. The public catalog contains no hidden fixture or wheelhouse bytes.

Control evidence:

- nop/empty: reward `0.0`, valid candidate-install failure classified as
  `model`, at `.nl2repo/runs/controls/pyperclip-custom-nop/2026-08-24__13-01-22/pyperclip__mJUAgPa/verifier/grading.json`
- stub: reward `0.0`, `10/10` leaves failed, at
  `.nl2repo/runs/controls/pyperclip-custom-stub-v3/2026-08-24__13-05-10/pyperclip-stub__XEoiAX3/verifier/grading.json`
- forgery: reward `0.0`, `10/10` leaves failed, at
  `.nl2repo/runs/controls/pyperclip-custom-forgery-v3/2026-08-24__13-05-10/pyperclip-forgery__ApZy33Z/verifier/grading.json`
- offline: the compiled verifier runs with no network and both external Oracle
  probes are false.
