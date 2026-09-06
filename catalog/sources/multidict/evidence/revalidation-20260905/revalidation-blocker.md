# multidict instruction revalidation blocker

- Task: `multidict` `1.0.0`
- Queue source digest: `sha256:2167c620c47e72973c164eaeb1ab3c2b06eca76eeecb9f5c2e48365fd0659770`
- Frozen source revision: `86351873dcc36edb11ba1a27035f2ce2e9ff8f4e`
- Frozen source archive: `sha256:bfdff853c97ee413df6bde23098fbef8d6232dec8c4a2a9c2dd6a26dbd93040d`
- Failure class: `artifact`

`validate-source` passed and the generated task contains a local source archive
matching the declared source digest. The generated Oracle script was inspected
offline and has no runtime source fetch or external-network command.

The three required private CAS objects (dependency lock, separate verifier
bundle, and Oracle bundle) were checked at the parent CAS location, but none was
present at its declared digest and size. Therefore no compile, Oracle, or
control receipt was created or reused. Existing lifecycle and
`production-evidence.json` remain unchanged.

Machine-readable details are in `artifact-check.json` and `oracle-payload.json`.

## Remediation

Restore or register the exact three declared private artifacts, then compile the
current source twice and run fresh NoNetwork Oracle, empty, stub, forgery, and
offline controls against the resulting manifest. Do not authorize GitHub,
registries, DNS, or other external services, and do not reuse historical
receipts.
