# httpcore revalidation blocker

The current queue source digest is `sha256:a538f2f287bf8dfd0796406f8b3aa38e7a9c5e6bc10dd48b7fa475d49c3f4b0a`, and source validation passed before revalidation. All three declared private artifacts matched their recorded size and SHA-256. The local Oracle bundle contains the exact `source.tar` for revision `10a658221deb38a4c5b16db55ab554b0bf731707`.

Validation exited `0`; both production compile commands exited `0` and produced byte-identical manifests with canonical digest `sha256:6cd7ebf8b4a0dab07cb4579bd6b5453238a7b701b1f6ab8cbe4218bd63ff6665`. The first Harbor Oracle command exited `0` but ended with `EnvironmentStartTimeoutError` and no trial. The one permitted infrastructure retry also exited `0`, reached a trial, verified the source archive, and then failed candidate installation with `Errno 11: Resource temporarily unavailable` during PEP 517 metadata preparation. The verifier collected `0/24`; no test leaf ran.

Commands used were `uv run nl2repo task validate-source catalog/sources/httpcore`, the locked `uv run nl2repo harbor compile ... --allow-private` command in the two compile summaries, and `uv run --frozen --project harbor-runner harbor run ... -a oracle --n-concurrent 1 --yes` for the initial and retry runs. No command authorized an external host.

This is classified as `infrastructure`, not model or verifier behavior. Controls were not run because they would not produce valid evidence after the installation-stage infrastructure failure. Existing `production-evidence.json` and lifecycle metadata were left unchanged; fresh receipts are not durable production evidence and do not replace the prior receipt set.

Next step: rerun the full Oracle and control matrix in a resource-available Harbor environment, using the same source digest and canonical manifest, with no additional source or instruction changes.
