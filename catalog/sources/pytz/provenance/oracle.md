# Generic Compiled Oracle

The generic private-bundle compiled Oracle passed:

- `valid=true`
- `collected=15`, `passed=15`, `failed=0`
- `reward=1.0`
- evidence: `.nl2repo/runs/oracle/pytz-custom-compiled-current/2026-08-24__13-17-14/pytz__s5deNRu/verifier/grading.json`

Control evidence:

- empty: reward `0.0`, candidate installation failure classified as `model`,
  at `.nl2repo/runs/controls/pytz-custom-empty/2026-08-24__13-20-47/pytz-empty__qGrsXeg/verifier/grading.json`
- stub: reward `0.06666666666666667` (`1/15`), at
  `.nl2repo/runs/controls/pytz-custom-stub-v2/2026-08-24__13-18-48/pytz-stub__8sEixJA/verifier/grading.json`
- forgery: reward `0.0` (`0/15`), at
  `.nl2repo/runs/controls/pytz-custom-forgery-v2/2026-08-24__13-18-48/pytz-forgery__Shnhn8n/verifier/grading.json`
- offline: the verifier uses the no-network profile; network probes are
  recorded by the compiled test harness.

The historical upstream 235-node suite is not the frozen denominator. The
current contract is the documented deterministic 15-case API slice.
