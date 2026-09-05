# Revalidation Summary

- Task: `get-east-asian-width`
- Instruction-migration source digest: `sha256:82d2a5bc56c93d9f1c9e873b969bf2919779eaa2ed449422a8732f2467f9175d`
- Source archive digest: `sha256:b412e8d6253a64848848d2b2e9a1e397b7668505d78c43a1c6583a29ec413593`
- Runtime: Node 24.19.0, npm 11.17.0, Harbor 0.21.0
- Two production compiles completed with `--allow-private` and no `--allow-incomplete`; both contain 79 files and have identical manifest bytes (`sha256:d4513b9f135e2521e5f644c238bb71d1430482991f1adcde7e347f94f818a98f`). The fresh canonical manifest digest is `sha256:7ed4d52f4c7775694ebdc020f20b23aa3a2fcdd59946927634a37ce7f7cc498c`.
- Oracle completed with 26/26 leaves and reward `1.0`. Stub and forgery scored `5/26`; offline scored `4/26`; loader-hook scored `5/26`; hang scored `2/26`. Empty and install-script intentionally stopped at candidate installation with `0/0` and reward `0.0`.
- All verifier network receipts report `public_network_available: false`.
- The historical `production-evidence.json` was not replaced because its existing receipt paths are ignored authoring paths. Parent integration must relocate the fresh receipts or preserve these hash-bound summaries as pending evidence before updating the canonical record.
