# Lodash revalidation checkpoint

The migrated source digest was validated as
`sha256:70108df3ac075439719dba192a339a39db3ca47e6c786a45c7e9bd2bb6a6fa03`.
All four private artifacts were found in the parent-local CAS and verified by
declared size and SHA-256. Two production compiles were byte-identical with
canonical manifest digest
`sha256:b77f838d63fa7ea7a9b364e342871bc0610b0e61598135d84d8442e3b022f563`.

Completed no-network Harbor receipts are summarized in the JSON files beside
this note:

- Oracle: valid, 63 collected, 62 passed, 1 failed, reward `62/63`;
- empty: valid `0/0`, candidate-installation-failed exception;
- stub: valid `1/63`, reward `1/63`;
- forgery: valid `1/63`, reward `1/63`, verifier-owned reward preserved.

The single Oracle failure is the package metadata leaf; its failed test ID is
retained in `oracle-failure-set.json`. Every completed verifier network receipt
reported `public_network_available=false`.

The supported `timeout` control was prepared but not run. This is intentionally
left pending after the parent checkpoint instruction; `production-evidence.json`
was not replaced and the existing lifecycle status must not be interpreted as a
fresh full-matrix receipt until timeout is independently rerun.
