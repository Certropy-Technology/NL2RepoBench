# Fastjsonschema instruction-migration revalidation blocker

- Task: `fastjsonschema`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:dec3464a533c404b8e3a348ebb386c9c0c6a8c62cbc356a09aab833397fd40ff`
- Historical lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged; its receipts are not durable under the current checkout.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/fastjsonschema` passed and reported the expected source digest. The three declared private artifacts were present in the parent CAS with matching size and SHA-256. Harbor `0.21.0` and the locked Python toolchain were inspected. All six source-owned controls passed shell syntax inspection.

Two production compiles were run with the current source, `toolchain.lock.toml`, parent CAS, `--allow-private`, and no runtime network authorization. Both exited `0` and `diff -rq` reported byte identity. Each generated bundle contains 272 files, canonical manifest digest `sha256:0d34c32fca54b8ab6475b4e27829466fe5901451e8631709d43af915d475b0e1`, and raw manifest SHA-256 `sha256:ce0d01f7b5a30a69595662da341a94b4fb2ef934569be074be77bb5124546a1c`.

## NoNetwork blocker

The private Oracle archive is `sha256:21ac1473fd0093f61613e6d6f545beacc845c6fd779d692cc4d338a01bab7afd`. Its only member is `solve.sh`, hash `sha256:b2a42008384180c9aad05191ee2e0315841ae16418adc2609ddb81d6de6d5978`. The script performs a runtime `git fetch` from `github.com` for revision `b88fa37cd46bb81e8d9dce91a7e1bc4debedd3a2`, then creates the source archive and checks its digest.

This violates the revalidation NoNetwork contract. No Oracle, empty, stub, forgery, or offline Harbor run was started, and no run ID, grading, network, collection, result, or failure-set receipt is claimed. The existing historical receipts are not reused or replaced.

## Remediation

Register a replacement private Oracle bundle containing a local payload tied to the frozen revision and source archive digest, or otherwise provide a hash-bound source-local immutable payload. Recompile twice against the replacement and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline matrix. Persist all receipts under this evidence directory before updating production evidence or `catalog/tasks/fastjsonschema`. Do not authorize `github.com`, change the denominator, alter lifecycle state, or claim current controls from this blocked revalidation.
