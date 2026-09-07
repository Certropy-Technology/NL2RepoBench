# Revalidation blocker: prompt-toolkit

The instruction-migration source validation passed before this evidence was
written. The current source digest is
`sha256:892e5b4686bcf8560f379fb2345e435d1157f6ca9d4b06d8cda6e658f12ae98b`.
The frozen upstream revision is
`583b3412c792a5cc9f01adde603679f3824a88f3` and its declared archive digest is
`sha256:b9dda9618cc8482f22128b28e60b095bb7eb95926e1c17276da2d4eeccc8feb0`.

Classification: **artifact-or-verifier-blocked**. The declared 375-byte
dependency lock matched its SHA-256 exactly. The declared 30,720-byte verifier
bundle and 6,031,360-byte Oracle bundle were not found in the authorized local
CAS lookup. A bounded local recovery operation timed out after 1,200 seconds;
no unverified file, replacement bundle, compile result, Oracle receipt, or
control receipt was accepted.

The task remains under the existing no-network policy. Harbor 0.21.0 was
confirmed locally. Oracle and controls were intentionally skipped because the
exact private artifacts were not established. The parent remediation is to
recover exact hash-and-size matching artifacts or review an unregistered
replacement proposal, then perform two deterministic compiles and a fresh
Oracle/control matrix without runtime network access.

See `artifact-check.json` for the compact command and digest record.
