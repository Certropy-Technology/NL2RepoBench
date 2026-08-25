# Execa production integration blocker

The Execa source catalog and all four private artifacts validate, and production
compilation succeeds without `--allow-incomplete`. The fresh Oracle, empty,
stub, and forgery verifiers also emitted valid grading and network receipts.

The Oracle Harbor process nevertheless remained active beyond the supervisor's
601-second orchestration bound after writing its verifier receipts. The process
returned exit code zero before the termination directive could be applied, but
the supervisor declared the campaign non-promotable and prohibited a retry.

The bounded run is retained under
`.nl2repo/runs/execa-production-20260825-v1/`. No compiled runtime is retained in
`catalog/tasks/execa`, and lifecycle status remains `blocked`.
