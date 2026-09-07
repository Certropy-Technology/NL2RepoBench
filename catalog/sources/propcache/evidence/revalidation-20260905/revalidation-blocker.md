# Revalidation blocker: propcache instruction migration

- Classification: `artifact-or-verifier-blocked`.
- Queue source digest and `validate-source` digest both equal `sha256:6b3cf23fb40470b80220a11eafb4af20a30c1574168a33b693dc4ab6e708e0a9`.
- Harbor 0.21.0 revalidation was not run. The existing generated task and historical receipts are stale because the public instruction changed.
- Declared candidate lock and verifier bundle were independently checked in local CAS with exact sizes and SHA-256. The declared Oracle bundle was also checked and is present.
- The exact frozen source archive required by `harbor/solution/solve.sh` (307200 bytes, SHA-256 `8f4d7e6e6a388c7d45e4830dcbfe286d3b43df40b97df0b7611f37f987ec79f2`) was not available in the current worktree, generated projections, private CAS, bounded handoff/work directories, or accessible archive payloads. Historical archive receipts prove metadata only and contain no source bytes usable for this run.
- The Oracle script performs a runtime GitHub fetch (`git clone`/`git fetch`), which is forbidden under this revalidation's NoNetwork policy. No host authorization was used.
- Existing `catalog/tasks/propcache` and `production-evidence.json` were preserved unchanged.

## Remediation

Provide the exact frozen source archive as a private CAS object, verify its size and SHA-256 against the source declaration, and replace the fetch-based Oracle path with a local/private artifact input before rerunning two locked compiles and the complete Oracle/control matrix. Do not promote this blocker to a terminal lifecycle change solely from this evidence.
