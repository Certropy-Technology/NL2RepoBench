# Marshmallow Remediation Evidence

The exact MIT source revision is `c7b559a1fa3aba57ca6dba0ab336841c5038a782`.
The source archive digest is
`sha256:c531024b6b6cf15be06fd2205f9304265524a3b1958e3e6c09793bc9b9f35728`.

The legacy in-process suite is not used as a trusted denominator because
schemas, fields, validators and registry state are process-local Python
objects. The current instruction freezes a 33-leaf JSON scenario adapter that
constructs those objects inside the candidate child process. Private
dependency, verifier and Oracle bytes are content-addressed refs in
`task.toml` and are not in the public catalog.

## Generic compiled evidence

- Oracle: `valid=true`, `33/33`, reward `1.0`, at
  `.nl2repo/runs/oracle/marshmallow-custom-compiled-current/2026-08-24__15-27-22/marshmallow__ncQMMiW/verifier/grading.json`.
- Empty: reward `0.0`, candidate-install failure classified as `model`, at
  `.nl2repo/runs/controls/marshmallow-custom-empty-v1/2026-08-24__15-32-52/marshmallow-empty__54vcSCt/verifier/grading.json`.
- Stub: reward `0.0`, `33/33` leaves failed, at
  `.nl2repo/runs/controls/marshmallow-custom-stub-v2/2026-08-24__15-31-03/marshmallow-stub__cC29qsW/verifier/grading.json`.
- Forgery: reward `0.0`, `33/33` leaves failed, at
  `.nl2repo/runs/controls/marshmallow-custom-forgery-v2/2026-08-24__15-31-03/marshmallow-forgery__wQtvW7Z/verifier/grading.json`.
- Offline: the compiled verifier uses the no-network profile.

The task remains a rescoped contract and must not be compared with the
historical 1,188-node upstream baseline.
