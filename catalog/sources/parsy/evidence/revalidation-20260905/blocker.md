# Parsy instruction-migration revalidation blocker

- Task: `parsy`
- Queue source digest: `sha256:c2e353526f6cba99e086b0cfb8f4707063f261f9e722973ca6fafd22e565f32e`
- Frozen upstream revision: `03deafa98a17adc27b1f650241701b2d21902b3e`
- Network policy: `no-network`; no source or package host was authorized.

## Classification

Status: **blocked — artifact**.

The exact source archive is recoverable from the generated local projection and
was verified as 194560 bytes with SHA-256
`5b3f5d7aa6d5ee31659ce341bc15dee031ca631cc69e1d3ac392b4b03df6f10f`, matching
the source descriptor. The dependency lock is also present in authorized local
CAS and matches its declared 707-byte digest.

The declared verifier bundle (61440 bytes,
`d9adcae4345746eb166cc0e367d22580f6587a1f42b471205d6f5f27113a897c`) and
Oracle bundle (204800 bytes,
`9daf44390c7aa813a4461b056d0f98f066bc5fe1fcf7eb7aaeda4850b09a53bc`) were not
found in the authorized local CAS, generated projection, historical handoff, or
archive search scope. A production compile consequently failed closed before
bundle generation because the verifier artifact was missing. No Harbor Oracle
or control result is claimed.

## Evidence and remediation

- `artifact-probe.json` records each expected size/digest and the local search result.
- `compile-attempt.log` records the sanitized compile failure.
- `source-freeze.json` records the immutable revision, archive hash, queue digest,
  and source validation command.
- `source-validate.log` and `source-archive-hash.log` contain command outputs with
  repository-relative or placeholder paths only.

Parent remediation: recover the exact verifier and Oracle bundle bytes from a
trusted local source, independently verify both size and SHA-256, register them
in parent-owned CAS, compile twice with the locked toolchain, inspect the final
manifest, and then run a fresh Harbor 0.21.0 Oracle plus every supported control.
Do not reuse the pre-migration production receipts.
