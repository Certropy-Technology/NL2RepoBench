# ghapi instruction-migration revalidation blocker

- Task: `ghapi`
- Revalidation date: `2026-09-05`
- Expected source digest: `sha256:cfbe67bf7dac8a1134293a75ccef6f1df920d8fd56c33cfaf279debe4ef2ee5e`
- Historical lifecycle: unchanged at `controls-passed`.
- Historical `production-evidence.json`: unchanged and not reused as current receipts.

## Completed checks

The expected source digest and all three declared private CAS artifacts were verified offline with matching size and SHA-256. Two fresh production compiles using the locked toolchain, parent CAS, `--allow-private`, and no runtime authorization exited successfully and were byte-identical. Each bundle contains 58 files, raw manifest SHA-256 `sha256:d65e30b04f482dd67cc3d7799a5dc04dfacbe348691ccda43c8eb668f4de104d`, and canonical manifest digest `sha256:3343a60eaf588ba17f0e1927d6292dd06228252f9602c6b7ce98b2b522ae3ad1`.

## NoNetwork blocker

The hash-valid private Oracle archive contains `solve.sh`, whose SHA-256 is recorded in `oracle-bundle-inspection.json`. The script performs runtime `git clone` and `git fetch` from `github.com` for the pinned revision before creating and checking the source archive. This violates the revalidation NoNetwork contract.

No Oracle, empty, stub, forgery, or offline Harbor run was started. No run ID, grading, network, collection, result, or failure-set receipt is claimed. The historical receipts remain unchanged and are not substituted for current evidence.

## Remediation

Replace the Oracle bundle with a local immutable payload tied to the pinned revision and source archive digest. Recompile twice against that replacement, then run the complete Harbor 0.21.0 Oracle, empty, stub, forgery, and offline matrix. Persist every current receipt under this evidence directory before updating production evidence or the generated projection. Do not authorize `github.com`, change the denominator, or claim current controls from this blocked revalidation.
