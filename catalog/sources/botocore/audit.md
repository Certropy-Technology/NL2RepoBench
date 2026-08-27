# Botocore Authoring Audit

The candidate is frozen at commit `577f39f278bec5635ffdc7efd6d99f17687419e2`.
An independent shallow fetch resolved that exact commit. Two archive probes
produced the same `git archive --format=tar` digest:
`sha256:13720b9e9a36c235c45535e1364ec7e5faddd47789b87cd27865b1ec9eafa9a3`.
The repository declares Apache-2.0 in `LICENSE.txt` and records vendored
requests/urllib3 notices in `NOTICE`.

Inventory evidence is in the task-local `.nl2repo/authoring-work/.../provenance`
directory. The frozen tree contains 213 Python test files; the complete
upstream suite includes service, account, CRT, metadata, and integration paths
that cannot be deterministic in a no-network Harbor task. The published
verifier therefore uses a documented 24-case offline contract covering session,
credentials, config, S3 model/paginator/waiter loading, request preparation,
SigV4 headers, client metadata, retry configuration, and Stubber behavior.

The task-local dependency lock is hash-verified and is installed only during
Docker image builds. The run-time agent and separate verifier are both
`no-network`; verifier network probes failed for `pypi.org:443` and
`1.1.1.1:443`. The Oracle alone receives source-host authorization and checks
the archive digest before extraction.

Evidence summary:

| Gate | Result |
| --- | --- |
| source validation | exit 0 |
| network lint | exit 0, 0 errors, expected Oracle-host warning |
| production compile | exit 0 |
| Oracle | valid, 24/24, reward 1.0 |
| empty | valid, reward 0.0, model installation failure |
| stub | valid, 0/24 |
| forgery | valid, 0/24; verifier-owned reward unchanged |
| offline | public network unavailable |

No Harbor Agent Run was started from this lane. The machine-readable evidence
record is `production-evidence.json`; the lane handoff is written under
`.nl2repo/authoring-handoff.json`.
