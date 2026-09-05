# fast-deep-equal instruction-migration revalidation blocker

- Task: `fast-deep-equal`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:576651d8a30903cb40a03d2f042e8c683dcab55087123dfb49fc5e29c1b72031`
- Existing lifecycle: `controls-passed` (unchanged)
- Existing `production-evidence.json`: unchanged

## Offline artifact check

The task source declares these private artifacts, and the parent CAS precheck
found all three absent by their digest-addressed paths:

- npm dependency bundle, 10,240 bytes: `sha256:949eaa861a331f8273258a69eed71002b5b484228045d85cfe7ea4558f9ccf9f`
- private test bundle, 10,240 bytes: `sha256:71a7b368d85c8aea4bf5ec64900e317cb4b815793ed31d7a60e866aeb618d97f`
- scripts-stripped Oracle bundle, 10,240 bytes: `sha256:0a878d3dc5bac73a18378cada7fcf709f586053183b0209afa73efd4e69d0a12`

The check used local filesystem existence and did not contact GitHub,
codeload, npm, DNS, or any external service. No host authorization was
granted.

## Revalidation decision

Revalidation is blocked before compilation because the required private
artifact closure is unavailable. No compiler command, Harbor command, Oracle,
or control run was executed in this attempt. Existing Oracle and control
receipts are not reused or replaced because the instruction migration requires
a current bundle manifest and fresh NoNetwork receipts.

## Remediation

Restore or register all three exact private CAS objects, verify their size and
SHA-256 values, then compile the current source twice with the locked Node/npm
toolchain and `--allow-private`. Require byte-identical projections before
running the Harbor 0.21.0 Oracle, empty, stub, forgery, and offline matrix with
no runtime network access. Persist compact repository-relative receipts under
this evidence directory and bind every receipt to the resulting manifest
digest before changing production evidence or lifecycle.
