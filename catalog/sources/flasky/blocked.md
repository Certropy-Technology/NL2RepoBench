# Flasky Production Integration Blocker

Status: `blocked` (`environment`).

The immutable legacy image and source archive were audited. The image digest
remains
`sha256:dd7c1ab35038eb22f5637d7fb8d210d2a6bf080d65ca72c89b4ac31af3e0c342`,
and the exact upstream archive remains 194,560 bytes with SHA-256
`d70278ce85aadc6127ef9f997c0410076488b744c01631a45499dc03bcd698d6`.
The image contains 35 test methods; the legacy effective denominator is 34
because the Selenium test is skipped without Chrome.

The production remediation attempted to replace the legacy Python 3.9 image
contract with a Python 3.12 package-index dependency lock. Per orchestration
steering, the image-install process was treated as a bounded dependency-lock
timeout at 587 seconds and the task was stopped without retry. The candidate
lock in the task-local run workspace is audit output only: it was not ingested
as a private artifact or referenced by the catalog.

No production compile without `--allow-incomplete` completed. No Harbor
Oracle was run, so there is no valid collection or reward. Empty, stub,
forgery, and offline controls were correctly not started. The tracked generated
runtime under `catalog/tasks/flasky/` was removed because it represented the
obsolete in-image verifier and unverified network-fetch Oracle contracts. The
pre-existing untracked `environment/docker-compose.yaml` is retained
byte-for-byte with SHA-256
`17ceef0a82e7dfb63d9f5ce974350f392dd8a323eac174ec69d28a90c7de8388`.

## Reopen Requirement

Regenerate the Python 3.12 requirements lock under an explicitly approved
build timeout, verify its hash-only package-index installation in the pinned
base image, author private subprocess-verifier and local Oracle bundles, and
then compile without `--allow-incomplete`. Only after one Oracle reports
`valid=true`, frozen effective collection 34, and reward at least 0.8 may the
control matrix run.

The exact termination record is in
`evidence/dependency-lock-timeout.txt`.
