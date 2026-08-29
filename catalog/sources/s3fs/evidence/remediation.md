# Authoring remediation

The upstream test suite was collected from the frozen commit and contains
service-backed tests using moto/flask and credential or endpoint fixtures. A
direct trusted import would violate the separate-verifier boundary and the
future Agent run is explicitly no-network. The task therefore uses a bounded
fake-client adaptation. The fake client is injected only through the documented
async S3 call boundary and exercises deterministic filesystem behavior without
credentials or remote state.

The first local dependency install attempt used a disk-backed Python 3.12 venv
and failed while expanding botocore's service model with `ENOSPC`; the failed
venv was removed. A bounded `/tmp` reference environment then installed the
complete 27-package hash-locked closure successfully. The source clone was
recreated with blob filtering after the failed disk-pressure probe.
