# Candidate Boundary

The production verifier uses `custom-json-v1`. Its root-owned entrypoint does not import `tzlocal` and does not append candidate paths to the trusted interpreter. For each leaf it sends a bounded Python scenario to:

```text
python -I -B -m nl2repobench.verification.candidate_runner \
  --candidate-site /tmp/candidate-site script
```

Only that UID-10001 child imports the candidate package. Scenarios reduce `ZoneInfo`, warnings, exceptions, signatures, metadata, and cache transitions to JSON-safe values before returning them. The canonical runner limits address space, CPU, output size, file descriptors, and process count. The outer custom verifier applies an eight-second timeout to every child and a task-wide bounded wall-clock timeout.

The verifier image installs the exact build-backend lock at Docker build time. Candidate installation uses `pip --no-deps --no-build-isolation` into a candidate-owned site. Agent and verifier phases are no-network; trusted reports are written only by root-owned runtime code under `/logs/verifier`.
